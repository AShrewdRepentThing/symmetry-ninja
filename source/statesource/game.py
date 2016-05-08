import os, pygame, time, levels
from player import Player
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_SIZE, MAX_FRAME_RATE, IS_FULLSCREEN, TIMESTEP
from constants import PLAYER_START_X, PLAYER_START_Y

COUNT = 0

class GameSession(object):

    def __init__(self):
        #pygame.init()

        # Set the height and width of the screen
        if IS_FULLSCREEN:
            self.screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(SCREEN_SIZE)

        # Create the self.player
        self.player = Player()
        self.clock = pygame.time.Clock()

        # Create all the levels
        self.level_list = []
        self.level_list.append(levels.Level_01(self.player))
        self.level_list.append(levels.Level_02(self.player))

        # Set the current level
        self.current_level_num = 0
        self.current_level = self.level_list[self.current_level_num]

        # Create player, add to sprite list
        self.active_sprite_list = pygame.sprite.Group()
        self.player.level = self.current_level
        self.player.rect.x = PLAYER_START_X
        self.player.rect.y = PLAYER_START_Y - 500
        self.active_sprite_list.add(self.player)

    def process_event(self, event):

        if event.type == pygame.QUIT: # If user clicked close
            self.done = True # Flag that we are done so we exit this loop

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True

        elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            self.player.handle_input(event)

    def update_everything(self):
        self.current_level.update()
        self.active_sprite_list.update()

        # If the self.player gets near the right side, shift the world left (-x)
        if self.player.rect.right >= 500:
            diff = self.player.rect.right - 500
            self.player.rect.right = 500
            self.current_level.shift_world(-diff)

        # If the self.player gets near the left side, shift the world right (+x)
        if self.player.rect.left <= 120:
            diff = 120 - self.player.rect.left
            self.player.rect.left = 120
            self.current_level.shift_world(diff)

        # If the self.player gets to the end of the level, go to the next level
        current_position = self.player.rect.x + self.current_level.world_shift

        if current_position < self.current_level.level_limit:

            if self.current_level_num < len(self.level_list) - 1:
                self.player.rect.x = 120
                self.current_level_num += 1
                self.current_level = self.level_list[self.current_level_num]
                self.player.level = self.current_level

            else:
                # Out of levels. This just exits the program.
                # You'll want to do something better.
                self.done = True

    def draw_everything(self):
        self.current_level.draw(self.screen)
        self.active_sprite_list.draw(self.screen)
        pygame.display.flip()
        self.clock.tick(MAX_FRAME_RATE)

    def start_loop(self):
        #Loop until the user clicks the close button.
        pygame.init()
        self.done = False

        # Used to manage how fast the screen updates
        last_time = time.time()

        # -------- Main Program Loop -----------
        while not self.done:
            this_time = time.time()
            delta_t = this_time - last_time

            if delta_t > 0.5:
                pass

            for event in pygame.event.get(): # User did something
                self.process_event(event)

            if delta_t > TIMESTEP:
                last_time = this_time
                self.update_everything()
                self.draw_everything()

        #End when self.done = True
        pygame.quit()


def main():
    session = GameSession()
    session.start_loop()


if __name__ == "__main__":
    main()

