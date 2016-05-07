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

    def __init__(self, player):
        self.player = player

    def update(self):
        # First update y, so update_x can add in platform velocity
        # if vertical collision detected.
        self.update_y()
        self.update_x()

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
        self.player.rect.y += int(self.player.y_velocity)
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

    def can_enter(self):
        return True


class JumpState(PlayerState):
    #Represents state of jumping.

    def __init__(self, player):
        PlayerState.__init__(self, player)
        self.name = 'jump'
        self.jump_count = 0

    def enter(self):
        self.jump_count += 1
        self.player.current_platform = None
        self.player.y_velocity = -JUMPSPEED

    def exit(self):
        self.jump_count = 0

    def can_enter(self):
        return (self.jump_count < 2)


class FallState(PlayerState):
    #Represents state of falling.

    def __init__(self, player):
        PlayerState.__init__(self, player)
        self.name = 'fall'

    """
    def can_enter(self):
        #return (self.player.current_platform is not None)
        return (self.player.current_platform is None)
    """


class GlideState(PlayerState):
    #Represents state of gliding.

    def __init__(self, player):
        PlayerState.__init__(self, player)
        self.name = 'glide'

    def _calculate_y_acceleration(self):
        return GLIDE_ACCELERATION

    def can_enter(self):
        #return (self.player.y_velocity >= 0)
        return True


class OnPlatformState(PlayerState):
    #Represents state of being on a platform.

    def __init__(self, player):
        PlayerState.__init__(self, player)
        self.name = 'on_platform'

    def update_x(self):
        self.player.rect.x += int(self.player.current_platform.x_velocity)
        PlayerState.update_x(self)

    def update_y(self):
        self.player.rect.y += int(self.player.current_platform.y_velocity)
        PlayerState.update_y(self)

    def can_enter(self):
        return (self.player.current_platform is not None)


class DriveHorizontalState(PlayerState):
    #Represents state of running.

    def __init__(self, player):
        PlayerState.__init__(self, player)
        self.name = 'drive_horizontal'
        self.delta = SPEED_DIFF/(MAX_FRAME_RATE * ACCELERATION_PERIOD)

    def enter(self):
        self.player.x_velocity = DIRDICT[self.player.direction] * MIN_SPEED
        PlayerState.update_x(self)

    def update_x(self):
        self.player.x_velocity += DIRDICT[self.player.direction] * self.delta
        PlayerState.update_x(self)

    def update_y(self):
        pass


class DriftHorizontalState(PlayerState):
    #Player was directed left or right by user, now drifting to a halt.

    def __init__(self, player):
        PlayerState.__init__(self, player)
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

    def __init__(self, player):
        PlayerState.__init__(self, player)
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

        for (state, event) in possible_pairs:

            if event == current_event and state.can_enter():

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

        has_changed = False
        self.current_state.update()
        events = []

        while not self.event_queue.empty():
            current_event = self.event_queue.get()
            events.append(current_event)

        for current_event in events:
            has_changed = self.process_event(current_event)

        return has_changed


class ConcurrentStateMachine(object):

    #Represents a concurrent state machine, consisting of many
    #simple state machines.

    def __init__(self, state_machine_list, state_to_animation_dict):
        self.state_machine_list = state_machine_list
        self.state_to_animation_dict = state_to_animation_dict
        self.player = self.state_machine_list[0].current_state.player
        self.current_state = tuple([sm.current_state for sm in self.state_machine_list])

        self.set_current_frames()

        self.last_time = time.time()
        self.frequency = 0.2

    def update_frame(self):
        self.current_frame_number += self.frame_step

        if self.current_frame_number >= len(self.animation_frames[self.player.direction]) - 1:
            self.current_frame_number = 0

        rounded_current_frame_number = int(round(self.current_frame_number))
        self.current_frame = self.animation_frames[self.player.direction][rounded_current_frame_number]

    def set_current_frames(self):
        self.current_frame_number = 0
        self.animation_frames, self.animation_period = self.state_to_animation_dict[self.current_state]
        self.frame_step = float(len(self.animation_frames[self.player.direction])) / float((self.animation_period * MAX_FRAME_RATE))
        self.current_frame = self.animation_frames[self.player.direction][self.current_frame_number]
        print 'current_state'
        print self.current_state
        print 'self.animation_period'
        print self.animation_period

    def update(self):
        old_state = self.current_state

        for state_machine in self.state_machine_list:
            state_machine.update()

        self.current_state = tuple([sm.current_state for sm in self.state_machine_list])

        if old_state == self.current_state:
            self.update_frame()
        else:
            self.set_current_frames()
