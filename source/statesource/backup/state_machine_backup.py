import pygame, time
from constants import MIN_SPEED, MAX_SPEED, MAX_FRAME_RATE, ACCELERATION_PERIOD
from constants import SPEED_DIFF, SLOW_TO_STOP, ACCELERATION
#from constants import JUMPSPEED, JUMPCOUNT, JUMP_PERIOD, ACCELERATION, IDLE_PERIOD, RUN_PERIOD, GLIDE_PERIOD, ATTACK_PERIOD
from constants import GLIDE_ACCELERATION, DRIFT_DECEL, JUMPSPEED
from constants import DIRDICT
from constants import MAX_FRAME_RATE


class PlayerState(object):
    """
    Represents a state.
    """

    def __init__(self):
        pass

    def __init__(self, animation_frames, period, player):
        self.player = player
        self.period = period
        self.current_frame_number = 0
        self.animation_frames = animation_frames
        self.frame_step = float(len(self.animation_frames[self.player.direction])) / float((self.period * MAX_FRAME_RATE))
        self.current_frame = self.animation_frames[self.player.direction][0]

    def update(self):
        self.update_frame()
        # First update y, so update_x can add in platform velocity
        # if vertical collision detected.
        self.update_y()
        self.update_x()

    def update_frame(self):
        self.current_frame_number += self.frame_step

        if self.current_frame_number >= len(self.animation_frames[self.player.direction]) - 1:
            self.current_frame_number = 0

        rounded_current_frame_number = int(round(self.current_frame_number))
        self.current_frame = self.animation_frames[self.player.direction][rounded_current_frame_number]

    def _platform_collision(self):
        collision_list = pygame.sprite.spritecollide(self.player, self.player.level.platform_list, False)

        if len(collision_list) > 0:
            platform = collision_list[0]
            return platform

        else:
            return None

    def _calculate_y_acceleration(self):
        return ACCELERATION

    def update_y(self):
        self.player.y_velocity += self._calculate_y_acceleration()
        self.player.rect.y += self.player.y_velocity
        platform = self._platform_collision()

        if platform is None:
            self.player.vertical_event_queue.put('midair')

        else:

            if self.player.y_velocity > 0:
                self.player.rect.bottom = platform.rect.top
                self.player.current_platform = platform
                self.player.vertical_event_queue.put('landing')

            elif self.player.y_velocity < 0:
                self.player.rect.top = platform.rect.bottom

            self.player.y_velocity = 0

    def update_x(self):

        self.player.rect.x += int(self.player.x_velocity)
        platform = self._platform_collision()

        if platform is not None:

            if self.player.x_velocity > 0:
                self.player.rect.right = platform.rect.left

            elif self.player.x_velocity < 0:
                self.player.rect.left = platform.rect.right

            self.player.x_velocity = 0

    def enter(self):
        pass

    def exit(self):
        pass


class JumpState(PlayerState):
    #Represents state of jumping.

    def __init__(self, animation_frames, period, player):
        PlayerState.__init__(self, animation_frames, period, player)
        self.name = 'jump'

    def enter(self):
        self.player.jump_count += 1
        self.player.current_platform = None
        self.player.y_velocity = -JUMPSPEED

    def update_x(self):
        pass

    def exit(self):
        self.player.jump_count = 0


class FallState(PlayerState):
    #Represents state of falling.

    def __init__(self, animation_frames, period, player):
        PlayerState.__init__(self, animation_frames, period, player)
        self.name = 'fall'

    def update_x(self):
        pass


class OnPlatformState(PlayerState):
    #Represents state of being on a platform.

    def __init__(self, animation_frames, period, player):
        PlayerState.__init__(self, animation_frames, period, player)
        self.name = 'on_platform'

    def enter(self):
        print 'Enter platform state!'
        self.player.x_velocity += self.player.current_platform.x_velocity
        self.player.y_velocity += self.player.current_platform.y_velocity

    """
    def enter(self):

        self.player.x_velocity += self.player.current_platform.x_velocity
        self.player.y_velocity += self.player.current_platform.y_velocity

    def update_y(self):
        PlayerState.update_y(self)
        #self.player.y_velocity += self.player.current_platform.y_velocity

    def update_x(self):
        #PlayerState.update_x(self)
        #self.player.x_velocity += self.player.current_platform.x_velocity
        self.player.x_velocity += self.player.current_platform.x_velocity
    """


class DriveHorizontalState(PlayerState):
    #Represents state of running.

    def __init__(self, animation_frames, period, player):
        PlayerState.__init__(self, animation_frames, period, player)
        self.name = 'drive_horizontal'
        self.delta = SPEED_DIFF/(MAX_FRAME_RATE * ACCELERATION_PERIOD)

    def enter(self):
        self.player.x_velocity = DIRDICT[self.player.direction] * MIN_SPEED
        PlayerState.update_x(self)

    def exit(self):
        pass
        #self.player.x_velocity = 0

    def update_x(self):
        self.player.x_velocity += DIRDICT[self.player.direction] * self.delta
        PlayerState.update_x(self)
        #self.player.x_velocity += DIRDICT[self.player.direction] * self.delta

    def update_y(self):
        pass


class DriftHorizontalState(PlayerState):
    #Player was directed left or right by user, now drifting to a halt.

    def __init__(self, animation_frames, period, player):
        PlayerState.__init__(self, animation_frames, period, player)
        self.name = 'drift_horizontal'

    def update_x(self):
        self.player.x_velocity /= DRIFT_DECEL

        if abs(self.player.x_velocity) < SLOW_TO_STOP:
            self.player.x_velocity = 0
            self.player.horizontal_event_queue.put('idle_horizontal')

        PlayerState.update_x(self)

    def update_y(self):
        pass


class IdleHorizontalState(PlayerState):
    #Player was directed left or right by user, now stopped drifting.

    def __init__(self, animation_frames, period, player):
        PlayerState.__init__(self, animation_frames, period, player)
        self.name = 'idle_horizontal'

    def update_x(self):
        pass

    def update_y(self):
        pass


class SimpleStateMachine(object):

    """
    Represents a simple state machine, having exactly
    one state at any time.
    """

    def __init__(self, state_transition_dct, initial_state, event_queue):
        """
        The dictionary 'state_transition_dct' has keyset = the states of the machine,
        which is a list of strings. The values are lists of pairs of the form (state, fn),
        each representing a state to which the key state may transition, together with a
        function testing whether the transition can occur.
        """
        self.event_queue = event_queue
        self.current_state = initial_state
        self.state_transition_dct = state_transition_dct

    def process_event(self, current_event):
        possible_pairs = self.state_transition_dct[self.current_state]

        for (state, event, fn) in possible_pairs:

            if event == current_event and fn():

                if state != self.current_state:
                    self.current_state.exit()
                    self.current_state = state

                self.current_state.enter()

                #Exit the method the first time a legal
                #transition is found.
                return

    def update(self):
        """
        First, updates the current_state. Then, transitions to a new one
        if a USEREVENT has occurred, and if the transition function returns
        the value True.
        """

        self.current_state.update()
        events = []

        #while not self.current_state.player.event_queue.empty():
        while not self.event_queue.empty():
            #current_event = self.current_state.player.event_queue.get()
            current_event = self.event_queue.get()
            events.append(current_event)

        for current_event in events:
            self.process_event(current_event)


class ConcurrentStateMachine(object):

    """
    Represents a concurrent state machine, consisting of many
    simple state machines.
    """

    def __init__(self, state_machine_list, state_to_animation_dict):
        self.state_machine_list = state_machine_list
        self.state_to_animation_dict = state_to_animation_dict
        self.set_current_frame()
        self.last_time = time.time()
        self.frequency = 0.2

    def set_current_frame(self):
        self.current_state = tuple([sm.current_state for sm in self.state_machine_list])
        self.dominant_state = self.state_to_animation_dict[self.current_state]
        self.current_frame = self.dominant_state.current_frame

    def update(self):
        this_time = time.time()

        if this_time - self.last_time > self.frequency:
            self.last_time = this_time

        for state_machine in self.state_machine_list:
            state_machine.update()
            self.set_current_frame()
