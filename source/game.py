import os, pygame, time, levels
from player import Player

# Global constants

SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
MAX_FRAME_RATE = 60

def main():
    """ Main Program """
    pygame.init()

    # Set the height and width of the screen
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Platformer with moving platforms")

    # Create the player
    player = Player()

    # Create all the levels
    level_list = []
    level_list.append(levels.Level_01(player))
    level_list.append(levels.Level_02(player))

    # Set the current level
    current_level_no = 0
    current_level = level_list[current_level_no]

    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    player.rect.x = 340
    player.rect.y = SCREEN_HEIGHT - player.rect.height
    active_sprite_list.add(player)

    #Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()
    last_time = time.time()

    # -------- Main Program Loop -----------
    while not done:

        this_time = time.time()

        if this_time - last_time > 0.5:

            last_time = this_time

            """
            print 'x_velocity'
            print player.x_velocity

            print 'y_velocity'
            print player.y_velocity

            print 'is_gliding'
            print player.is_gliding

            print 'is_firing_fireball'
            print player.is_firing_fireball

            print 'is_firing_grenade'
            print player.is_firing_grenade

            print 'jump_cycle'
            print player.jump_cycle
            """

            #print 'is_jumping'
            #print player.is_jumping

            #print 'is_driven'
            #print player.is_driven

            #print 'is_firing_fireball'
            #print player.is_firing_fireball

            #print 'player.is_idle'
            #print player.is_idle

            #print 'jump count'
            #print player.jump_count

            #print 'direction'
            #print player.direction

            #print 'frame'
            #print player.frame

        for event in pygame.event.get(): # User did something

            if event.type == pygame.QUIT: # If user clicked close

                done = True # Flag that we are done so we exit this loop

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_LEFT:
                    player.go_left()

                if event.key == pygame.K_RIGHT:
                    player.go_right()

                if event.key == pygame.K_UP:
                    player.jump()

                if event.key == pygame.K_SPACE:
                    player.bullet_attack()

                if event.key == pygame.K_LALT:
                    player.grenade_attack()

                if event.key == pygame.K_LSHIFT:
                    player.glidedown()

            if event.type == pygame.KEYUP:

                if event.key == pygame.K_LEFT and player.x_velocity < 0:
                    player.stop()

                if event.key == pygame.K_RIGHT and player.x_velocity > 0:
                    player.stop()

                if event.key == pygame.K_LSHIFT:
                    player.is_gliding = False

        # Update the player.
        active_sprite_list.update()

        # Update items in the level
        current_level.update()

        # If the player gets near the right side, shift the world left (-x)
        if player.rect.right >= 500:

            diff = player.rect.right - 500
            player.rect.right = 500
            current_level.shift_world(-diff)

        # If the player gets near the left side, shift the world right (+x)
        if player.rect.left <= 120:

            diff = 120 - player.rect.left
            player.rect.left = 120
            current_level.shift_world(diff)

        # If the player gets to the end of the level, go to the next level
        current_position = player.rect.x + current_level.world_shift

        if current_position < current_level.level_limit:

            if current_level_no < len(level_list)-1:

                player.rect.x = 120
                current_level_no += 1
                current_level = level_list[current_level_no]
                player.level = current_level

            else:
                # Out of levels. This just exits the program.
                # You'll want to do something better.
                done = True

        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        current_level.draw(screen)
        active_sprite_list.draw(screen)

        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

        # Limit to 60 frames per second
        clock.tick(MAX_FRAME_RATE)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()

if __name__ == "__main__":
    main()
