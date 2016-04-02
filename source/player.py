import os, pygame, platforms, projectiles
from load_animation_frames import load_animation_frames, load_animation_frames_key_tween

# Global constants

MIN_SPEED = 10
MAX_SPEED = 15
MAX_FRAME_RATE = 60
ACCELERATION_PERIOD = 0.75

JUMPSPEED = 25
JUMPCOUNT = 2
JUMP_PERIOD = 20
ACCELERATION = 1.5
GLIDE_ACCELERATION = 0.2
DRIFT_DECEL = 1.1

# Screen dimensions
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
DIRDICT = {'L': -1.0, 'R': 1.0}


class Player(pygame.sprite.Sprite):

    """
    This class represents the player.
    """

    def __init__(self):
        # Call the parent's constructor
        super(Player, self).__init__()

        self.is_jumping = False
        self.is_drifting = False
        self.is_walking = False
        self.is_idle = True
        self.is_firing_fireball = False
        self.is_firing_grenade = False
        self.is_gliding = False
        self.is_driven = False

        self.jump_count = 0
        self.frame = 0
        self.direction = 'R'
        self.current_block = None
        self.jump_cycle = 1

        # Set speed vector of player
        self.x_velocity = 0
        self.y_velocity = 0
        self.walk_period = 5
        self.jump_period = JUMP_PERIOD
        self.jump_timer = 0
        self.idle_period = 20
        self.glide_period = 5
        self.glide_timer = 0
        self.attack_period = 8
        self.attack_timer = 0
        self.acceleration_period = ACCELERATION_PERIOD
        self.acceleration_meter = 0
        self.max_speed = MAX_SPEED
        self.min_speed = MIN_SPEED

        # List of sprites we can bump against
        self.level = None

        keyframe_range, tween_range = range(10), range(1, 6)

        run_file_stem = os.path.expanduser('~/Desktop/coding/games/hacking/devgame/ninjasprites/sixtyfps/run/Run__00%i_%i.png')
        self.walking_frames = load_animation_frames_key_tween(run_file_stem, keyframe_range, tween_range)

        jump_file_stem = os.path.expanduser('~/Desktop/coding/games/hacking/devgame/ninjasprites/sixtyfps/jump/Jump__00%i_%i.png')
        self.jump_frames = load_animation_frames_key_tween(jump_file_stem, keyframe_range, tween_range)

        attack_file_stem = os.path.expanduser('~/Desktop/coding/games/hacking/devgame/ninjasprites/sixtyfps/attack/Attack__00%i_%i.png')
        self.attack_frames = load_animation_frames_key_tween(attack_file_stem, keyframe_range, tween_range)

        glide_file_stem = os.path.expanduser('~/Desktop/coding/games/hacking/devgame/ninjasprites/sixtyfps/glide/Glide_00%i_%i.png')
        self.gliding_frames = load_animation_frames_key_tween(glide_file_stem, keyframe_range, tween_range)

        image_indices = range(10)
        idle_file_stem = os.path.expanduser('~/Desktop/coding/games/hacking/devgame/ninjasprites/sixtyfps/idle/Idle__00%i.png')
        self.idle_frames = load_animation_frames(idle_file_stem, image_indices)

        # Set the image the player starts with
        self.image = self.idle_frames['R'][0]

        # Set a referance to the image rect.
        self.rect = self.image.get_rect()

        self.height = self.image.get_height()
        self.width = self.image.get_width()


    def _compute_current_frame(self):

        pos = self.rect.x + self.level.world_shift

        if self.is_jumping:

            if self.is_gliding and self.y_velocity >= 0:
                length = len(self.gliding_frames[self.direction])
                step = length // self.glide_period
                self.frame = step * self.glide_timer

                if self.glide_timer < self.glide_period:
                    self.image = self.gliding_frames[self.direction][self.frame]
                    self.glide_timer += 1

                else:
                    self.image = self.gliding_frames[self.direction][-1]

            else:
                length = len(self.jump_frames[self.direction])
                step = length // self.jump_period
                self.frame = step * self.jump_timer

                if self.jump_timer < self.jump_period:
                    self.image = self.jump_frames[self.direction][self.frame]
                    self.jump_timer += 1

                else:
                    self.image = self.idle_frames[self.direction][0]
                    self.jump_timer = 0

        elif self.is_walking:
            self.frame = (pos // self.walk_period) % len(self.walking_frames[self.direction])
            self.image = self.walking_frames[self.direction][self.frame]

            if self.is_driven:
                speed = self.acceleration_meter * (self.max_speed - self.min_speed) + self.min_speed
                self.x_velocity = speed * DIRDICT[self.direction]
                delta = 1.0 / (float(self.acceleration_period) * float(MAX_FRAME_RATE))
                self.acceleration_meter = min(self.acceleration_meter + delta, 1.0)

        elif self.is_idle:
            self.frame = (pos // self.idle_period) % len(self.idle_frames[self.direction])
            self.image = self.idle_frames[self.direction][self.frame]

        if self.is_firing_fireball:
            step = len(self.attack_frames[self.direction]) // self.attack_period

            self.frame = step * self.attack_timer

            if self.attack_timer < self.attack_period:
                self.image = self.attack_frames[self.direction][self.frame]
                self.attack_timer += 1

            else:
                self.image = self.idle_frames[self.direction][0]
                self.is_firing_fireball = False
                self.attack_timer = 0

    def _calculate_gravity(self):
        if self.is_gliding and self.y_velocity >= 0:
            return GLIDE_ACCELERATION

        else:
            return ACCELERATION

    def _compute_y_velocity(self):
        if self._on_floor() and self.is_jumping:
            return -JUMPSPEED
        else:
            return self.y_velocity + self._calculate_gravity()

    def _on_floor(self):
        return self.rect.bottom >= SCREEN_HEIGHT

    def _on_floor_or_block(self):
        return self._on_floor() or self.current_block is not None

    def _is_hitting_ground(self):
        return self.y_velocity > 0 and self._on_floor()

    def _struck_platform(self):
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        return block_hit_list[0] if len(block_hit_list) > 0 else None

    def update_y_coords(self):
        self.y_velocity = self._compute_y_velocity()
        self.rect.y += self.y_velocity

        block = self._struck_platform()

        if block is not None:
            if self.y_velocity > 0:
                self.rect.bottom = block.rect.top
                self.is_jumping = False
                self.is_gliding = False
                self.current_block = block

                if self.x_velocity == 0:
                    self.is_walking = False
                    self.is_idle = True

                else:
                    self.is_walking = True
                    self.is_idle = False

            elif self.y_velocity < 0:
                self.rect.top = block.rect.bottom

            self.y_velocity = 0
            self.glide_timer = 0
            self.jump_timer = 0

            if isinstance(block, platforms.MovingPlatform):
                self.rect.x += block.x_velocity

        elif self._is_hitting_ground():
            self.y_velocity = 0
            self.glide_timer = 0
            self.jump_timer = 0
            self.is_jumping = False
            self.is_gliding = False
            self.is_idle = True
            self.current_block = None
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def update_x_coords(self):
        self.rect.x += self.x_velocity

        if self.is_drifting:
            self.drift()

        block = self._struck_platform()
        if block is not None:
            if self.x_velocity > 0:
                self.rect.right = block.rect.left

            elif self.x_velocity < 0:
                self.rect.left = block.rect.right

            self.is_idle = True

    def update(self):
        self._compute_current_frame()
        self.update_y_coords()
        self.update_x_coords()

    def jump(self):
        if self._on_floor_or_block() or self.jump_count < JUMPCOUNT:
            if self._on_floor_or_block():
                self.jump_count = 1

            elif self.jump_count < JUMPCOUNT:
                self.jump_count += 1

            self.y_velocity = -JUMPSPEED
            self.is_jumping = True
            self.is_walking = False
            self.is_idle = False

    def glidedown(self):
        if self.is_jumping:
            self.is_gliding = True

    def go_left(self):
        self.x_velocity = -self.min_speed
        self.direction = 'L'
        self.is_drifting = False
        self.jump_cycle = 1

        if self._on_floor_or_block():
            self.is_jumping = False
            self.is_walking = True
            self.is_driven = True
            self.is_idle = False

    def go_right(self):
        self.x_velocity = self.min_speed
        self.direction = 'R'
        self.is_drifting = False
        self.jump_cycle = 1

        if self._on_floor_or_block():
            self.is_jumping = False
            self.is_walking = True
            self.is_driven = True
            self.is_idle = False

    def drift(self):
        if self.is_jumping and abs(self.x_velocity) > 0.1:
            self.x_velocity /= DRIFT_DECEL

        else:
            self.x_velocity = 0
            self.is_drifting = False
            self.is_idle = True

    def stop(self):
        if self.is_jumping:
            self.is_drifting = True

        else:
            self.x_velocity = 0
            self.is_idle = True

        self.is_walking = False
        self.is_driven = False
        self.acceleration_meter = 0.0

    def bullet_attack(self):
        self._create_fireball()
        self.attack_timer = 0
        self.is_firing_fireball = True
        self.frame = 0

    def grenade_attack(self):
        self._create_grenade()
        self.is_firing_grenade = True

    def _create_fireball(self):
        acceleration = 0.0
        velocity = (15, 0)
        _type = 'fireball'
        projectile = projectiles.Projectile(self, velocity, acceleration, _type)
        self.level.projectile_list.add(projectile)

    def _create_grenade(self):
        acceleration = 1.5
        velocity = (10, 20)
        _type = 'grenade'
        projectile = projectiles.Projectile(self, velocity, acceleration, _type)
        self.level.projectile_list.add(projectile)
