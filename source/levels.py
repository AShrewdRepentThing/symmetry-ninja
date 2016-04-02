import os, pygame
import platforms
import constants
from load_animation_frames import load_animation_frames

ANIMATED_BACKGROUND_FILEPATH = os.path.expanduser('~/Desktop/coding/games/hacking/devgame/waterfall/png/frame_%i.png')
BACKGROUND_ANIMATION_PERIOD = 5

class Level(object):

    # Lists of sprites used in all levels. Add or remove
    # lists as needed for your game.
    platform_list = None
    enemy_list = None

    # Background image
    background = None

    # How far this world has been scrolled left/right
    world_shift = 0
    level_limit = -1000

    def __init__(self, player):

        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.projectile_list = pygame.sprite.Group()
        self.player = player
        self.num_background_frames = 44
        image_indices = range(self.num_background_frames)
        self.background_images = load_animation_frames(ANIMATED_BACKGROUND_FILEPATH, image_indices, reverse=False)
        self.background_animation_count = 0
        self.background_animation_period = BACKGROUND_ANIMATION_PERIOD

    def update(self):
        self.platform_list.update()
        self.enemy_list.update()
        self.projectile_list.update()

    def draw(self, screen):
        x_offset = self.world_shift // 3
        self.background = self.background_images[self.background_animation_count]
        #screen.blit(self.background, (x_offset, 0))
        #screen.blit(self.background, (x_offset - self.background.get_width(), 0))
        screen.blit(self.background, (0, 0))
        self.background_animation_count = (self.background_animation_count + 1) % self.num_background_frames

        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)
        self.projectile_list.draw(screen)

    def shift_world(self, shift_x):
        # Keep track of the shift amount
        self.world_shift += shift_x

        # Go through all the sprite lists and shift
        for platform in self.platform_list:
            platform.rect.x += shift_x

        for enemy in self.enemy_list:
            enemy.rect.x += shift_x

        for projectile in self.projectile_list:
            projectile.rect.x += shift_x


class Level_01(Level):

    def __init__(self, player):

        Level.__init__(self, player)

        self.level_limit = -1500

        # Array with type of platform, and x, y location of the platform.
        level = [[constants.GRASS_LEFT, 500, 500],
                 [constants.GRASS_MIDDLE, 570, 500],
                 [constants.GRASS_RIGHT, 640, 500],
                 [constants.GRASS_LEFT, 800, 400],
                 [constants.GRASS_MIDDLE, 870, 400],
                 [constants.GRASS_RIGHT, 940, 400],
                 [constants.GRASS_LEFT, 1000, 500],
                 [constants.GRASS_MIDDLE, 1070, 500],
                 [constants.GRASS_RIGHT, 1140, 500],
                 [constants.STONE_PLATFORM_LEFT, 1120, 280],
                 [constants.STONE_PLATFORM_MIDDLE, 1190, 280],
                 [constants.STONE_PLATFORM_RIGHT, 1260, 280]]

        # Go through the array above and add platforms
        for platform in level:
            block = platforms.Platform(platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.platform_list.add(block)

        # Add a custom moving platform
        block = platforms.MovingPlatform(constants.STONE_PLATFORM_MIDDLE)
        block.rect.x = 1350
        block.rect.y = 280
        block.boundary_left = 1350
        block.boundary_right = 1600
        block.x_velocity = 3
        block.player = self.player
        block.level = self
        self.platform_list.add(block)


# Create platforms for the level
class Level_02(Level):

    def __init__(self, player):

        Level.__init__(self, player)

        self.level_limit = -1000

        # Array with type of platform, and x, y location of the platform.
        level = [[constants.STONE_PLATFORM_LEFT, 500, 550],
                 [constants.STONE_PLATFORM_MIDDLE, 570, 550],
                 [constants.STONE_PLATFORM_RIGHT, 640, 550],
                 [constants.GRASS_LEFT, 800, 400],
                 [constants.GRASS_MIDDLE, 870, 400],
                 [constants.GRASS_RIGHT, 940, 400],
                 [constants.GRASS_LEFT, 1000, 500],
                 [constants.GRASS_MIDDLE, 1070, 500],
                 [constants.GRASS_RIGHT, 1140, 500],
                 [constants.STONE_PLATFORM_LEFT, 1120, 280],
                 [constants.STONE_PLATFORM_MIDDLE, 1190, 280],
                 [constants.STONE_PLATFORM_RIGHT, 1260, 280]]

        # Go through the array above and add platforms
        for platform in level:
            block = platforms.Platform(platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.platform_list.add(block)

        # Add a custom moving platform
        block = platforms.MovingPlatform(constants.STONE_PLATFORM_MIDDLE)
        block.rect.x = 1500
        block.rect.y = 300
        block.boundary_top = 100
        block.boundary_bottom = 550
        block.y_velocity = -2
        block.player = self.player
        block.level = self
        self.platform_list.add(block)

        """
        # Array with type of platform, and x, y location of the platform.
        level = [[210, 70, 500, 550],
                 [210, 70, 800, 400],
                 [210, 70, 1000, 500],
                 [210, 70, 1120, 280],
                 ]


        # Go through the array above and add platforms
        for platform in level:
            block = platforms.Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        # Add a custom moving platform
        block = platforms.MovingPlatform(70, 70)
        block.rect.x = 1500
        block.rect.y = 300
        block.boundary_top = 100
        block.boundary_bottom = 550
        block.y_velocity = -1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)
        """

