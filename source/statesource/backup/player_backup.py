import os, pygame, platforms, projectiles, Queue
from load_animation_frames import load_animation_frames, load_animation_frames_key_tween
from constants import MIN_SPEED, MAX_SPEED, MAX_FRAME_RATE, ACCELERATION_PERIOD, SPEED_DIFF, SLOW_TO_STOP
from constants import JUMPSPEED, JUMPCOUNT, JUMP_PERIOD, ACCELERATION, IDLE_PERIOD, RUN_PERIOD, GLIDE_PERIOD, ATTACK_PERIOD
from constants import GLIDE_ACCELERATION, DRIFT_DECEL, SCREEN_WIDTH
from constants import SCREEN_HEIGHT, DIRDICT
from constants import RUN_FILE_STEM, JUMP_FILE_STEM, ATTACK_FILE_STEM, GLIDE_FILE_STEM, IDLE_FILE_STEM
from constants import MAX_FRAME_RATE
from state_machine import SimpleStateMachine, ConcurrentStateMachine, PlayerState, DriveHorizontalState
from state_machine import JumpState, IdleHorizontalState, OnPlatformState, DriftHorizontalState, FallState


class Player(pygame.sprite.Sprite):

    def __init__(self):
        super(Player, self).__init__()

        self.level = None
        self.direction = 'R'
        self.x_velocity = 0
        self.y_velocity = 0
        self.jump_count = 0
        self.current_platform = None
        self.vertical_event_queue = Queue.Queue()
        self.horizontal_event_queue = Queue.Queue()

        self._load_animation_frames()

        self._create_concurrent_state_machine()
        self.image = self.csm.current_frame
        self.current_event = None

        self.rect = self.image.get_rect()
        self.height = self.image.get_height()
        self.width = self.image.get_width()

        key_down_method_dct = {pygame.K_LEFT: self.go_left, pygame.K_RIGHT: self.go_right,
                               pygame.K_UP: self.jump}
        key_up_method_dct = {pygame.K_LEFT: self.stop_horizontal, pygame.K_RIGHT: self.stop_horizontal,
                             pygame.K_UP: self.stop_vertical}
        self.key_method_dct = {pygame.KEYDOWN: key_down_method_dct, pygame.KEYUP: key_up_method_dct}

    def _load_animation_frames(self):
        keyframe_range, tween_range = range(10), range(1, 6)
        self.run_frames = load_animation_frames_key_tween(RUN_FILE_STEM, keyframe_range, tween_range)
        self.jump_frames = load_animation_frames_key_tween(JUMP_FILE_STEM, keyframe_range, tween_range)
        self.attack_frames = load_animation_frames_key_tween(ATTACK_FILE_STEM, keyframe_range, tween_range)
        self.glide_frames = load_animation_frames_key_tween(GLIDE_FILE_STEM, keyframe_range, tween_range)
        image_indices = range(10)
        self.idle_frames = load_animation_frames(IDLE_FILE_STEM, image_indices)

    def _create_concurrent_state_machine(self):
        idle_horizontal_state = IdleHorizontalState(self.idle_frames, IDLE_PERIOD, self)
        drive_horizontal_state = DriveHorizontalState(self.run_frames, RUN_PERIOD, self)
        drift_horizontal_state = DriftHorizontalState(self.run_frames, RUN_PERIOD, self)
        horizontal_states = [idle_horizontal_state, drive_horizontal_state, drift_horizontal_state]
        initial_state = idle_horizontal_state

        idle_transitions = [(drive_horizontal_state, 'drive_horizontal', self._can_drive_horizontal)]
        drive_transitions = [(drift_horizontal_state, 'drift_horizontal', self._can_drift_horizontal)]
        drift_transitions = [(drive_horizontal_state, 'drive_horizontal', self._can_drive_horizontal),
                             (idle_horizontal_state, 'idle_horizontal', self._can_stop)]

        state_transition_dct = {idle_horizontal_state: idle_transitions, drive_horizontal_state: drive_transitions,
                                drift_horizontal_state: drift_transitions}

        self.state_horizontal_machine = SimpleStateMachine(state_transition_dct, initial_state, self.horizontal_event_queue)

        on_platform_state = OnPlatformState(self.idle_frames, IDLE_PERIOD, self)
        jump_state = JumpState(self.jump_frames, JUMP_PERIOD, self)
        fall_state = FallState(self.idle_frames, IDLE_PERIOD, self)
        vertical_states = [on_platform_state, jump_state, fall_state]

        initial_state = fall_state
        on_platform_transitions = [(jump_state, 'jump', self._can_jump), (fall_state, 'midair', self._not_on_platform)]
        jump_transitions = [(on_platform_state, 'landing', self._on_platform), (jump_state, 'jump', self._can_jump)]
        fall_transitions = [(on_platform_state, 'landing', self._on_platform), (jump_state, 'jump', self._can_jump)]

        state_transition_dct = {on_platform_state: on_platform_transitions, jump_state: jump_transitions,
                                fall_state: fall_transitions}

        self.state_vertical_machine = SimpleStateMachine(state_transition_dct, initial_state, self.vertical_event_queue)

        state_machine_list = [self.state_horizontal_machine, self.state_vertical_machine]

        state_to_animation_dict = dict()

        for hstate in horizontal_states:
            state_to_animation_dict[(hstate, jump_state)] = jump_state

        for hstate in horizontal_states:
            state_to_animation_dict[(hstate, on_platform_state)] = hstate

        for hstate in horizontal_states:
            state_to_animation_dict[(hstate, fall_state)] = hstate

        self.csm = ConcurrentStateMachine(state_machine_list, state_to_animation_dict)

    """
    def redund(self):
        glide_state = SpriteState(self.glide_frames, self.direction, GLIDE_PERIOD)
        #attack_state = SpriteState(self.attack_frames, self.direction, ATTACK_PERIOD)

    """

    def _on_platform(self):
        return (self.current_platform is not None)

    def _not_on_platform(self):
        return (self.current_platform is None)

    def _can_jump(self):
        return (self.jump_count < 2)

    def _can_run(self):
        return True

    def _can_drive_horizontal(self):
        return True

    def _can_drift_horizontal(self):
        return True

    def _can_stop(self):
        return True

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

    """
    def glidedown(self):
        pass
    """
