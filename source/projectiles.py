import os, pygame
from load_animation_frames import load_animation_frames, load_animation_frames_key_tween

# Global constants

GUN_HEIGHT = 0.0
DIRDICT = {'L': -1.0, 'R': 1.0}

FIREBALL_STR = '~/Desktop/coding/games/hacking/devgame/flame_sprites/fireball/scaled/fireball_000%i_%i.png'
FIREBALL_FILE_PATH = os.path.expanduser(FIREBALL_STR)

GRENADE_STR = '~/Desktop/coding/games/hacking/devgame/grenade_sprites/scaled/grenade_%i.png'
GRENADE_FILE_PATH = os.path.expanduser(GRENADE_STR)

GRENADE_EXPLOSION_STR = '/Users/enrightward/Desktop/coding/games/hacking/devgame/grenade_explosion_sprites/slice_%i.png'
GRENADE_EXPLOSION_FILE_PATH = os.path.expanduser(GRENADE_EXPLOSION_STR)

GRENADE_PERIOD = 20
FIREBALL_PERIOD = 10
GRENADE_EXPLOSION_PERIOD = 15
EXPLOSION_Y_OFFSET = 120
EXPLOSION_X_OFFSET = 10

SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600


class Projectile(pygame.sprite.Sprite):

    def __init__(self, player, velocity, acceleration, _type):

        super(Projectile, self).__init__()

        # Set speed vector
        x_vel, y_vel = velocity
        self.x_velocity = DIRDICT[player.direction] * x_vel + 0.5 * player.x_velocity
        self.y_velocity = -y_vel

        # List of sprites we can bump against
        self._type = _type
        self.player = player
        self.level = player.level
        self.acceleration = acceleration
        self.direction = player.direction
        self.animation_timer = 0
        self.is_exploding = False

        if _type == 'fireball':
            keyframe_range = range(1, 7)
            tween_range = range(1, 10)
            self.image_frames = load_animation_frames_key_tween(FIREBALL_FILE_PATH, keyframe_range, tween_range)
            self.animation_period = FIREBALL_PERIOD
            self.explosion_frames = None

        elif _type == 'grenade':
            self.explosion_timer = 0
            self.animation_period = GRENADE_PERIOD
            self.explosion_period = GRENADE_EXPLOSION_PERIOD
            self.image_frames = load_animation_frames(GRENADE_FILE_PATH, image_indices=range(60))
            self.explosion_frames = load_animation_frames(GRENADE_EXPLOSION_FILE_PATH, image_indices=range(1, 31))

        self.image = self.image_frames[self.direction][0]
        self.height = self.image.get_height()
        self.width = self.image.get_width()
        self.rect = self.image.get_rect()
        self.rect.x = player.rect.x
        self.rect.y = player.rect.y + player.height * GUN_HEIGHT

    def calc_grav(self):
        self.y_velocity += self.acceleration

    def _eliminate(self):
        if self._type == 'fireball':
            self.player.is_firing_fireball = False
        if self._type == 'grenade':
            self.player.is_firing_grenade = False
        self.kill()

    def update(self):
        if abs(self.player.rect.x - self.rect.x) > SCREEN_WIDTH:
            self._eliminate()

        elif self.is_exploding:
            step = len(self.explosion_frames[self.direction]) // self.explosion_period
            self.frame = step * self.explosion_timer

            if self.explosion_timer < self.explosion_period:
                self.image = self.explosion_frames[self.direction][self.frame]
                self.explosion_timer += 1

            else:
                self._eliminate()

        else:
            # Move left/right
            self.rect.x += self.x_velocity
            self.calc_grav()
            self.rect.y += self.y_velocity
            pos = self.rect.x + self.level.world_shift

            if self.animation_timer == self.animation_period:
                self.animation_timer = 0
            length = len(self.image_frames[self.direction])
            step = length // self.animation_period
            self.frame = step * self.animation_timer
            self.image = self.image_frames[self.direction][self.frame]
            self.animation_timer += 1

            # See if we hit anything
            block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)

            if len(block_hit_list) > 0 or self.rect.bottom > SCREEN_HEIGHT:
                if self.explosion_frames is not None:
                    self.is_exploding = True
                    self.image_frames = self.explosion_frames
                    self.image = self.image_frames[self.direction][0]
                    self.rect.x -= EXPLOSION_X_OFFSET
                    self.rect.y -= EXPLOSION_Y_OFFSET
                else:
                    self._eliminate()
