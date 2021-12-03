"""
I-M Siegel

Explosion graphics from https://www.explosiongenerator.com/, via Arcade
resources

Other images from Space Shooter (Redux, plus fonts and sounds) by Kenney
Vleugels (www.kenney.nl), licensed under Creative Commons.
https://kenney.nl/assets/space-shooter-redux


Practice:
    Done - moving with angles (eg space ship)
    - colliding sprites with lists (enemies, enemy shooters)
    - disappear (after shot)
    - spawning (already done, but can check how they do)

TODO:
    - clean up (eg basic enemy from which asteroids and enemy ships descend)
    - add add damage
    - implement strings
    - differing functions for resetting for new game and resetting for level
    - add lives?
    - add sounds
    - add levels and design levels
        - add shortcuts (cmd 1, cmd 2, cmd 3)
    - add start screen
    - add end screen
    - add a compass so player can see where they're facing
    - standardise images (paths and who controls, sprite or game)

DONE:
    - add enemy lasers
    - add collision between player lasers and asteroids, player lasers and
        enemy ships
    - add collision between enemy lasers and player ship
    - add score
    - add explosions

"""


import arcade
import math
import random


SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Space Shooter"

# TODO: put this laser_image just within player
LASER_IMAGE = "spaceshooter/PNG/Lasers/laserBlue01.png"

METEOR_POINTS = 5
ENEMY_POINTS = 15

IMAGE_SCALE = .5


class Player(arcade.Sprite):
    """
    Player sprite inherits from arcade.Sprite to represent the player on in
    the game. Makes use of arcade.Sprite attributes and methods to update
    (move or change) the player's sprite in response to player input and
    interactions with other sprites.

    ATTRIBUTES used (see arcade.Sprite for other, unused attributes):
    :speed:
    :angle_rate:
    :forward_rate:
    :angle:
    :center_x:
    :center_y:
    :change_x:
    :change_y:
    :change_angle:
    :width:

    METHODS used (see arcade.Sprite for other, unused methods):
    """

    def __init__(self, image, scale=IMAGE_SCALE):
        super().__init__(filename=image, scale=scale)
        """
        Constructor. Sets attributes self.speed, self.angle_rate and 
        self.forward_rate. Uses arcade.Sprite default settings for other
        attributes, including self.angle.
        """

        # Set starting speed
        self.speed = 0

        # No need to set self.angle since arcade.Sprite initializes it to 0
        # Angle is in degrees; angle 0 == North

        # Rates per second, not per update (approx rates of 5 per update)
        # Attributes, not global constants, so they can be updated with level
        # changes
        self.angle_rate = 360
        self.forward_rate = 360

        # Need to know diagonal size to completely hide sprite offscreen at
        # at any angle
        self.diagonal_size = (self.width ** 2 + self.height ** 2) ** .5

    def on_update(self, delta_time: float = 1 / 60):
        """
        Updates sprite's position by changing angle, center_x and center_y to
        animate sprite. Should be called at least 30 times per second.
        Uses delta_time as a factor in setting new position and angle to
        smooth movement in case of a delay in the frequency of calls to
        on_update. Otherwise, a call to on_update with delta_time of .5
        seconds would move the sprite the same amount as a call with
        delta_time of .01.
        :param delta_time: time since last call
        :return: None
        """

        # Update angle player is facing
        # Multiply by delta_time for smooth movement
        self.angle += self.change_angle * delta_time

        # Find change_x and change_y based on new angle (essentially a target
        # point). Default angle is North, so target point on unit circle
        # x-coordinate (change_x) is negative sin (not positive cos) and
        # y-coordinate (change_y) is cos (not sin)
        self.change_x = -math.sin(math.radians(self.angle))
        self.change_y = math.cos(math.radians(self.angle))

        # Move sprite in direction it's facing, as determined above
        self.center_x += self.change_x * self.speed * delta_time
        self.center_y += self.change_y * self.speed * delta_time

        # Let sprite go offscreen so player feels like they can get lost,
        # but keep sprite from going far so player can bring it back onto
        # screen immediately
        if self.center_x < -1 * self.diagonal_size / 2:
            self.center_x = -1 * self.diagonal_size / 2
        if self.center_x > SCREEN_WIDTH + self.diagonal_size / 2:
            self.center_x = SCREEN_WIDTH + self.diagonal_size / 2
        if self.center_y < -1 * self.diagonal_size / 2:
            self.center_y = -1 * self.diagonal_size / 2
        if self.center_y > SCREEN_HEIGHT + self.diagonal_size / 2:
            self.center_y = SCREEN_HEIGHT + self.diagonal_size / 2


class Laser(arcade.Sprite):
    # TODO: maybe a list of bullet speeds at different levels
    def __init__(self,  x, y, image=LASER_IMAGE, scale=IMAGE_SCALE,
                 angle=0, speed=200, fade_rate=0):
        super().__init__(filename=image, scale=scale, center_x=x, center_y=y,
                         angle=angle, )

        self.speed = speed

        # Set direction angle
        self.change_x = -math.sin(math.radians(self.angle))
        self.change_y = math.cos(math.radians(self.angle))

        # Bullets start invisible until spawned
        # redundant if not drawing spawning bullets in separate list
        self.visible = True

        # Frames since initialization
        self.frames = 0

        # How quickly the laser should disappear
        self.fade_rate = fade_rate

    def on_update(self, delta_time: float = 1 / 60):
        # used to track when to spawn laser and when it should die
        self.frames += 1
        # Always move in the same direction at the same rate
        self.center_x += self.change_x * self.speed * delta_time
        self.center_y += self.change_y * self.speed * delta_time

        # Fade player_lasers out after firing
        # TODO: Is this an okay use of try-except?
        if self.frames > 60:
            try:
                self.alpha -= self.fade_rate
            except ValueError:
                self.remove_from_sprite_lists()
        elif self.frames > 50:
            self.alpha -= self.fade_rate // 3


class Asteroid(arcade.Sprite):
    # TODO: maybe a list of asteroid speeds at different levels
    def __init__(self, image, scale=IMAGE_SCALE):
        super().__init__(filename=image, scale=scale)

        # Initialize speed to not moving
        self.speed = 0

        # Initialize target point to center of screen
        self.target_x = SCREEN_WIDTH / 2
        self.target_y = SCREEN_HEIGHT / 2

        # TODO: DON'T THINK I NEED THESE HERE -- INHERITED?
        # Amount to change x and y to move in straight line to target
        self.change_x = 0
        self.change_y = 0

        # Set spinning at random rate
        self.change_angle = 0

        # Largest measurement. Used to determine if can be seen offscreen at
        # any angle
        self.diagonal = int((self.width ** 2 + self.height ** 2) ** .5)

        # # Whether visible based on location (not alpha, like visible)
        # self.on_screen = False

    def on_update(self, delta_time: float = 1 / 60):

        # Get x and y distance to target from current position
        x_distance = self.target_x - self.center_x
        y_distance = self.target_y - self.center_y

        # No need to move if already at target point
        if x_distance == 0 and y_distance == 0:
            return

        # Angle between -pi and pi, formed by pos x axis and vector to target
        # Handles situations that would raise ZeroDivisionError with math.tan
        angle_rad = math.atan2(y_distance, x_distance)

        # Since angle's initial side is pos x axis, use normal trig functions
        # to find changes in x and y
        self.change_x = math.cos(angle_rad)
        self.change_y = math.sin(angle_rad)

        # Set new center_x
        # Move to target if within range, otherwise move towards target
        self.change_x *= self.speed * delta_time
        if abs(x_distance) <= self.change_x:
            self.center_x = self.target_x
        else:
            self.center_x += self.change_x

        # Set new center_y
        self.change_y *= self.speed * delta_time
        if abs(y_distance) <= self.change_y:
            self.center_y = self.target_y
        else:
            self.center_y += self.change_y

        # Spin asteroid
        self.angle += self.change_angle

        # # TODO: Is there a way to make this less expensive? seems costly
        # # Set whether or not visible based on location (not alpha)
        # if (self.center_x < -self.diagonal // 2
        #         or self.center_x > SCREEN_WIDTH + self.diagonal // 2):
        #     self.on_screen = False
        # # Only need to check y-based visibility if could be visible based on x
        # elif (self.center_y < -self.diagonal // 2
        #         or self.center_y > SCREEN_HEIGHT + self.diagonal // 2):
        #     self.on_screen = False
        # else:
        #     self.on_screen = True

        # Don't need above code, just check whether target x is same as center
        # Eliminate asteroids once they disappear offscreen
        if self.center_x == self.target_x and self.center_y == self.target_y:
            self.remove_from_sprite_lists()

    # TODO: DELETE (JUST FOR DEBUGGING)
    def __repr__(self):
        return ("Asteroid: center_x = {}, center_y = {}, speed = {}, "
                "target_x = {}, target_y = {}, change_x = {},"
                " change_y = {}".format(self.center_x, self.center_y,
                                        self.speed, self.target_x,
                                        self.target_y, self.change_x,
                                        self.change_y))


class EnemyShip(arcade.Sprite):
    def __init__(self, image, laser_list, scale=IMAGE_SCALE):
        super().__init__(filename=image, scale=scale)

        # Pointer to game window's enemy_laser_list
        self.laser_list = laser_list

        # Laser image
        # TODO: why is this hardcoded when image is a parameter?
        self.laser_image = "spaceshooter/PNG/Lasers/laserRed01.png"

        # TODO: how and when should these be set up? to be flexible
        self.laser_speed = 0    # twice ship speed
        self.reload_time = 0

        # TODO: make setup method to handle this
        # Initialize speed to not moving
        self.speed = 0

        # Initialize target point to center of screen
        self.target_x = SCREEN_WIDTH / 2
        self.target_y = SCREEN_HEIGHT / 2

        # TODO: DON'T THINK I NEED THESE HERE -- INHERITED?
        # Amount to change x and y to move in straight line to target
        self.change_x = 0
        self.change_y = 0

        # Largest measurement. Used to determine if can be seen offscreen at
        # any angle
        self.diagonal = int((self.width ** 2 + self.height ** 2) ** .5)

    def on_update(self, delta_time: float = 1/60):
        # Get x and y distance to target from current position
        x_distance = self.target_x - self.center_x
        y_distance = self.target_y - self.center_y

        # No need to move if already at target point
        if x_distance == 0 and y_distance == 0:
            return

        # Angle between -pi and pi, formed by pos x axis and vector to target
        # Handles situations that would raise ZeroDivisionError with math.tan
        angle_rad = math.atan2(y_distance, x_distance)

        # Set angle of ship to match angle of movement
        # angle_rad is the measured from the positive x axis, but image
        # angles are measured from the positive y axis
        self.angle = math.degrees(angle_rad) + 90

        # Since angle's initial side is pos x axis, use normal trig functions
        # to find changes in x and y
        self.change_x = math.cos(angle_rad)
        self.change_y = math.sin(angle_rad)

        # Set new center_x
        # Move to target if within range, otherwise move towards target
        self.change_x *= self.speed * delta_time
        if abs(x_distance) <= self.change_x:
            self.center_x = self.target_x
        else:
            self.center_x += self.change_x

        # Set new center_y
        self.change_y *= self.speed * delta_time
        if abs(y_distance) <= self.change_y:
            self.center_y = self.target_y
        else:
            self.center_y += self.change_y

        # Periodically shoot at player
        self.reload_time -= 1
        if self.reload_time <= 0:
            # TODO: look through angle stuff to comment here
            # TODO: set speed and fade rate based on level
            self.laser_list.append(Laser(self.center_x, self.center_y,
                                         image=self.laser_image,
                                         angle=self.angle + 180,
                                         speed=self.laser_speed,
                                         fade_rate=20))
            # TODO: fix this...
            self.reload_time = self.laser_speed

    def set_target(self, x, y):
        self.target_x = x
        self.target_y = y


class Explosion(arcade.Sprite):
    def __init__(self, center_x, center_y, scale=1):

        # Initialize from super without images
        super().__init__(center_x=center_x, center_y=center_y, scale=scale)

        # List of textures (frames of an animation; ways the sprite can look)
        self.textures = []

        # Add textures from spritesheet
        # "explosion.png" is 4096x3584, (16x14 grid of 256-sq pixel frames)
        #  last row only has 13 frames
        filename = "explosion.png"

        # Dimensions of each frame to extract
        width = 256
        height = 256

        # 221 frames to extract from sheet
        for i in range(222):

            # coordinates of top-left pixel of section to extract
            # x coordinate changes with every image, cycling over 16 columns
            # in each row
            x = (i % 16) * width

            # y coordinate changes for each row, every 16 images
            y = (i // 16) * height

            self.textures.append(arcade.load_texture(filename, x=x, y=y,
                                                     width=width,
                                                     height=height))

        # Initialize current texture and texture index
        self.cur_texture_index = 0
        self.texture = self.textures[self.cur_texture_index]

    def update(self):
        """
        Animate explosion.
        """
        # Animate explosion
        if self.cur_texture_index < len(self.textures):
            self.texture = self.textures[self.cur_texture_index]
            self.cur_texture_index += 1

        # Remove from lists
        else:
            self.remove_from_sprite_lists()


class MyGameWindow(arcade.Window):
    """
    Extends arcade.Window with specifics for how this game runs. Inherits
    attributes and methods from arcade.Window that make a game possible.
    For example, as a descendent of an arcade.Window, MyGameWindow's on_draw
    and on_update methods automatically get called 60 times per second, which
    enables animation and gameplay.
    """
    def __init__(self, width, height, title):
        """
        Constructor.
        Initializes attributes to None so they're recognized, but calls
        setup() to set their values so as not to repeat code that needs to
        exist in a setup method (to be able to reset at game restart).
        Sets background color, since that only needs to happen once.
        :param width:
        :param height:
        :param title:
        """
        super().__init__(width, height, title)

        arcade.set_background_color((0, 0, 0))

        # Start at level 1
        self.level = 1

        # Start with 0 points
        self.points = 0

        # Lives TODO: IDK if this should go here or in player
        self.lives = 3

        # Player ships to change each level
        self.ships = ["spaceshooter/PNG/Player_ships/playerShip1_blue.png",
                      "spaceshooter/PNG/Player_ships/playerShip2_blue.png",
                      "spaceshooter/PNG/Player_ships/playerShip3_blue.png"]

        # Set up list of images to use for asteroids
        self.asteroid_images = []
        asteroid_base_name = "spaceshooter/PNG/Meteors/meteorBrown_{}.png"
        for i in range(1, 5):
            self.asteroid_images.append(asteroid_base_name.format(
                "big{}".format(i)))
        for i in range(1, 3):
            self.asteroid_images.append(asteroid_base_name.format(
                "med{}".format(i)))
            self.asteroid_images.append(asteroid_base_name.format(
                "small{}".format(i)))
            self.asteroid_images.append(asteroid_base_name.format(
                "tiny{}".format(i)))

        # List of enemy ship images
        self.enemy_ship_images = ["spaceshooter/PNG/Enemies/enemyRed1.png",
                                  "spaceshooter/PNG/Enemies/enemyRed2.png"]

        # TODO: WHY HAVE A PLAYER SPRITE LIST?
        self.player_sprite = None
        self.player_list = None

        self.player_laser_list = None

        self.asteroid_list = None

        self.enemy_list = None
        self.enemy_laser_list = None

        self.explosion_list = None

        # Key press info
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Key press
        self.space_pressed = False
        self.reloading = 0

        self.setup()

    def setup(self):
        """
        Sets or resets game when the window is opened or the game is
        restarted.
        :return: None
        """

        # Set up player
        # Player ship depends upon level
        self.player_sprite = Player(self.ships[self.level - 1])
        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = SCREEN_HEIGHT // 2

        # Set up SpriteLists to take advantage of SpriteList methods and
        # fast batched drawing
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        self.player_laser_list = arcade.SpriteList()

        self.asteroid_list = arcade.SpriteList()

        self.enemy_list = arcade.SpriteList()
        self.enemy_laser_list = arcade.SpriteList()

        self.explosion_list = arcade.SpriteList()

        # TODO: MAKE NUMBER AND SPEED DEPENDENT ON LEVEL
        # Number of asteroids depends upon level
        self.make_asteroids(10, (50, 200))    # TODO: undo numbers

        # Number of asteroids depends upon level
        self.make_enemy_ships(10, (50, 100))

    def make_asteroids(self, num_asteroids, speed_range):

        # TODO: Start them way closer to edge of screen
        for i in range(num_asteroids + 1):
            asteroid = Asteroid(random.choice(self.asteroid_images))

            # TODO: MOVE THIS LATER -- AT END WOULD BE EASIER
            self.asteroid_list.append(asteroid)

            # Get coordinates of random point offscreen by getting a random
            # x and a corresponding y that makes it work
            diagonal = self.asteroid_list[-1].diagonal

            # x can be anywhere in the width of the screen, and a little to
            # the left or right
            x = random.randrange(SCREEN_WIDTH // -2, 3 * SCREEN_WIDTH // 2)

            # If x coordinate is within range of visible x's, place
            # y-coordinate offscreen
            if -diagonal // 2 <= x <= SCREEN_WIDTH + diagonal // 2:

                # Whether y will be above or below screen
                y_sign = random.choice([1, -1])

                # How far away from edge of screen y will be
                y_offset = random.randrange(diagonal, 5 * diagonal)

                # Place y above or below edge of screen
                if y_sign > 0:
                    y = SCREEN_HEIGHT + y_offset
                else:
                    y = -y_offset

            # If x-coordinate is offscreen, place y-coordinate within,
            # range of visible y-coordinates, or a little beyond
            else:
                y = random.randrange(-diagonal, SCREEN_HEIGHT + diagonal)

            # Set coordinates of asteroid
            self.asteroid_list[-1].center_x = x
            self.asteroid_list[-1].center_y = y

            # Set random speed of asteroid within range
            self.asteroid_list[-1].speed = random.randrange(speed_range[0],
                                                            speed_range[1])

            # Set random spin rate for asteroid, avoiding zero
            self.asteroid_list[-1].change_angle = random.randrange(-5, 6, 2)

            # Set random target point for asteroid across screen

            #
            if x < 0:
                target_x = SCREEN_WIDTH + diagonal
            elif x > SCREEN_WIDTH:
                target_x = -diagonal
            else:
                target_x = random.randrange(SCREEN_WIDTH)

            #
            if y < 0:
                target_y = SCREEN_HEIGHT + diagonal
            elif y > SCREEN_HEIGHT:
                target_y = -diagonal
            else:
                target_y = random.randrange(SCREEN_HEIGHT)

            self.asteroid_list[-1].target_x = target_x
            self.asteroid_list[-1].target_y = target_y




    # TODO: THIS IS THE SAME AS MAKE_METEORS SO MAKE AS ONE FUNCTION
    # TODO: make most of this a setup method for sprite
    def make_enemy_ships(self, num_enemies, speed_range):

        # TODO: Start them way closer to edge of screen
        for i in range(num_enemies + 1):
            # Pass laser list to enemy so enemy can fill it
            self.enemy_list.append(EnemyShip(self.enemy_ship_images[0],
                                   self.enemy_laser_list))

            # Get diagonal size of enemy_ship to hide it offscreen
            diagonal = self.enemy_list[-1].diagonal

            # Get coordinates of random point offscreen by getting a random
            # x and a corresponding y that makes it work

            # x can be anywhere in the width of the screen, and a little to
            # the left or right
            x = random.randrange(SCREEN_WIDTH // -2, 3 * SCREEN_WIDTH // 2)

            # If x coordinate is within range of visible x's, place
            # y-coordinate offscreen
            if -diagonal // 2 <= x <= SCREEN_WIDTH + diagonal // 2:

                # Whether y will be above or below screen
                y_sign = random.choice([1, -1])

                # How far away from edge of screen y will be
                y_offset = random.randrange(diagonal, 5 * diagonal)

                # Place y above or below edge of screen
                if y_sign > 0:
                    y = SCREEN_HEIGHT + y_offset
                else:
                    y = -y_offset

            # If x-coordinate is offscreen, place y-coordinate within,
            # range of visible y-coordinates, or a little beyond
            else:
                y = random.randrange(-diagonal, SCREEN_HEIGHT + diagonal)

            # Set coordinates of asteroid
            self.enemy_list[-1].center_x = x
            self.enemy_list[-1].center_y = y

            # Set random speed of asteroid within range
            self.enemy_list[-1].speed = random.randrange(speed_range[0],
                                                         speed_range[1])

            # TODO: CHANGE THIS TO BE BASED ON LEVEL
            self.enemy_list[-1].laser_speed = 3 * self.enemy_list[-1].speed


    def on_draw(self):
        arcade.start_render()

        # Draw player_lasers first so covered by player and look like they're growing
        # out from space ship
        self.player_laser_list.draw()
        self.player_list.draw()

        # Drawing with SpriteList means anything outside the viewport won't
        # be drawn
        self.asteroid_list.draw()

        self.enemy_laser_list.draw()
        self.enemy_list.draw()

        self.explosion_list.draw()

        # Draw writing last so it can be seen
        arcade.draw_text("Points: {}".format(self.points), 20,
                         SCREEN_HEIGHT - 20, font_size=14, bold=True)
        arcade.draw_text("Level: {}".format(self.level), 20,
                         SCREEN_HEIGHT - 50, font_size=14, bold=True)

    def on_update(self, delta_time):
        """
        Main game logic
        :param delta_time:
        :return:
        """

        # Check collisions first because we'll delete sprites based on these
        # collisions and want them to have visually overlapped in the last
        # frame before deleting them. If we deleted them after the other
        # updates, we'd delete based on collisions that hadn't yet been drawn.
        # Additionally, there's no need to move a sprite during this update
        # if we'll also delete it during this update.

        # Check player collisions before player laser collisions so in the
        # case of the player and a laser both hitting a asteroid, the player
        # dies
        # If the player collides with any other sprite, they die
        hits = arcade.check_for_collision_with_lists(self.player_sprite,
                                                     [self.asteroid_list,
                                                      self.enemy_laser_list,
                                                      self.enemy_list])

        if hits:
            # Decrement lives left
            self.lives -= 1
            self.explosion_list.append(Explosion(self.player_sprite.center_x,
                                                 self.player_sprite.center_y))
            # TODO: DEAL WITH PLAYER SPRITE'S CONTINUED EXISTANCE AND LASERS
            #  for lasers, just make them made by the sprite on updates, like movement
            self.player_sprite.remove_from_sprite_lists()
            # TODO: Restart level?
            for hit in hits:
                hit.remove_from_sprite_lists()


        # Check player laser collisions
        # Check asteroids and enemy ships separately to make point assignments
        # easier

        # Check player lasers hitting asteroids
        player_laser_hits = []

        # There's not a method to check for collisions between one Spritelist
        # and one or more others, so must iterate over player_laser_list
        for laser in self.player_laser_list:

            # No good way to break a line that's any longer
            ht = arcade.check_for_collision_with_list(laser,
                                                      self.asteroid_list)
            player_laser_hits += ht

        # Assign points for each asteroid hit
        # TODO: should different amounts be assigned for different sizes?
        #  If so, should different sizes be in different lists?
        self.points += METEOR_POINTS * len(player_laser_hits)

        # Destroy hit asteroids
        # TODO: add explosions and possibly fading debris
        for sprite in player_laser_hits:
            self.explosion_list.append(Explosion(sprite.center_x,
                                                 sprite.center_y))
            sprite.remove_from_sprite_lists()

        # Check player lasers hitting enemy ships
        player_laser_hits = []
        for laser in self.player_laser_list:
            ht = arcade.check_for_collision_with_list(laser, self.enemy_list)
            player_laser_hits += ht

        # Assign points for each enemy hit
        self.points += ENEMY_POINTS * len(player_laser_hits)

        # TODO: Give enemies lives so they don't disappear after one hit
        # Destroy hit enemies
        # TODO: possibly possibly fading debris
        for sprite in player_laser_hits:
            self.explosion_list.append(Explosion(sprite.center_x,
                                                 sprite.center_y))
            sprite.remove_from_sprite_lists()



        # Update player change_movement based on key presses
        # Default to no movement if keys aren't pressed
        self.player_sprite.change_angle = 0
        self.player_sprite.speed = 0

        # TODO: Issue where if L and U are pressed, D won't stop U/D movement

        # If opposite keys are pressed, movement shouldn't occur
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_angle = -self.player_sprite.angle_rate
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_angle = self.player_sprite.angle_rate
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.speed = self.player_sprite.forward_rate
        if self.down_pressed and not self.up_pressed:
            self.player_sprite.speed = -self.player_sprite.forward_rate

        # TODO: Is this the right choice? I think so, since they player
        #  itself can't handle it because of the the key input...or can it?
        #  Figure out how it can...similar to enemy sprite
        # Shoot player_lasers periodically while space is pressed
        self.reloading -= 1
        if self.space_pressed and self.reloading <= 0:
            self.player_laser_list.append(Laser(self.player_sprite.center_x,
                                                self.player_sprite.center_y,
                                                angle=self.player_sprite.angle,
                                                fade_rate=30))
            # Slow enough reload time that player could do it faster by
            # repeatedly hitting space, but fast enough to be fun
            self.reloading = 10

        # TODO: give player pointer to laser list like enemies? no need?

        # Set enemies' new target point as player's current (soon-to-be-old)
        # location
        for enemy in self.enemy_list:
            enemy.set_target(self.player_sprite.center_x,
                             self.player_sprite.center_y)

        self.player_list.on_update(delta_time)
        self.player_laser_list.on_update(delta_time)
        self.asteroid_list.on_update(delta_time)
        self.enemy_list.on_update(delta_time)
        self.enemy_laser_list.on_update(delta_time)

        self.explosion_list.update()

    def on_key_press(self, symbol, modifiers):
        # Gracefully quit program
        if symbol == arcade.key.W and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            arcade.close_window()

        # Restart program
        if symbol == arcade.key.R and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            self.setup()

        if symbol == arcade.key.RIGHT:
            self.right_pressed = True
        if symbol == arcade.key.LEFT:
            self.left_pressed = True
        if symbol == arcade.key.UP:
            self.up_pressed = True
        if symbol == arcade.key.DOWN:
            self.down_pressed = True

        if symbol == arcade.key.SPACE:
            self.space_pressed = True

        # # TODO: DELETE -- JUST USED FOR DEBUGGING
        # if symbol == arcade.key.P:
        #     for asteroid in self.asteroid_list:
        #         # print("{}, {}\n{}, {}\n{}\n".format(asteroid.center_x,
        #         #                                     asteroid.center_y,
        #         #                                     asteroid.target_x,
        #         #                                     asteroid.target_y,
        #         #                                     asteroid.speed))
        #         print(asteroid)
        #     print("-" * 50)

    def on_key_release(self, symbol, modifiers):

        if symbol == arcade.key.RIGHT:
            self.right_pressed = False
        if symbol == arcade.key.LEFT:
            self.left_pressed = False
        if symbol == arcade.key.UP:
            self.up_pressed = False
        if symbol == arcade.key.DOWN:
            self.down_pressed = False

        if symbol == arcade.key.SPACE:
            self.space_pressed = False
            # Reset reloading so repeatedly hitting space gives player
            # potential to shoot faster
            self.reloading = 0






def main():
    """ Main function """
    game = MyGameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()

