import time, os, pygame, platforms, projectiles, Queue
from load_animation_frames import load_animation_frames, load_animation_frames_key_tween
from constants import MIN_SPEED, MAX_SPEED, MAX_FRAME_RATE, ACCELERATION_PERIOD, SPEED_DIFF, SLOW_TO_STOP
from constants import JUMPSPEED, JUMPCOUNT, JUMP_PERIOD, ACCELERATION
from constants import IDLE_PERIOD, RUN_PERIOD, GLIDE_PERIOD, GRENADE_ATTACK_PERIOD, SLIDE_PERIOD, FIREBALL_ATTACK_PERIOD
from constants import GLIDE_ACCELERATION, DRIFT_AIR_DECEL, DRIFT_GROUND_DECEL, SCREEN_WIDTH
from constants import SCREEN_HEIGHT, DIRDICT
from constants import RUN_FILE_STEM, JUMP_FILE_STEM, FIREBALL_ATTACK_FILE_STEM, GLIDE_FILE_STEM, IDLE_FILE_STEM, SLIDE_FILE_STEM
from constants import MAX_FRAME_RATE
from state_machine import SimpleStateMachine, ConcurrentStateMachine, PlayerState, DriveHorizontalState
from state_machine import JumpState, IdleHorizontalState, OnPlatformState, DriftHorizontalState, FallState, GlideState, SlideHorizontalState
from state_machine import IdleAttackState, FireballAttackState


class Player(pygame.sprite.Sprite):

    def __init__(self):
        super(Player, self).__init__()
        self.level = None
        self.direction = 'R'
        self.x_velocity = 0
        self.y_velocity = 0
        self.drift_decel = DRIFT_AIR_DECEL
        self.current_platform = None
        self.vertical_event_queue = Queue.Queue()
        self.horizontal_event_queue = Queue.Queue()
        self.attack_event_queue = Queue.Queue()
        self._load_animation_frames()
        self._create_concurrent_state_machine()
        self.image = self.csm.current_frame
        self.rect = self.image.get_rect()
        self.current_event = None

        key_down_method_dct = {pygame.K_LEFT: self.go_left, pygame.K_RIGHT: self.go_right,
                               pygame.K_UP: self.jump, pygame.K_LALT: self.glide, pygame.K_DOWN: self.slide,
                               pygame.K_SPACE: self.fireball_attack}

        key_up_method_dct = {pygame.K_LEFT: self.stop_horizontal, pygame.K_RIGHT: self.stop_horizontal,
                             pygame.K_UP: self.stop_vertical, pygame.K_LALT: self.stop_glide, pygame.K_DOWN: self.stop_slide,
                             pygame.K_SPACE: self.stop_fireball_attack}

        self.key_method_dct = {pygame.KEYDOWN: key_down_method_dct, pygame.KEYUP: key_up_method_dct}

    def _load_animation_frames(self):
        keyframe_range, tween_range = range(10), range(1, 6)
        self.run_frames = load_animation_frames_key_tween(RUN_FILE_STEM, keyframe_range, tween_range)
        self.jump_frames = load_animation_frames_key_tween(JUMP_FILE_STEM, keyframe_range, tween_range)
        self.fireball_attack_frames = load_animation_frames_key_tween(FIREBALL_ATTACK_FILE_STEM, keyframe_range, tween_range)
        self.glide_frames = load_animation_frames_key_tween(GLIDE_FILE_STEM, keyframe_range, tween_range)
        image_indices = range(10)
        self.idle_frames = load_animation_frames(IDLE_FILE_STEM, image_indices)
        self.slide_frames = load_animation_frames(SLIDE_FILE_STEM, image_indices)

    def _create_horizontal_state_machine(self):
        idle_horizontal_state = IdleHorizontalState(self)
        drive_horizontal_state = DriveHorizontalState(self)
        drift_horizontal_state = DriftHorizontalState(self)
        slide_horizontal_state = SlideHorizontalState(self)

        initial_state = idle_horizontal_state

        idle_transitions = [(drive_horizontal_state, 'drive_horizontal'), (slide_horizontal_state, 'slide_horizontal')]
        drive_transitions = [(drift_horizontal_state, 'drift_horizontal'), (slide_horizontal_state, 'slide_horizontal')]
        drift_transitions = [(drive_horizontal_state, 'drive_horizontal'), (idle_horizontal_state, 'idle_horizontal'),
                             (slide_horizontal_state, 'slide_horizontal')]
        slide_transitions = [(idle_horizontal_state, 'idle_horizontal')]

        state_transition_dct = {idle_horizontal_state: idle_transitions, drive_horizontal_state: drive_transitions,
                                drift_horizontal_state: drift_transitions, slide_horizontal_state: slide_transitions}

        self.horizontal_states = [idle_horizontal_state, drive_horizontal_state, drift_horizontal_state, slide_horizontal_state]
        self.horizontal_state_machine = SimpleStateMachine(state_transition_dct, initial_state, self.horizontal_event_queue)

    def _create_vertical_state_machine(self):
        on_platform_state = OnPlatformState(self)
        jump_state = JumpState(self)
        fall_state = FallState(self)
        glide_state = GlideState(self)

        initial_state = fall_state
        on_platform_transitions = [(jump_state, 'jump'), (fall_state, 'midair')]
        jump_transitions = [(on_platform_state, 'landing'), (jump_state, 'jump'), (glide_state, 'glide')]
        fall_transitions = [(on_platform_state, 'landing'), (jump_state, 'jump'), (glide_state, 'glide')]
        glide_transitions = [(on_platform_state, 'landing'), (fall_state, 'stop_glide')]

        state_transition_dct = {on_platform_state: on_platform_transitions, jump_state: jump_transitions,
                                fall_state: fall_transitions, glide_state: glide_transitions}

        self.vertical_states = [on_platform_state, jump_state, fall_state, glide_state]
        self.vertical_state_machine = SimpleStateMachine(state_transition_dct, initial_state, self.vertical_event_queue)

    def _create_attack_state_machine(self):
        idle_attack_state = IdleAttackState(self)
        fireball_attack_state = FireballAttackState(self)

        initial_state = idle_attack_state
        idle_attack_transitions = [(fireball_attack_state, 'fireball_attack')]
        fireball_attack_transitions = [(idle_attack_state, 'idle_attack')]

        state_transition_dct = {idle_attack_state: idle_attack_transitions,
                                fireball_attack_state: fireball_attack_transitions}

        self.attack_states = [idle_attack_state, fireball_attack_state]
        self.attack_state_machine = SimpleStateMachine(state_transition_dct,
                                                       initial_state, self.attack_event_queue)

    """
    def _create_concurrent_state_machine(self):
        self._create_horizontal_state_machine()
        self._create_vertical_state_machine()
        self._create_attack_state_machine()

        state_machine_list = [self.horizontal_state_machine, self.vertical_state_machine]
        idle_horizontal_state, drive_horizontal_state, drift_horizontal_state, slide_horizontal_state = self.horizontal_states
        on_platform_state, jump_state, fall_state, glide_state = self.vertical_states

        state_to_animation_dict = dict()

        for hstate in self.horizontal_states:
            state_to_animation_dict[(hstate, jump_state)] = (self.jump_frames, JUMP_PERIOD)
            state_to_animation_dict[(hstate,  glide_state)] = (self.glide_frames, GLIDE_PERIOD)

        state_to_animation_dict[(idle_horizontal_state, on_platform_state)] = (self.idle_frames, IDLE_PERIOD)
        state_to_animation_dict[(drive_horizontal_state, on_platform_state)] = (self.run_frames, RUN_PERIOD)
        state_to_animation_dict[(drift_horizontal_state, on_platform_state)] = (self.run_frames, RUN_PERIOD)
        state_to_animation_dict[(slide_horizontal_state, on_platform_state)] = (self.slide_frames, SLIDE_PERIOD)

        state_to_animation_dict[(idle_horizontal_state,  fall_state)] = (self.idle_frames, IDLE_PERIOD)
        state_to_animation_dict[(drive_horizontal_state, fall_state)] = (self.run_frames, RUN_PERIOD)
        state_to_animation_dict[(drift_horizontal_state, fall_state)] = (self.run_frames, RUN_PERIOD)
        state_to_animation_dict[(slide_horizontal_state, fall_state)] = (self.run_frames, RUN_PERIOD)

        state_machine_list = [self.horizontal_state_machine, self.vertical_state_machine]
        self.csm = ConcurrentStateMachine(state_machine_list, state_to_animation_dict)
    """

    def _create_concurrent_state_machine(self):
        self._create_horizontal_state_machine()
        self._create_vertical_state_machine()
        self._create_attack_state_machine()

        state_machine_list = [self.horizontal_state_machine, self.vertical_state_machine, self.vertical_state_machine]
        idle_horizontal_state, drive_horizontal_state, drift_horizontal_state, slide_horizontal_state = self.horizontal_states
        on_platform_state, jump_state, fall_state, glide_state = self.vertical_states
        idle_attack_state, fireball_attack_state = self.attack_states

        state_to_animation_dict = dict()

        for hstate in self.horizontal_states:
            state_to_animation_dict[(hstate, jump_state, idle_attack_state)] = (self.jump_frames, JUMP_PERIOD)
            state_to_animation_dict[(hstate, glide_state, idle_attack_state)] = (self.glide_frames, GLIDE_PERIOD)
            state_to_animation_dict[(hstate, jump_state, fireball_attack_state)] = (self.fireball_attack_frames, FIREBALL_ATTACK_PERIOD)
            state_to_animation_dict[(hstate, glide_state, fireball_attack_state)] = (self.fireball_attack_frames, FIREBALL_ATTACK_PERIOD)

        state_to_animation_dict[(idle_horizontal_state, on_platform_state, idle_attack_state)] = (self.idle_frames, IDLE_PERIOD)
        state_to_animation_dict[(drive_horizontal_state, on_platform_state, idle_attack_state)] = (self.run_frames, RUN_PERIOD)
        state_to_animation_dict[(drift_horizontal_state, on_platform_state, idle_attack_state)] = (self.run_frames, RUN_PERIOD)
        state_to_animation_dict[(slide_horizontal_state, on_platform_state, idle_attack_state)] = (self.slide_frames, SLIDE_PERIOD)

        state_to_animation_dict[(idle_horizontal_state, on_platform_state,  fireball_attack_state)] = (self.fireball_attack_frames, FIREBALL_ATTACK_PERIOD)
        state_to_animation_dict[(drive_horizontal_state, on_platform_state, fireball_attack_state)] = (self.fireball_attack_frames, FIREBALL_ATTACK_PERIOD)
        state_to_animation_dict[(drift_horizontal_state, on_platform_state, fireball_attack_state)] = (self.fireball_attack_frames, FIREBALL_ATTACK_PERIOD)
        state_to_animation_dict[(slide_horizontal_state, on_platform_state, fireball_attack_state)] = (self.fireball_attack_frames, FIREBALL_ATTACK_PERIOD)

        state_to_animation_dict[(idle_horizontal_state, fall_state, idle_attack_state)] = (self.idle_frames, IDLE_PERIOD)
        state_to_animation_dict[(drive_horizontal_state, fall_state, idle_attack_state)] = (self.run_frames, RUN_PERIOD)
        state_to_animation_dict[(drift_horizontal_state, fall_state, idle_attack_state)] = (self.run_frames, RUN_PERIOD)
        state_to_animation_dict[(slide_horizontal_state, fall_state, idle_attack_state)] = (self.run_frames, RUN_PERIOD)

        state_to_animation_dict[(idle_horizontal_state, fall_state, fireball_attack_state)] = (self.fireball_attack_frames, FIREBALL_ATTACK_PERIOD)
        state_to_animation_dict[(drive_horizontal_state, fall_state, fireball_attack_state)] = (self.fireball_attack_frames, FIREBALL_ATTACK_PERIOD)
        state_to_animation_dict[(drift_horizontal_state, fall_state, fireball_attack_state)] = (self.fireball_attack_frames, FIREBALL_ATTACK_PERIOD)
        state_to_animation_dict[(slide_horizontal_state, fall_state, fireball_attack_state)] = (self.fireball_attack_frames, FIREBALL_ATTACK_PERIOD)

        state_machine_list = [self.horizontal_state_machine,
                              self.vertical_state_machine,
                              self.attack_state_machine]

        self.csm = ConcurrentStateMachine(state_machine_list, state_to_animation_dict)

    def bullet_attack(self):
        self._create_fireball()
        self.attack_timer = 0
        self.is_firing_fireball = True
        self.frame = 0

    def grenade_attack(self):
        self._create_grenade()
        self.is_firing_grenade = True

    def _create_slidedust(self):
        velocity = (0, 0)
        _type = 'skiddust'
        projectile = projectiles.Projectile(self, velocity, _type)
        self.level.projectile_list.add(projectile)

    def _create_fireball(self):
        velocity = (15, 0)
        _type = 'fireball'
        projectile = projectiles.Projectile(self, velocity, _type)
        self.level.projectile_list.add(projectile)

    def _create_grenade(self):
        velocity = (10, 20)
        _type = 'grenade'
        projectile = projectiles.Projectile(self, velocity, _type)
        self.level.projectile_list.add(projectile)

    def handle_input(self, event):
        if event.type in self.key_method_dct.keys() and event.key in self.key_method_dct[event.type].keys():
            self.key_method_dct[event.type][event.key]()
        else:
            pass

    def update(self):
        self.csm.update()
        self.image = self.csm.current_frame

    def jump(self):
        self.vertical_event_queue.put('jump')

    def glide(self):
        print 'GLIDE'
        self.vertical_event_queue.put('glide')

    def slide(self):
        print 'SLIDE'
        self._create_slidedust()
        self.horizontal_event_queue.put('slide_horizontal')

    def fireball_attack(self):
        print 'FIREBALL'
        self._create_fireball()
        self.attack_event_queue.put('fireball_attack')

    def go_left(self):
        print 'GO LEFT'
        self.direction = 'L'
        self.horizontal_event_queue.put('drive_horizontal')

    def go_right(self):
        print 'GO RIGHT'
        self.direction = 'R'
        self.horizontal_event_queue.put('drive_horizontal')

    def stop_horizontal(self):
        print 'HORIZONTAL KEY UP'
        self.horizontal_event_queue.put('drift_horizontal')

    def stop_vertical(self):
        pass

    def stop_glide(self):
        print 'GLIDE KEY UP'
        self.vertical_event_queue.put('stop_glide')

    def stop_slide(self):
        pass

    def stop_fireball_attack(self):
        pass
