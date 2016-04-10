from constants import MAX_FRAME_RATE


class SimpleStateMachine(object):
        """
        Represents a simple state machine, having exactly
        one state at all times.
        """

    def __init__(self, state_transition_dct, initial_state):
        """
        The dictionary 'state_transition_dct' has keysetthe state_names of the machine,
        which is a list of strings. The values are lists of pairs of the form
        (state_name, test_function), each representing a state to which the key state
        may transition, together with a function testing whether the transition can occur.
        """
        self.current_state = initial_state
        self.state_transition_dct = state_transition_dct

    def update(self, state, **kwargs):
        """
        Set the current_state equal to 'state' if this is allowed, otherwise do nothing.
        """
        target_states = [state for state, fn in self.state_transition_dct[self.current_state]]
        if state in target_states and fn(**kwargs):
            self.current_state = state
        else:
            pass


class ConcurrentStateMachine(object):
        """
        Represents a concurrent state machine which is a product of
        N simple state machines.
        """

    def __init__(self, state_machine_list):
        self.state_machine_list = state_machine_list
        self.current_state_tuple = tuple([sm.current_state for sm in self.state_machine_list])
        state_llist = [sm.state_transition_dct.keys() for sm in self.state_machine_list]
        self.state_tuples = list(itertools.product(*state_llist))

    def update(self, state):
        """
        Set the current_state equal to 'state' if this is allowed,
        otherwise do nothing.
        """
        for state_machine in self.state_machine_list:
            state_machine.update()

        self.current_state_tuple = tuple([sm.current_state for sm in self.state_machine_list])


class SpriteStateMachine(ConcurrentStateMachine):
        """
        Represents a concurrent state machine which is a product of
        N simple state machines.
        """

    def __init__(self, state_machine_list, state_to_animation_dct, direction):
        """state_to_animation_dct has keys state_tuples and values pairs (animation_frames, period)"""
        super(ConcurrentStateMachine, self).__init__()
        self.direction = direction
        self.state_to_animation_dct = state_to_animation_dct
        self.reset_frames()

    def reset_frames(self):
        self.animation_frames, self.period = self.state_to_animation_dct[self.current_state_tuple]
        self.frame_step = len(self.animation_frames) / (self.period * MAX_FRAME_RATE)
        self.current_frame_number = 0
        self.current_frame = self.animation_frames[self.direction][0]

    def update(self, state, direction):
        """
        Set the current_state equal to 'state' if this is allowed,
        otherwise do nothing.
        """
        previous_state_tuple = self.current_state_tuple

        for state_machine in self.state_machine_list:
            state_machine.update()

        self.current_state_tuple = tuple([sm.current_state for sm in self.state_machine_list])
        self.direction = direction

        if previous_state_tuple == current_state_tuple:
            self.current_frame_number += self.frame_step

            if self.current_frame_number >= len(self.animation_frames[direction]):
                self.current_frame_number = 0
            rounded_current_frame_number = int(round(self.current_frame_number))
            self.current_frame = self.animation_frames[direction][rounded_current_frame_number]
        else:
            self.reset_frames()
