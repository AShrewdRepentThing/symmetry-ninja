import os, pygame
from load_animation_frames import load_animation_frames, load_animation_frames_key_tween
from constants import GUN_HEIGHT, DIRDICT, FIREBALL_FILE_PATH, GRENADE_FILE_PATH
from constants import GRENADE_EXPLOSION_STR, GRENADE_EXPLOSION_FILE_PATH, GRENADE_PERIOD
from constants import FIREBALL_PERIOD, GRENADE_EXPLOSION_PERIOD, EXPLOSION_Y_OFFSET
from constants import EXPLOSION_X_OFFSET, SCREEN_WIDTH, SCREEN_HEIGHT
from constants import GRENADE_ACCELERATION, FIREBALL_ACCELERATION


class Projectile(pygame.sprite.Sprite):

    def __init__(self, player, velocity, _type):

        super(Projectile, self).__init__()

        # Set speed vector
        x_vel, y_vel = velocity
        self.x_velocity = DIRDICT[player.direction] * x_vel + 0.5 * player.x_velocity
        self.y_velocity = -y_vel

        self._type = _type
        self.player = player
        self.level = player.level
        self.direction = player.direction
        self.animation_timer = 0
        self.is_exploding = False
        self.has_exploded = False
        self.current_block = None

        if _type == 'fireball':
            keyframe_range = range(1, 7)
            tween_range = range(1, 10)
            self.image_frames = load_animation_frames_key_tween(FIREBALL_FILE_PATH, keyframe_range, tween_range)
            self.animation_period = FIREBALL_PERIOD
            self.explosion_frames = None
            self.acceleration = FIREBALL_ACCELERATION

        elif _type == 'grenade':
            self.explosion_timer = 0
            self.animation_period = GRENADE_PERIOD
            self.explosion_period = GRENADE_EXPLOSION_PERIOD
            self.image_frames = load_animation_frames(GRENADE_FILE_PATH, image_indices=range(60))
            self.explosion_frames = load_animation_frames(GRENADE_EXPLOSION_FILE_PATH, image_indices=range(1, 31))
            self.acceleration = GRENADE_ACCELERATION

        self.image = self.image_frames[self.direction][0]
        self.height = self.image.get_height()
        self.width = self.image.get_width()
        self.rect = self.image.get_rect()
        self.rect.x = player.rect.x
        self.rect.y = player.rect.y + player.height * GUN_HEIGHT

    def eliminate(self):

        if self._type == 'fireball':
            self.player.is_firing_fireball = False

        if self._type == 'grenade':
            self.player.is_firing_grenade = False

        self.kill()

    def compute_current_frame(self):

        if self.is_exploding:

            if self._type == 'grenade':
                step = len(self.explosion_frames[self.direction]) // self.explosion_period
                self.frame = step * self.explosion_timer

                if self.explosion_timer < self.explosion_period:
                    self.image = self.explosion_frames[self.direction][self.frame]
                    self.explosion_timer += 1

                else:
                    self.has_exploded = True

            elif self._type == 'fireball':
                self.has_exploded = True

        else:

            if self.animation_timer == self.animation_period:
                self.animation_timer = 0
            length = len(self.image_frames[self.direction])
            step = length // self.animation_period
            self.frame = step * self.animation_timer
            self.image = self.image_frames[self.direction][self.frame]
            self.animation_timer += 1

    def _struck_platform(self):
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        return block_hit_list[0] if len(block_hit_list) > 0 else None

    def get_x_velocity(self):
        return 0 if self.is_exploding else self.x_velocity

    def update_x_coords(self):
        self.rect.x += self.get_x_velocity()
        block = self._struck_platform()

        if block is not None:

            if self.x_velocity > 0:
                self.rect.right = block.rect.left

            elif self.x_velocity < 0:
                self.rect.left = block.rect.right

            self.x_velocity = 0
            self.is_exploding = True

        return block

    def get_y_velocity(self):
        return 0 if self.is_exploding else self.y_velocity + self.acceleration

    def update_y_coords(self):
        self.y_velocity = self.get_y_velocity()
        self.rect.y += self.y_velocity
        block = self._struck_platform()

        if block is not None:

            if self.y_velocity > 0:
                self.rect.bottom = block.rect.top
                self.current_block = block

            elif self.y_velocity < 0:
                self.rect.top = block.rect.bottom

            self.y_velocity = 0
            self.is_exploding = True

        return block

    def is_off_screen(self):
        return abs(self.player.rect.x - self.rect.x) > SCREEN_WIDTH

    def update(self):

        if self.is_off_screen() or self.has_exploded:
            self.eliminate()

        blocks = (self.update_x_coords(), self.update_y_coords())

        for block in blocks:
            if block is not None:
                if self.explosion_frames is not None:
                    self.is_exploding = True
                    self.image_frames = self.explosion_frames
                    self.image = self.image_frames[self.direction][0]
                    self.rect.x -= EXPLOSION_X_OFFSET
                    self.rect.y -= EXPLOSION_Y_OFFSET
                else:
                    self.has_exploded = True

        self.compute_current_frame()
