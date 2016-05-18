import os

IS_FULLSCREEN = False
MAX_FRAME_RATE = 60
TIMESTEP = 1.0/40.0

# Colors

BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
BLUE     = (   0,   0, 255)

# Screen dimensions

SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
MAX_FRAME_RATE = 60
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

#Tile positions

GRASS_LEFT            = (576, 720, 70, 70)
GRASS_RIGHT           = (576, 576, 70, 70)
GRASS_MIDDLE          = (504, 576, 70, 70)
STONE_PLATFORM_LEFT   = (432, 720, 70, 40)
STONE_PLATFORM_MIDDLE = (648, 648, 70, 40)
STONE_PLATFORM_RIGHT  = (792, 648, 70, 40)

# Projectile constants

GRENADE_PERIOD = 20
FIREBALL_PERIOD = 10
GRENADE_EXPLOSION_PERIOD = 15
EXPLOSION_Y_OFFSET = 120
EXPLOSION_X_OFFSET = 10
GRENADE_ACCELERATION = 1.5
FIREBALL_ACCELERATION = 0.0


#Player constants

PLAYER_START_X = 570
PLAYER_START_Y = SCREEN_HEIGHT - 80

#MIN_SPEED = 10
#MAX_SPEED = 15
MIN_SPEED = 4
MAX_SPEED = 8
SPEED_DIFF = MAX_SPEED - MIN_SPEED
ACCELERATION_PERIOD = 0.75
SLOW_TO_STOP = 1.0
JUMPSPEED = 25
JUMPCOUNT = 2
IDLE_PERIOD = 20
#RUN_PERIOD = 5
RUN_PERIOD = 0.333
#JUMP_PERIOD = 2
JUMP_PERIOD = 0.5
GLIDE_PERIOD = 5
ATTACK_PERIOD = 8
SLIDE_PERIOD = 2
ACCELERATION = 1.5
GLIDE_ACCELERATION = 0.2
DRIFT_AIR_DECEL = 1.1
DRIFT_GROUND_DECEL = 1.5
SLIDE_DECEL = 1.15
SLIDE_INITIAL_VELOCITY = 28.0
GUN_HEIGHT = 0.0
DIRDICT = {'L': -1.0, 'R': 1.0}

# Projectile art asset locations

FIREBALL_STR = '~/Desktop/coding/games/symmetry-ninja/artassets/sprites/flames/fireball/scaled/fireball_000%i_%i.png'
FIREBALL_FILE_PATH = os.path.expanduser(FIREBALL_STR)
GRENADE_STR = '~/Desktop/coding/games/symmetry-ninja/artassets/sprites/grenade/scaled/grenade_%i.png'
GRENADE_FILE_PATH = os.path.expanduser(GRENADE_STR)
GRENADE_EXPLOSION_STR = '/Users/enrightward/Desktop/coding/games/symmetry-ninja/artassets/sprites/grenade_explosion/slice_%i.png'
GRENADE_EXPLOSION_FILE_PATH = os.path.expanduser(GRENADE_EXPLOSION_STR)

# Player art asset locations

RUN_FILE_STEM = os.path.expanduser('~/Desktop/coding/games/symmetry-ninja/artassets/sprites/ninja/sixtyfps/run/Run__00%i_%i.png')
JUMP_FILE_STEM = os.path.expanduser('~/Desktop/coding/games/symmetry-ninja/artassets/sprites/ninja/sixtyfps/jump/Jump__00%i_%i.png')
ATTACK_FILE_STEM = os.path.expanduser('~/Desktop/coding/games/symmetry-ninja/artassets/sprites/ninja/sixtyfps/attack/Attack__00%i_%i.png')
GLIDE_FILE_STEM = os.path.expanduser('~/Desktop/coding/games/symmetry-ninja/artassets/sprites/ninja/sixtyfps/glide/Glide_00%i_%i.png')
IDLE_FILE_STEM = os.path.expanduser('~/Desktop/coding/games/symmetry-ninja/artassets/sprites/ninja/sixtyfps/idle/Idle__00%i.png')
SLIDE_FILE_STEM = os.path.expanduser('~/Desktop/coding/games/symmetry-ninja/artassets/sprites/ninja/sixtyfps/slide/Slide__00%i.png')

# Environment art asset locations

TILES_SS_PATH = os.path.expanduser('~/Desktop/coding/games/symmetry-ninja/artassets/tilesets/basic_tiles.png')
ANIMATED_BACKGROUND_FILEPATH = os.path.expanduser('~/Desktop/coding/games/symmetry-ninja/artassets/sprites/waterfall/png/frame_%i.png')
BACKGROUND_ANIMATION_PERIOD = 5
