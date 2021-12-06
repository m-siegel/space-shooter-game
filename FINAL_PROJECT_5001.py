"""
I-M Siegel

Explosion graphics from https://www.explosiongenerator.com/, via Arcade
resources

Other images from Space Shooter (Redux, plus fonts and sounds) by Kenney
Vleugels (www.kenney.nl), licensed under Creative Commons.
https://kenney.nl/assets/space-shooter-redux




NOTE: HOW THINGS ARE BROKEN DOWN
    - image filenames, scale and window name and dimensions belong in main,
    helper functions and the global variables

    - how each sprite class works, including shooting its lasers, belongs to
    each sprite, general enough that it can get information like that the
    player is trying to shoot (self.shooting) and take care of that, this
    is how movement works.

    - window class is responsible for putting all game logic together,
    interfacing with the user, and communicating settings from file/main to
    the sprites. This includes monitoring for key presses and updating sprite
    attributes based on that, changing levels, determining how many sprites of
    each kind appear and when, and scoring.







Practice:
    Done - moving with angles (eg space ship)
    - colliding sprites with lists (enemies, enemy shooters)
    - disappear (after shot)
    - spawning (already done, but can check how they do)

TODO:
    - add start screen
        - add end screen
    ------------------------------------
    STYLE
        - DEFENSIVE PROGRAMMING (at least in the method params, not name mangling)
        - PEP8 COMPLIANCE
        - general structure
        - COMMENTS
    ------------------------------------
    PRESENTATION
    ------------------------------------
    - change meteors: maybe only big and med ones at .5 scale (maybe small, too)
    - add lives?
    - add damage
    - implement strings???
    - add a compass so player can see where they're facing

DONE:
    - add enemy lasers
    - add collision between player lasers and asteroids, player lasers and
        enemy ships
    - add collision between enemy lasers and player ship
    - add score
    - add explosions
    - clean up (eg basic enemy from which asteroids and enemy ships descend)
    - no filenames or globals hardcoded into classes other than MyGameWindow.
    - figure out why enemy lasers shoot long when they first start
    - differing functions for resetting for new game and resetting for level (eg when points should be reset)
    - add levels and design levels
        - add shortcuts (cmd 1, cmd 2, cmd 3)
    - add sounds
    - type hints
    - __str__ to all
"""


import arcade
import math
import random

from typing import List, Tuple, Union, Optional  # For type hinting

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Space Shooter"

ASTEROID_POINTS = 5
ENEMY_POINTS = 15

# File names for sprites
# Using globals so they're easy to change if someone wants to use different
# images or if the images are stored with a different filepath

# If images come from the same pack of resources, they may be able to scale
# together. In case any need different scaling, each has a global variable
# for its scale. Most are set equal to IMAGE_SCALE, but all can be changed
IMAGE_SCALE = .5

# Player ship filenames (3 strign filenames: one for each level)
PLAYER_SHIPS = ("media/kenney_nl/spaceshooter/PNG/"
                "Player_ships/playerShip1_blue.png",
                "media/kenney_nl/spaceshooter/PNG/"
                "Player_ships/playerShip2_blue.png",
                "media/kenney_nl/spaceshooter/PNG/"
                "Player_ships/playerShip3_blue.png")
# In case image needs unique scaling
PLAYER_SHIP_SCALE = IMAGE_SCALE

# Player laser filename (one string)
PLAYER_LASER = "media/kenney_nl/spaceshooter/PNG/Lasers/laserBlue01.png"
# In case image needs unique scaling
PLAYER_LASER_SCALE = IMAGE_SCALE


# Enemy Ship filenames (2 filename strings: one for each of levels 2 and 3)
ENEMY_SHIPS = ("media/kenney_nl/spaceshooter/PNG/Enemies/enemyRed1.png",
               "media/kenney_nl/spaceshooter/PNG/Enemies/enemyRed2.png")
ENEMY_SHIP_SCALE = IMAGE_SCALE

# Used in main() to get variations on base filename using iteration
# For example, "spaceshooter/PNG/Meteors/meteorBrown_big3.png"
# NOTE: main expects 4 files named big 1-4, 2 files names med, 2 named small,
# and 2 named tiny
ASTEROID_FILENAME_BASE = ("media/kenney_nl/spaceshooter/PNG/"
                          "Meteors/meteorBrown_{}.png")
ASTEROID_SCALE = 1

# Enemy laser filename (one string)
ENEMY_LASER = "media/kenney_nl/spaceshooter/PNG/Lasers/laserRed01.png"
ENEMY_LASER_SCALE = IMAGE_SCALE

# Explosion textures are stored in a grid in a spritesheet
EXPLOSION_FILE = {"filename": "media/explosion.png", "texture_width": 256,
                  "texture_height": 256, "columns": 16,
                  "num_textures": 221}
EXPLOSION_SCALE = 1
# Since the file has so many textures, only include one out of every two
# for a shorter animation
EXPLOSION_SKIP_RATE = 2


# TODO: ASK -- better as a dictionary?
BACKGROUND_SOUND = "media/imovie_sound_effect_space_log.wav"
PLAYER_LASER_SOUND = "media/kenney_nl/sounds/laser2.wav"
ENEMY_LASER_SOUND = "media/kenney_nl/sounds/laser1.mp3"
EXPLOSION_SOUND = "media/kenney_nl/sounds/explosion2.wav"
LEVEL_UP_SOUND = "media/kenney_nl/sounds/upgrade1.wav"
LOST_LIFE_SOUND = "media/kenney_nl/sounds/lose5.wav"
GAME_OVER_SOUND = "media/kenney_nl/sounds/gameover1.wav"
WIN_SOUND = "media/imovie_sound_effects_broadcast_news_short.wav"


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

    # TODO: get speed? for enemies and ateroids, too?
    def __init__(self, image_filename: str, scale: Union[int, float],
                 laser_filename: str, laser_scale: Union[int, float],
                 laser_list: arcade.SpriteList, window_dims: Tuple[int, int],
                 laser_fade_rate: Union[int, float] = 15,
                 laser_sound: Optional[arcade.Sound] = None):
        super().__init__(filename=image_filename, scale=scale)
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

        # Laser settings
        self.laser_list = laser_list

        # How long in updates/frames (1/60 sec) it takes player's lasers to
        # reload and shoot again if player holds down the trigger
        # Slow enough reload time that player could do it faster by
        # repeatedly hitting space, but fast enough to be fun
        self.reload_time = 10

        # Counter counting number of frames since last shot
        self.reload_ticks = 10
        self.laser_filename = laser_filename
        self.laser_scale = laser_scale

        # TODO
        self.laser_fade_rate = laser_fade_rate

        # If the player is trying to shoot now
        self.shooting = False

        self.window_width = window_dims[0]
        self.window_height = window_dims[1]

        self.laser_sound = laser_sound

    # TODO: HOW MUCH SHOULD I DECOMPOSE?
    def on_update(self, delta_time: float = 1 / 60) -> None:
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

        # TODO: NOW TURN AND MOVE
        self.turn_and_move(delta_time)

        # # Update angle player is facing
        # # Multiply by delta_time for smooth movement
        # self.angle += self.change_angle * delta_time
        #
        # # Find change_x and change_y based on new angle (essentially a target
        # # point). Default angle is North, so target point on unit circle
        # # x-coordinate (change_x) is negative sin (not positive cos) and
        # # y-coordinate (change_y) is cos (not sin)
        # self.change_x = -math.sin(math.radians(self.angle))
        # self.change_y = math.cos(math.radians(self.angle))
        #
        # # Move sprite in direction it's facing, as determined above
        # self.center_x += self.change_x * self.speed * delta_time
        # self.center_y += self.change_y * self.speed * delta_time
        #
        # # Let sprite go offscreen so player feels like they can get lost,
        # # but keep sprite from going far so player can bring it back onto
        # # screen immediately
        # if self.center_x < -1 * self.diagonal_size / 2:
        #     self.center_x = -1 * self.diagonal_size / 2
        # if self.center_x > self.window_width + self.diagonal_size / 2:
        #     self.center_x = self.window_width + self.diagonal_size / 2
        # if self.center_y < -1 * self.diagonal_size / 2:
        #     self.center_y = -1 * self.diagonal_size / 2
        # if self.center_y > self.window_height + self.diagonal_size / 2:
        #     self.center_y = self.window_height + self.diagonal_size / 2

        # TODO: NOW, SHOOT LASERS
        self.shoot_lasers()
        # # Shoot lasers
        # if self.shooting and self.reload_ticks <= 0:
        #     self.laser_list.append(Laser(self.center_x, self.center_y,
        #                                  self.laser_filename, self.laser_scale,
        #                                  angle=self.angle,
        #                                  speed=400,    # TODO: variable
        #                                  fade_rate=self.laser_fade_rate,
        #                                  sound=self.laser_sound))
        #     self.reload_ticks = self.reload_time
        # else:
        #     self.reload_ticks -= 1

    def turn_and_move(self, delta_time: float = 1 / 60) -> None:
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
        if self.center_x > self.window_width + self.diagonal_size / 2:
            self.center_x = self.window_width + self.diagonal_size / 2
        if self.center_y < -1 * self.diagonal_size / 2:
            self.center_y = -1 * self.diagonal_size / 2
        if self.center_y > self.window_height + self.diagonal_size / 2:
            self.center_y = self.window_height + self.diagonal_size / 2

    def shoot_lasers(self):
        # Shoot lasers
        if self.shooting and self.reload_ticks <= 0:
            self.laser_list.append(Laser(self.center_x, self.center_y,
                                         self.laser_filename, self.laser_scale,
                                         angle=self.angle,
                                         speed=400,  # TODO: variable
                                         fade_rate=self.laser_fade_rate,
                                         sound=self.laser_sound))
            self.reload_ticks = self.reload_time
        else:
            self.reload_ticks -= 1

    def __str__(self) -> str:
        return ("<Player: center_x = {}, center_y = {}, speed = {}, "
                "angle = {}, change_x = {}, change_y = {}>".format(
                    self.center_x, self.center_y, self.speed, self.angle,
                    self.change_x, self.change_y))


class Laser(arcade.Sprite):
    # TODO: maybe a list of bullet speeds at different levels
    def __init__(self,  x: Union[int, float], y: Union[int, float],
                 image_filename: str, scale: Union[int, float],
                 angle: Union[int, float] = 0, speed: Union[int, float] = 200,
                 fade_rate: Union[int, float] = 0,
                 sound: Optional[arcade.Sound] = None):
        super().__init__(filename=image_filename, scale=scale, center_x=x,
                         center_y=y, angle=angle, )

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

        # Optionally play sound (if one is sent)
        self.sound = sound
        self.player = None
        if self.sound:
            self.player = sound.play()

    def on_update(self, delta_time: float = 1 / 60) -> None:
        # used to track when to spawn laser and when it should die
        self.frames += 1
        # Always move in the same direction at the same rate
        self.center_x += self.change_x * self.speed * delta_time
        self.center_y += self.change_y * self.speed * delta_time

        # Remove very faint lasers
        # (feels weird to destroy an obstacle with invisible laser)
        if self.alpha <= 20:
            self.remove_from_sprite_lists()

        # Fade player_lasers out after firing
        if self.frames > 60:
            try:
                self.alpha -= self.fade_rate
            except ValueError:
                self.remove_from_sprite_lists()
        elif self.frames > 50:
            try:
                self.alpha -= self.fade_rate // 3
            except ValueError:
                self.remove_from_sprite_lists()

    def __str__(self) -> str:
        return ("<Laser: center_x = {}, center_y = {}, speed = {}, "
                "change_x = {}, change_y = {}, fade_rate = {}>".format(
                    self.center_x, self.center_y, self.speed, self.change_x,
                    self.change_y, self.fade_rate))


class TargetingSprite(arcade.Sprite):
    def __init__(self, image_filename: str, scale: Union[int, float],
                 target_x: Union[int, float] = 0,
                 target_y: Union[int, float] = 0):
        super().__init__(filename=image_filename, scale=scale)

        # Initialize speed to not moving
        self.speed = 0

        # Initialize target point to center of screen
        self.target_x = target_x
        self.target_y = target_y

        # TODO: DON'T THINK I NEED THESE HERE -- INHERITED?
        # Amount to change x and y to move in straight line to target
        self.change_x = 0
        self.change_y = 0

        # Largest measurement. Used to determine if can be seen offscreen at
        # any angle
        self.diagonal = int((self.width ** 2 + self.height ** 2) ** .5)

    def on_update(self, delta_time: float = 1 / 60) -> float:
        # Get x and y distance to target from current position
        x_distance = self.target_x - self.center_x
        y_distance = self.target_y - self.center_y

        # Only move if not already at target point
        if x_distance != 0 or y_distance != 0:

            # Angle between -pi and pi, formed by pos x axis and vector to
            # target. Handles situations that would raise ZeroDivisionError
            # with math.tan
            angle_rad = math.atan2(y_distance, x_distance)

            # Arcade's sprite has methods to do something similar to this
            # (getting the change in x and y from the angle and updating
            # sprite's position), but it doesn't factor in delta_time

            # Since angle's initial side is pos x axis, use normal trig
            # functions to find changes in x and y per unit of 1
            self.change_x = math.cos(angle_rad)
            self.change_y = math.sin(angle_rad)

            # Find changes in x and y in terms of speed and delta time
            self.change_x *= self.speed * delta_time
            self.change_y *= self.speed * delta_time

        else:
            angle_rad = math.radians(self.angle - 90)

        # Set new center_x
        # Move to target if within range, otherwise move towards target
        if abs(x_distance) <= self.change_x:
            self.center_x = self.target_x
        else:
            self.center_x += self.change_x

        # Set new center_y
        if abs(y_distance) <= self.change_y:
            self.center_y = self.target_y
        else:
            self.center_y += self.change_y

        # TODO: this is to support EnemyShip's movement
        return angle_rad

    # TODO: unique to EnemyShip, but okay for both to have, necessary to neither
    def set_target(self, x: Union[int, float], y: Union[int, float]) -> None:
        self.target_x = x
        self.target_y = y

    def set_random_offscreen_location(self, screen_width: int,
                                      screen_height: int) -> None:
        # Get coordinates of random point offscreen by getting a random
        # x and a corresponding y that makes it work

        # x can be anywhere in the width of the screen, and a little to
        # the left or right
        x = random.randrange(screen_width // -2, 3 * screen_height // 2)

        # If x coordinate is within range of visible x's, place
        # y-coordinate offscreen
        if -self.diagonal // 2 <= x <= screen_width + self.diagonal // 2:

            # Whether y will be above or below screen
            y_sign = random.choice([1, -1])

            # How far away from edge of screen y will be
            y_offset = random.randrange(self.diagonal, 5 * self.diagonal)

            # Place y above or below edge of screen
            if y_sign > 0:
                y = screen_height + y_offset
            else:
                y = -y_offset

        # If x-coordinate is offscreen, place y-coordinate within,
        # range of visible y-coordinates, or a little beyond
        else:
            y = random.randrange(-self.diagonal, screen_height + self.diagonal)

        self.center_x = x
        self.center_y = y

    def set_speed_in_range(self,
                           speed_range: Union[Tuple[int, int],
                                              Tuple[int, int, int]]) -> None:

        # Validate parameters
        if not isinstance(speed_range, tuple):
            raise TypeError("Speed range must be a 2- or 3-tuple")
        if not 2 <= len(speed_range) <= 3:
            raise ValueError("Speed range must have length 2 or 3")
        for num in speed_range:
            if not isinstance(num, int):
                raise TypeError("Speed range's elements must be integers")

        # Set step
        if len(speed_range) == 2:
            step = 1
        else:
            step = speed_range[2]

        # TODO speed range (0, 0) or any single int, just make that the speed
        self.speed = random.randrange(speed_range[0], speed_range[1], step)

    # TODO: currently only used for Asteroid, but doesn't hurt to have for all
    def set_random_spin(self, speed_range: tuple = (-5, 6, 2)) -> None:
        # Validate parameters
        if not isinstance(speed_range, tuple):
            raise TypeError("Speed range must be a 2- or 3-tuple")
        if not 2 <= len(speed_range) <= 3:
            raise ValueError("Speed range must have length 2 or 3")
        for num in speed_range:
            if not isinstance(num, int):
                raise TypeError("Speed range's elements must be integers")

        # Set step
        if len(speed_range) == 2:
            step = 1
        else:
            step = speed_range[2]

        self.change_angle = random.randrange(speed_range[0], speed_range[1],
                                             step)

    # TODO: currently only used for Asteroid, but doesn't hurt to have for all
    def set_random_cross_screen_target(self, screen_width: int,
                                       screen_height: int) -> None:
        if self.center_x < 0:
            self.target_x = screen_width + self.diagonal
        elif self.center_x > screen_width:
            self.target_x = -self.diagonal
        else:
            self.target_x = random.randrange(screen_width)

        if self.center_y < 0:
            self.target_y = screen_height + self.diagonal
        elif self.center_y > screen_height:
            self.target_y = -self.diagonal
        else:
            self.target_y = random.randrange(screen_height)

    def __str__(self) -> str:
        return ("<TargetingSprite: center_x = {}, center_y = {}, speed = {}, "
                "target_x = {}, target_y = {}, change_x = {},"
                " change_y = {}>".format(self.center_x, self.center_y,
                                         self.speed, self.target_x,
                                         self.target_y, self.change_x,
                                         self.change_y))


class Asteroid(TargetingSprite):
    # TODO: what if initialized without image so random one could be chosen in
    #  setup? Or, could random one be chosen here and then super's init called?
    #  Could the list of meteor images be a class variable first? Or global?
    def __init__(self, image_filename: str, scale: Union[int, float]):
        super().__init__(image_filename, scale)

        # TODO: don't think is necessary since sprite has
        # Set spinning at random rate
        self.change_angle = 0

    def on_update(self, delta_time: float = 1 / 60) -> None:
        super().on_update(delta_time)

        # Spin asteroid
        self.angle += self.change_angle

        # Eliminate asteroids once they disappear offscreen (reach target)
        if self.center_x == self.target_x and self.center_y == self.target_y:
            self.remove_from_sprite_lists()

    def __str__(self) -> str:
        return ("<Asteroid: center_x = {}, center_y = {}, speed = {}, "
                "target_x = {}, target_y = {}, change_x = {},"
                " change_y = {}>".format(self.center_x, self.center_y,
                                         self.speed, self.target_x,
                                         self.target_y, self.change_x,
                                         self.change_y))


class EnemyShip(TargetingSprite):
    def __init__(self, image_filename: str, scale: Union[int, float],
                 laser_filename: str, laser_scale: Union[int, float],
                 laser_list: arcade.SpriteList,
                 laser_fade_rate: Union[int, float] = 40,
                 reload_time: int = 10,
                 laser_sound: Optional[arcade.Sound] = None):
        # TODO: commentary on why inheriting from BasicEnemy?
        super().__init__(image_filename, scale)

        # Pointer to game window's enemy_laser_list
        self.laser_list = laser_list

        # Laser image
        self.laser_filename = laser_filename
        self.laser_scale = laser_scale
        self.laser_fade_rate = laser_fade_rate

        # TODO: how and when should these be set up? to be flexible
        self.laser_speed = 0  # twice ship speed

        # Ships should be able to shoot the moment they're created
        self.reload_time = reload_time + 10

        self.laser_sound = laser_sound

    def on_update(self, delta_time: float = 1 / 60) -> None:
        # Moves sprite towards target point at speed, returns angle to target
        angle_rad = super().on_update(delta_time)  # TODO: is the argument necessary?

        # Set angle of ship to match angle of movement
        # angle_rad is the measured from the positive x axis, but image
        # initially faces down
        self.angle = math.degrees(angle_rad) + 90

        # Periodically shoot at player
        self.reload_time -= 1
        if self.reload_time <= 0:
            # TODO: look through angle stuff to comment here -- space ship
            #  initial angle is south, but laser's is North, so + 180?
            # TODO: set speed and fade rate based on level
            self.laser_list.append(Laser(self.center_x, self.center_y,
                                         self.laser_filename,
                                         self.laser_scale,
                                         angle=self.angle + 180,
                                         speed=self.laser_speed,
                                         fade_rate=self.laser_fade_rate,
                                         sound=self.laser_sound))
            # TODO: fix this...
            self.reload_time = self.laser_speed

    def __str__(self) -> str:
        return ("<EnemyShip: center_x = {}, center_y = {}, speed = {}, "
                "target_x = {}, target_y = {}, change_x = {},"
                " change_y = {}, laser_speed = {}, reload_time = {}>".format(
                    self.center_x, self.center_y, self.speed, self.target_x,
                    self.target_y, self.change_x, self.change_y,
                    self.laser_speed, self.reload_time))


class Explosion(arcade.Sprite):
    """
    Creates a sprite and animates it once in place with textures, then
    disappears.
    """
    def __init__(self, textures: List[arcade.Texture],
                 center_x: Union[int, float], center_y: Union[int, float],
                 scale: Union[int, float] = 1,
                 sound: Optional[arcade.Sound] = None):

        # Initialize from super without images
        super().__init__(center_x=center_x, center_y=center_y, scale=scale)

        self.textures = textures

        # Initialize current texture and texture index
        self.cur_texture_index = 0
        self.texture = self.textures[self.cur_texture_index]

        # Optionally play sound (if one is sent)
        self.sound = sound
        self.player = None
        if self.sound:
            self.player = sound.play()

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

    def __str__(self) -> str:
        return ("<Explosion: center_x = {}, center_y = {},"
                "number of textures = {}>".format(self.center_x, self.center_y,
                                                  len(self.textures)))


class FadingView(arcade.View):
    def __init__(self, fade_rate: int, alpha: int):
        super().__init__()

        self.alpha = alpha
        self.fade_rate = fade_rate

    def fade_in(self):
        self.alpha += self.fade_rate
        if self.alpha >= 255:
            self.alpha = 255
            return True
        else:
            return False

    def fade_out(self):
        self.alpha -= self.fade_rate
        if self.alpha <= 0:
            self.alpha = 0
            return True
        else:
            return False


class TitleView(FadingView):
    def __init__(self, game_view):
        super().__init__(5, 0)

        arcade.set_background_color((0, 0, 0))

        self.game_view = game_view

        self.title_text = "Spin\n&\nShoot"

        self.faded_in = False
        self.pause_count = 60
        self.faded_out = False

        self.bg_colors = ((0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0))
        self.bg_points = ((0, 0), (self.window.width, 0),
                          (self.window.width, self.window.height),
                          (0, self.window.height))

    def on_update(self, delta_time: float = 1 / 60):
        if self.faded_out:
            instructions = InstructionsView(self.game_view)
            self.window.show_view(instructions)
        if not self.faded_in:
            self.faded_in = self.fade_in()
        elif self.pause_count == 0:
            self.faded_out = self.fade_out()
        else:
            self.pause_count -= 1

    def on_draw(self):
        arcade.start_render()

        green = (27, 160, 62, self.alpha)
        black = (0, 0, 0, self.alpha)
        blue = (0, 0, 205, self.alpha)
        self.bg_colors = (black, blue, black, green)
        background = arcade.create_rectangle_filled_with_colors(self.bg_points,
                                                                self.bg_colors)

        background.draw()

        arcade.draw_text(self.title_text, self.window.width / 2,
                         self.window.height / 2, (255, 255, 255, self.alpha),
                         anchor_x="center", anchor_y="center",
                         font_size=80, align="center", bold=True,
                         width=self.window.width, multiline=True)


class InstructionsView(FadingView):
    def __init__(self, game_view):
        super().__init__(5, 0)

        arcade.set_background_color((0, 0, 0))

        self.game_view = game_view

        self.title_text = ("INSTRUCTIONS:"
                           "\n\n\nShoot the asteroids and enemies without"
                           " getting shot"
                           "\n\n\nMove forward and backward with up and down "
                           "arrows"
                           "\n\nSpin left and right with left and right arrows"
                           "\n\nShoot with the space bar"
                           "\n\n\nPause with 'cmd + t' or 'ctrl + t'"
                           "\n\nRestart with 'cmd + r' or 'ctrl + r'"
                           "\n\nExit with 'cmd + w' or 'ctrl + w'"
                           "\n\n\nPress space to start")

        self.faded_in = False

        self.bg_colors = ((0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0))
        self.bg_points = ((0, 0), (self.window.width, 0),
                          (self.window.width, self.window.height),
                          (0, self.window.height))

    def on_update(self, delta_time: float = 1 / 60):
        if not self.faded_in:
            self.faded_in = self.fade_in()

    def on_draw(self):
        arcade.start_render()

        purple = (65, 44, 129, self.alpha)
        black = (0, 0, 0, self.alpha)
        blue = (0, 0, 205, self.alpha)
        self.bg_colors = (black, purple, black, blue)
        background = arcade.create_rectangle_filled_with_colors(self.bg_points,
                                                                self.bg_colors)

        background.draw()

        arcade.draw_text(self.title_text, self.window.width / 2,
                         self.window.height / 2, (255, 255, 255, self.alpha),
                         anchor_x="center", anchor_y="center",
                         font_size=20, align="center", bold=True,
                         width=self.window.width, multiline=True)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            self.window.show_view(self.game_view)


# Main game logic
class GameView(arcade.View):
    """
    Extends arcade.Window with specifics for how this game runs. Inherits
    attributes and methods from arcade.Window that make a game possible.
    For example, as a descendent of an arcade.Window, MyGameWindow's on_draw
    and on_update methods automatically get called 60 times per second, which
    enables animation and gameplay.
    """
    # TODO: Install Python 3.10 after semester; allows for writing
    #  Union[int, float] as int | float
    def __init__(self, explosion_textures: Tuple[List[arcade.Texture],
                                           Union[int, float]],
                 player_ship_image_files: Tuple[Tuple[str, str, str],
                                                Union[int, float]],
                 player_laser_image_file: Tuple[str, Union[int, float]],
                 enemy_ship_image_files: Tuple[Tuple[str, str],
                                               Union[int, float]],
                 enemy_laser_image_file: Tuple[str, Union[int, float]],
                 asteroid_image_files: Tuple[List[str], Union[int, float]],
                 background_music: str, player_laser_sound: str,
                 enemy_laser_sound: str, explosion_sound: str,
                 level_up_sound: str, lost_life_sound: str,
                 win_sound: str, game_over_sound: str):
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
        super().__init__()

        arcade.set_background_color((0, 0, 0))

        # Window dimensions
        self.width = self.window.width
        self.height = self.window.height

        # Used for indexing, so start at zero
        self.level = 0

        # Start with 0 points
        self.points = 0

        # Lives
        self.lives = 3

        # Whether the player has won
        self.won = False

        # Exception will be thrown if there's an attempt to update this
        # before setup() is called. That is intentional
        self.updates_this_level = None

        # Store all sprite image and scale data
        # Pre-loaded list of arcade.Textures for explosion sprite
        self.explosion_textures = explosion_textures[0]
        self.explosion_image_scale = explosion_textures[1]

        # Filenames and scale for sprite images
        self.player_ship_filenames = player_ship_image_files[0]
        self.player_ship_image_scale = player_ship_image_files[1]

        self.player_laser_filename = player_laser_image_file[0]
        self.player_laser_image_scale = player_laser_image_file[1]

        self.enemy_ship_filenames = enemy_ship_image_files[0]
        self.enemy_ship_image_scale = enemy_ship_image_files[1]

        self.enemy_laser_filename = enemy_laser_image_file[0]
        self.enemy_laser_image_scale = enemy_laser_image_file[1]

        self.asteroid_filenames = asteroid_image_files[0]
        self.asteroid_image_scale = asteroid_image_files[1]

        # Load sounds
        self.background_music_sound = arcade.load_sound(background_music)
        self.background_music_player = None    # Necessary to stop playing

        self.player_laser_sound = arcade.load_sound(player_laser_sound)
        # Not needed; don't do check if sound is playing or stop it
        self.player_laser_player = None

        self.enemy_laser_sound = arcade.load_sound(enemy_laser_sound)
        # Not needed; don't do check if sound is playing or stop it
        self.enemy_laser_player = None

        # TODO: maybe stop playing this (if setup() is called,
        #  game ends or player wins)
        self.explosion_sound = arcade.load_sound(explosion_sound)
        # Not needed; don't do check if sound is playing or stop it
        self.explosion_player = None

        # TODO: maybe stop playing this (if lose life is called)
        self.level_up_sound = arcade.load_sound(level_up_sound)
        # Not needed; don't do check if sound is playing or stop it
        self.level_up_player = None

        self.lost_life_sound = arcade.load_sound(lost_life_sound)
        # Not needed; don't do check if sound is playing or stop it
        self.lost_life_player = None

        self.win_sound = arcade.load_sound(win_sound)
        # TODO: is this needed?
        self.win_player = None

        # TODO: maybe stop playing this (if setup() is called)
        self.game_over_sound = arcade.load_sound(game_over_sound)
        # Not needed; don't do check if sound is playing or stop it
        self.game_over_player = None

        # Key press info
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.space_pressed = False

        # TODO: should these be stored directly as attributes at the start of
        #  the level so less work has to be done checking level updates vs
        #  spawn rate, etc?

        # Game level settings store specific settings (which ship image to
        # use, how many asteroids or enemies to have, etc.)
        # These can be easily changed to alter level feel or difficulty
        self.level_settings = {
            'points goal': (100, 200, 300),
            'player ship': self.player_ship_filenames,
            'player laser fade': (15, 15, 15),
            # Keep same enemy ships for first two levels
            'enemy ship': (self.enemy_ship_filenames[0],
                           self.enemy_ship_filenames[0],
                           self.enemy_ship_filenames[1]),
            'starting enemies': (0, 10, 5),
            'enemy spawn rate': (0, .5, .5),  # per second
            'enemy speed range': ((50, 100), (30, 80), (80, 130)),
            # TODO: change to distance-based -- right now there's something with max()
            'enemy laser fade': (255, 40, 40),  # per frames
            'enemy laser reload': (10, 10, 10),
            'starting asteroids': (10, 0, 10),
            'asteroid spawn rate': (1, 0, 1),
            'asteroid speed range': ((50, 200), (50, 200), (100, 200))}

        self.asteroids_spawning = None
        self.enemies_spawning = None

        # These are set up later in setup() because they're reset at each
        # death or new level
        # TODO: WHY HAVE A PLAYER SPRITE LIST?
        # Player sprite
        self.player_sprite = None

        # Sprite lists for each group of sprites
        self.player_list = None
        self.player_laser_list = None

        self.asteroid_list = None

        self.enemy_list = None
        self.enemy_laser_list = None

        self.explosion_list = None

        # TODO: initial setup vs reset at death or new level
        self.setup()

    def setup(self) -> None:
        """
        Sets or resets game when the window is opened or the game is
        restarted.
        :return: None
        """

        # Number of updates since level started
        self.updates_this_level = 0

        # TODO: If playing any other sounds (esp game over or game won, stop)

        # Start background sound. stop any previously playing background sound
        if (self.background_music_player
                and self.background_music_sound.is_playing(
                    self.background_music_player)):
            self.background_music_sound.stop(self.background_music_player)

        self.background_music_player = self.background_music_sound.play(
            loop=True)

        # TODO: for debugging
        # if self.level > 0:
        #     self.background_music_sound.stop(self.background_music_player)

        # TODO: keep or remove?
        level = self.level

        # Set number of updates before new asteroid or enemy is spawned
        # 60 updates per second TODO: change to self.update_rate as parameter
        # TODO better way to handle whether asteroids etc in level
        if self.level_settings['starting asteroids'][level] > 0:
            self.asteroids_spawning = 60 // self.level_settings[
                'asteroid spawn rate'][level]
        if self.level_settings['starting enemies'][level] > 0:
            self.enemies_spawning = 60 // self.level_settings[
                'enemy spawn rate'][level]

        # Set up laser lists first because they need to be passed to player
        # and enemy sprites
        self.player_laser_list = arcade.SpriteList()
        self.enemy_laser_list = arcade.SpriteList()

        # Set up other sprite lists so sprites can be added to them
        # SpriteLists have useful methods like draw() for fast batched drawing
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.asteroid_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()

        # Set up player sprite and append to list
        # Player ship depends upon level
        # PyCharm is confused by this first element because it comes from
        # a dictionary whose first value is a tuple of ints and PyCharm thinks
        # all values from that dict are int tuples, but this is a string
        self.player_sprite = Player(self.level_settings['player ship'][level],
                                    self.player_ship_image_scale,
                                    self.player_laser_filename,
                                    self.player_laser_image_scale,
                                    self.player_laser_list,
                                    (self.width, self.height),
                                    laser_fade_rate=self.level_settings[
                                        'player laser fade'][level],
                                    laser_sound=self.player_laser_sound)

        self.player_sprite.center_x = self.width // 2
        self.player_sprite.center_y = self.height // 2

        # Though the player_list only holds one sprite, using a spritelist
        # instead of the sprite itself for updating and drawing means that
        # MyGameWindow can have a player_sprite attribute without it getting
        # drawn or updated (eg after the player dies) if the sprite is just
        # removed from the list
        self.player_list.append(self.player_sprite)

        # TODO: MAKE NUMBER AND SPEED DEPENDENT ON LEVEL
        # Number of asteroids depends upon level
        self.make_asteroids(self.level_settings['starting asteroids'][level],
                            self.level_settings['asteroid speed range'][level])

        # Number of asteroids depends upon level
        self.make_enemy_ships(self.level_settings['starting enemies'][level],
                              self.level_settings['enemy speed range'][level])

    def make_asteroids(self, num_asteroids: int,
                       speed_range: Union[Tuple[int, int],
                                          Tuple[int, int, int]]) -> None:

        # TODO speed range (0, 0) or any single int, just make that the speed
        for i in range(num_asteroids):
            asteroid = Asteroid(random.choice(self.asteroid_filenames),
                                self.asteroid_image_scale)

            asteroid.set_random_offscreen_location(self.width, self.height)

            # Todo: base on level
            asteroid.set_speed_in_range(speed_range)

            asteroid.set_random_spin()

            # Set random target point for asteroid across screen
            asteroid.set_random_cross_screen_target(self.width, self.height)

            self.asteroid_list.append(asteroid)

    def make_enemy_ships(self, num_enemies: int,
                         speed_range: Union[Tuple[int, int],
                                            Tuple[int, int, int]]) -> None:

        # TODO speed range (0, 0) or any single int, just make that the speed
        for i in range(num_enemies):
            # Pass laser list to enemy so enemy can fill it
            # Use the first image for levels 1 and 2, then switch for level 3
            enemy = EnemyShip(self.level_settings['enemy ship'][self.level],
                              self.enemy_ship_image_scale,
                              self.enemy_laser_filename,
                              self.enemy_laser_image_scale,
                              self.enemy_laser_list,
                              laser_fade_rate=self.level_settings[
                                  'enemy laser fade'][self.level],
                              reload_time=self.level_settings[
                                  'enemy laser reload'][self.level],
                              laser_sound=self.enemy_laser_sound)

            # TODO: Give enemy lasers slower fade rate for higher level

            enemy.set_random_offscreen_location(self.width, self.height)

            # Todo: base on level
            enemy.set_speed_in_range(speed_range)

            enemy.laser_speed = max(3 * enemy.speed, 50)

            self.enemy_list.append(enemy)

    # TODO: I THINK these and other window methods return None since I don't
    #  return anything, but I also don't call them, so I'm not entirely sure
    def on_draw(self) -> None:

        # This clears the screen for the following drawings to work
        arcade.start_render()

        # Drawing with SpriteList means anything outside the viewport won't
        # be drawn
        # Put asteroids in the background
        self.asteroid_list.draw()

        # Draw lasers before ships so lasers are covered by ships and look
        # like they're growing out from the space ships
        self.player_laser_list.draw()
        self.enemy_laser_list.draw()

        # Draw space ships above their lasers
        self.enemy_list.draw()

        # Draw player in front of enemies, asteroids and lasers
        self.player_list.draw()

        # Draw explosions in front of all other sprites
        self.explosion_list.draw()

        # Draw writing last so it can be seen in front of everything
        arcade.draw_text("Points: {}".format(self.points), 20,
                         self.height - 30, font_size=14, bold=True)
        arcade.draw_text("Level: {}".format(self.level + 1), 20,
                         self.height - 60, font_size=14, bold=True)
        arcade.draw_text("Extra Lives: {}".format(self.lives), 20,
                         self.height - 90, font_size=14, bold=True)

    def on_update(self, delta_time):    # Super's signature doesn't type hint
        """
        Main game logic
        """

        # TODO if not self.game_over and not self.game_won:

        # Check whether or not the player should level up and whether or not
        # they die before anything else because if either happens, everything
        # else gets reset and there's no point in updating movement that will get
        # reset

        # Do first so if player gets enough points to win as they get killed, they
        # still win
        self.update_level_based_on_points()

        # Check player collisions before player laser collisions so in the
        # case of the player and a laser both hitting a asteroid, the player
        # dies
        self.update_lives_based_on_hits()

        # Increment count of updates this level after level_up_if_points()
        # that calls setup, which returns to it, which returns to on_update, which
        # then continues, and we want to count this update
        self.updates_this_level += 1

        # Check collisions

        # TODO: Less verbose: Check collisions before moving sprites so on_draw
        #  (and the player seeing sprite positions) happens between sprites hitting
        #  each other and getting deleted. Otherwise, sprites could be deleted
        #  based on their new positions without those positions ever being drawn

        # Check collisions before moving sprits because we'll delete sprites based
        # on these collisions and want them to have visually overlapped in the
        # last frame before deleting them. If we deleted them after the other
        # updates, we'd delete based on collisions that hadn't yet been drawn.
        # Additionally, there's no need to move a sprite during this update
        # if we'll also delete it during this update.
        self.update_points_based_on_strikes()

        # player-dictated actions
        self.update_player_sprite_based_on_input()

        # Refill obstacles
        self.refill_asteroids_and_enemies()

        # Set targets for enemy sprites
        self.set_targets_for_enemies()

        # Update all sprite lists
        self.player_list.on_update(delta_time)
        self.player_laser_list.on_update(delta_time)
        self.asteroid_list.on_update(delta_time)
        self.enemy_list.on_update(delta_time)
        self.enemy_laser_list.on_update(delta_time)
        self.explosion_list.update()

    def update_level_based_on_points(self) -> None:
        # If points goal reached for this level, jump to the next one
        if self.points >= self.level_settings['points goal'][self.level]:
            if self.level <= 1:
                self.level += 1
                self.level_up_sound.play()
                self.setup()
            else:
                # TODO: ending screen and STOP ALL ELSE FOR WINNING maybe
                self.background_music_sound.stop(self.background_music_player)
                if not self.won:
                    self.win_sound.play()  # TODO figure this out -- seems to avoid pyglet error
                    self.won = True
                    won_view = GameWonView()
                    self.window.show_view(won_view)

    def update_lives_based_on_hits(self):
        # If the player collides with any other sprite, they die
        # Use sprite list to check instead of self.player_sprite so that
        # collisions don't get checked if player dies and is removed from list
        hits = []
        for player in self.player_list:
            h = arcade.check_for_collision_with_lists(player,
                                                      [self.asteroid_list,
                                                       self.enemy_laser_list,
                                                       self.enemy_list])
            hits += h

        if hits:
            # TODO: pause before restarting... self.dead = False, if self.dead
            #  or if self.dead > 0: self.dead -= 1, return...gives time for
            #  explosion and sound to play before restart (60 ticks?)
            # Decrement lives left
            self.lives -= 1
            self.explosion_list.append(Explosion(self.explosion_textures,
                                                 self.player_sprite.center_x,
                                                 self.player_sprite.center_y,
                                                 self.explosion_image_scale,
                                                 self.explosion_sound))

            # TODO: call setup and return early

            self.player_sprite.remove_from_sprite_lists()

            # If lives left, restart level
            if self.lives >= 0:
                self.lost_life_sound.play()

                # Don't reset points -- or I can't pass level 2
                # Reset points to minimum to enter this level
                # if self.level >= 1:
                #     this = self.level_settings['points goal'][self.level]
                #     last = self.level_settings['points goal'][self.level - 1]
                #     self.points = this - last
                # else:
                #     self.points = 0

                self.setup()

            # If out of lives go to ending screen
            else:
                self.game_over_sound.play()
                game_lost_view = GameLostView()
                self.window.show_view(game_lost_view)

            # TODO: Restart level? THIS ISN'T NECESSARY SINCE CALLING SETUP
            for hit in hits:
                hit.remove_from_sprite_lists()

    def update_points_based_on_strikes(self):
        # Check player laser collisions
        # Lists to track hit asteroids and enemies separately for scoring
        asteroids_hit = []
        enemies_hit = []

        # There's not a method to check for collisions between one Spritelist
        # and one or more others, so must iterate over player_laser_list

        # Iterate backwards over list of lasers to avoid IndexErrors as lasers
        # are removed
        for i in range(len(self.player_laser_list) - 1, -1, -1):

            # Get asteroids this laser has collided with
            a = arcade.check_for_collision_with_list(self.player_laser_list[i],
                                                     self.asteroid_list)

            # Get enemies this laser has collided with
            e = arcade.check_for_collision_with_list(self.player_laser_list[i],
                                                     self.enemy_list)

            # Remove laser if it hit anything
            if a or e:
                self.player_laser_list[i].remove_from_sprite_lists()

                # Add these hit ateroids and enemies to lists of all hit asteroids
                # and enemies
                asteroids_hit += a
                enemies_hit += e

        # Add points for each hit
        # TODO: should different sizes earn different points?
        #  Using generator or list comprehension (https://docs.python.org/3/tutorial/classes.html)
        self.points += ASTEROID_POINTS * len(asteroids_hit)
        self.points += ENEMY_POINTS * len(enemies_hit)

        # TODO: Make function to remove and do explosions
        #  def destroy(sprites_lst):
        #      for sprite in sprites_lst:
        #          self.explosion_list.append(Explosion(sprite.center_x,
        #                                          sprite.center_y))
        #          sprite.remove_from_sprite_lists()
        # Remove hit sprites
        for asteroid in asteroids_hit:
            self.explosion_list.append(Explosion(self.explosion_textures,
                                                 asteroid.center_x,
                                                 asteroid.center_y,
                                                 self.explosion_image_scale,
                                                 self.explosion_sound))
            asteroid.remove_from_sprite_lists()
        for enemy in enemies_hit:
            self.explosion_list.append(Explosion(self.explosion_textures,
                                                 enemy.center_x,
                                                 enemy.center_y,
                                                 self.explosion_image_scale,
                                                 self.explosion_sound))
            enemy.remove_from_sprite_lists()

    def update_player_sprite_based_on_input(self):
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

        # Update player sprite's shooting attribute to match whether space
        # is pressed
        self.player_sprite.shooting = self.space_pressed

        # TODO: could this be more generic and reused for both?

    def refill_asteroids_and_enemies(self):
        # If there are asteroids or enemies on level, add new ones on interval
        if self.level_settings['starting asteroids'][self.level] > 0:
            if self.asteroids_spawning > 0:
                self.asteroids_spawning -= 1
            else:
                self.make_asteroids(1,
                                    self.level_settings[  # PyCharm's confused
                                        'asteroid speed range'][self.level])
                self.asteroids_spawning = 60 // self.level_settings[
                    'asteroid spawn rate'][self.level]
        if self.level_settings['starting enemies'][self.level] > 0:
            if self.enemies_spawning > 0:
                self.enemies_spawning -= 1
            else:
                self.make_enemy_ships(1,
                                      self.level_settings[  # PyCharm's confused
                                          'enemy speed range'][self.level])
                self.enemies_spawning = 60 // self.level_settings[
                    'enemy spawn rate'][self.level]

    def set_targets_for_enemies(self):
        # Set enemies' new target point as player's current (soon-to-be-old)
        # location
        if len(self.player_list) >= 1:
            for enemy in self.enemy_list:
                enemy.set_target(self.player_sprite.center_x,
                                 self.player_sprite.center_y)
        # If player has been removed from list (been killed), set enemies'
        # targets to random points offscreen
        # else:
        #     for enemy in self.enemy_list:
        #         enemy.set_target(enemy.center_x, enemy.center_y)
        # TODO: change sprite so if there's no target, they just keep going
        #  and then here set angle 180 of current and remove target

    # TODO: Not sure about return vals....
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        # Gracefully quit program
        if symbol == arcade.key.W and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            arcade.close_window()

        # Restart program, TODO also reset to level 1
        if symbol == arcade.key.R and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            self.points = 0
            self.level = 0
            self.setup()

        # Pause game
        if symbol == arcade.key.T and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            game = GameView()
            self.window.show_view(game)

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

        # For "cheating," jumping to a different level with full lives and
        # necessary points
        if symbol == arcade.key.KEY_1 and modifiers == arcade.key.MOD_COMMAND:
            self.level = 0
            self.lives = 2    # TODO: make more generic in case dif lives?
            self.points = 0
            self.setup()

        if symbol == arcade.key.KEY_2 and modifiers == arcade.key.MOD_COMMAND:
            self.level = 1
            self.lives = 2    # TODO: make more generic in case dif lives?
            self.points = self.level_settings['points goal'][0]
            self.setup()

        if symbol == arcade.key.KEY_3 and modifiers == arcade.key.MOD_COMMAND:
            self.level = 2
            self.lives = 2    # TODO: make more generic in case dif lives?
            self.points = self.level_settings['points goal'][1]
            self.setup()

    def on_key_release(self, symbol: int, modifiers: int) -> None:

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

    def __str__(self) -> str:
        return ("<MyGameWindow: width = {}, height = {}, player_location = {},"
                " num EnemyShips = {}, num Asteroids = {},"
                " num player lasers = {}, num enemy lasers = {},"
                " num explosions = {}>".format(self.width, self.height,
                                               (self.player_sprite.center_x,
                                                self.player_sprite.center_y),
                                               len(self.enemy_list),
                                               len(self.asteroid_list),
                                               len(self.player_laser_list),
                                               len(self.enemy_laser_list),
                                               len(self.explosion_list)))


class GameLostView(arcade.View):
    def __init__(self):
        super().__init__()

        arcade.set_background_color((0, 0, 0))

        self.game_over_text = "Game Over"
        self.instruction_text = ("\n\nRestart with 'cmd + r' or 'ctrl + r'"
                                 "\n\nExit with 'cmd + w' or 'ctrl + w'")

        self.bg_colors = ((0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0))
        self.bg_points = ((0, 0), (self.window.width, 0),
                          (self.window.width, self.window.height),
                          (0, self.window.height))

    def on_draw(self):
        arcade.start_render()

        red = (128, 0, 0)
        black = (0, 0, 0)
        blue = (0, 0, 205)
        self.bg_colors = (black, red, black, blue)
        background = arcade.create_rectangle_filled_with_colors(self.bg_points,
                                                                self.bg_colors)

        background.draw()

        arcade.draw_text(self.game_over_text, self.window.width / 2,
                         self.window.height / 2, (255, 255, 255),
                         anchor_x="center", anchor_y="bottom",
                         font_size=60, align="center", bold=True,
                         width=self.window.width, multiline=True)
        arcade.draw_text(self.instruction_text, self.window.width / 2,
                         self.window.width / 4, (255, 255, 255),
                         anchor_x="center", anchor_y="baseline",
                         font_size=20, align="center", bold=True,
                         width=self.window.width, multiline=True)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        # Gracefully quit program
        if symbol == arcade.key.W and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            arcade.close_window()

        # Restart program, TODO also reset to level 1
        if symbol == arcade.key.R and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
# TODO ARGUMENTS FOR ALL RESTARTS -- TUPLES? DICTS?
            game = GameView()
            self.window.show_view(game)


class GameWonView(arcade.View):
    def __init__(self):
        super().__init__()

        arcade.set_background_color((0, 0, 0))

        self.game_won_text = "You won!"
        self.instruction_text = ("\n\nRestart with 'cmd + r' or 'ctrl + r'"
                                 "\n\nExit with 'cmd + w' or 'ctrl + w'")

        self.bg_colors = ((0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0))
        self.bg_points = ((0, 0), (self.window.width, 0),
                          (self.window.width, self.window.height),
                          (0, self.window.height))

    # TODO --- let player play around? have to get sprites, updates and controls
    def on_update(self, delta_time: float = 1 / 60):
        pass

    def on_draw(self):
        arcade.start_render()

        red = (180, 100, 240)
        black = (0, 0, 0)
        blue = (0, 0, 205)
        self.bg_colors = (black, blue, black, red)
        background = arcade.create_rectangle_filled_with_colors(self.bg_points,
                                                                self.bg_colors)

        background.draw()

        arcade.draw_text(self.game_won_text, self.window.width / 2,
                         self.window.height / 2, (255, 255, 255),
                         anchor_x="center", anchor_y="bottom",
                         font_size=60, align="center", bold=True,
                         width=self.window.width, multiline=True)
        arcade.draw_text(self.instruction_text, self.window.width / 2,
                         self.window.width / 4, (255, 255, 255),
                         anchor_x="center", anchor_y="baseline",
                         font_size=20, align="center", bold=True,
                         width=self.window.width, multiline=True)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        # Gracefully quit program
        if symbol == arcade.key.W and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            arcade.close_window()

        # Restart program, TODO also reset to level 1
        if symbol == arcade.key.R and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
# TODO ARGUMENTS FOR ALL RESTARTS -- TUPLES? DICTS?
            game = GameView()
            self.window.show_view(game)


class PauseView(arcade.View):
    def __init__(self, game_view: GameView):
        super().__init__()

        self.game_view = game_view

        arcade.set_background_color((0, 0, 0))
        self.faded_look = (255, 255, 255, 100)

        self.pause_text = "Paused"
        self.instruction_text = ("\n\nResume play with 'cmd + t' or 'ctrl + t'"
                                 "\n\nRestart with 'cmd + r' or 'ctrl + r'"
                                 "\n\nExit with 'cmd + w' or 'ctrl + w'")

        self.player_list = game_view.player_list
        self.asteroid_list = game_view.asteroid_list
        self.enemy_list = game_view.enemy_list
        self.player_lasers = game_view.player_laser_list
        self.enemy_lasers = game_view.enemy_laser_list

    def on_update(self, delta_time: float = 1 / 60):
        pass

    def on_draw(self):
        arcade.start_render()

        if self.player_list:
            self.player_list.draw()
        if self.asteroid_list:
            self.asteroid_list.draw()
        if self.enemy_list:
            self.enemy_list.draw()
        if self.player_lasers:
            self.player_lasers.draw()
        if self.enemy_lasers:
            self.enemy_lasers.draw()

        arcade.draw_rectangle_filled(self.window.width / 2,
                                     self.window.height / 2,
                                     self.window.width, self.window.height,
                                     self.faded_look)

        arcade.draw_text(self.pause_text, self.window.width / 2,
                         self.window.height / 2, (255, 255, 255),
                         anchor_x="center", anchor_y="bottom",
                         font_size=60, align="center", bold=True,
                         width=self.window.width, multiline=True)
        arcade.draw_text(self.instruction_text, self.window.width / 2,
                         self.window.width / 4, (255, 255, 255),
                         anchor_x="center", anchor_y="baseline",
                         font_size=20, align="center", bold=True,
                         width=self.window.width, multiline=True)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        # Gracefully quit program
        if symbol == arcade.key.W and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            arcade.close_window()

        # Restart program, TODO also reset to level 1
        if symbol == arcade.key.R and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):

# TODO ARGUMENTS FOR ALL RESTARTS -- TUPLES? DICTS?
            game = GameView()
            self.window.show_view(game)

        if symbol == arcade.key.T and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            pause_view = PauseView(self.game_view)
            self.window.show_view(pause_view)


def textures_from_spritesheet(filename: str, texture_width: int,
                              texture_height: int, columns: int,
                              num_textures: int,
                              skip_rate: int = 1) -> List[arcade.Texture]:
    """
    Returns a list of textures from given spritesheet. A spritesheet is an
    image file with grid of sprite textures. The textures must all be the
    same width and the same height. The spritesheet's last (bottom) row may
    be partially filled by textures; all other rows are assumed to be full.

    Note: It turns out there's an Arcade function that loads a spritesheet,
    to a list but it would only save a couple lines of code and I like
    what I have here, so I'm intentionally not using Arcade's version.
    (Next time I have to load a spritesheet in a different file, I will use
    the Arcade function)
    """

    # Validate parameters
    if not isinstance(filename, str):
        raise TypeError("filename must be a string")
    if not isinstance(texture_width, int):
        raise TypeError("texture_width must be an integer")
    if texture_width < 0:
        raise TypeError("texture_width must be non-negative")
    if not isinstance(texture_height, int):
        raise TypeError("texture_height must be an integer")
    if texture_height < 0:
        raise TypeError("texture_height must be non-negative")
    if not isinstance(columns, int):
        raise TypeError("columns must be an integer")
    if columns <= 0:
        raise TypeError("columns must be positive")
    if not isinstance(num_textures, int):
        raise TypeError("num_textures must be an integer")
    if num_textures < 0:
        raise TypeError("num_textures must be non-negative")

    # List of textures (frames of an animation; ways the sprite can look, eg
    # standing facing right vs crouching)
    textures = []

    # Iterate over spritesheet
    for i in range(0, num_textures, skip_rate):

        # coordinates of top-left pixel of section to extract
        # x coordinate changes with every image, cycling over each column
        # in each row
        x = (i % columns) * texture_width

        # y coordinate changes for each row, after 'columns' number of
        # textures
        y = (i // columns) * texture_height

        # This may raise an error if the image is too short or too narrow
        # for the given number of columns or images, but I want that
        # message to be passed along to the user, not handled here
        textures.append(arcade.load_texture(filename, x=x, y=y,
                                            width=texture_width,
                                            height=texture_height))

    return textures


def main():
    """
    Determines the specifics of screen size and which images to use for each
    sprite in the game. Instantiates and runs the game window.
    """

    # Process images and filenames for sprites whose image data needs extra
    # work

    # Get list of explosion textures from explosion file spritesheet
    explosion_textures = textures_from_spritesheet(EXPLOSION_FILE["filename"],
                                                   EXPLOSION_FILE[
                                                       "texture_width"],
                                                   EXPLOSION_FILE[
                                                       "texture_height"],
                                                   EXPLOSION_FILE["columns"],
                                                   EXPLOSION_FILE[
                                                       "num_textures"],
                                                   EXPLOSION_SKIP_RATE)

    # Set up list of 10 asteroid filenames formed from base name
    asteroid_filenames = []
    for i in range(1, 5):
        asteroid_filenames.append(ASTEROID_FILENAME_BASE.format(
            "big{}".format(i)))
    for i in range(1, 3):
        asteroid_filenames.append(ASTEROID_FILENAME_BASE.format(
            "med{}".format(i)))
        asteroid_filenames.append(ASTEROID_FILENAME_BASE.format(
            "small{}".format(i)))
        asteroid_filenames.append(ASTEROID_FILENAME_BASE.format(
            "tiny{}".format(i)))

    # Make tuples of each sprite's image filename(s) and scale
    player_ship_data = (PLAYER_SHIPS, PLAYER_SHIP_SCALE)
    player_laser_data = (PLAYER_LASER, PLAYER_LASER_SCALE)
    enemy_ship_data = (ENEMY_SHIPS, ENEMY_SHIP_SCALE)
    enemy_laser_data = (ENEMY_LASER, ENEMY_LASER_SCALE)
    asteroid_data = (asteroid_filenames, ASTEROID_SCALE)

    # Explosion has already been processed into list of arcade Textures
    # so it's a tuple of Textures and scale
    explosion_data = (explosion_textures, EXPLOSION_SCALE)

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game_view = GameView(explosion_data, player_ship_data, player_laser_data,
                         enemy_ship_data, enemy_laser_data, asteroid_data,
                         BACKGROUND_SOUND, PLAYER_LASER_SOUND,
                         ENEMY_LASER_SOUND, EXPLOSION_SOUND, LEVEL_UP_SOUND,
                         LOST_LIFE_SOUND, WIN_SOUND, GAME_OVER_SOUND)
    game_view.setup()
    title_view = TitleView(game_view)
    window.show_view(title_view)
    arcade.run()


if __name__ == "__main__":
    main()
