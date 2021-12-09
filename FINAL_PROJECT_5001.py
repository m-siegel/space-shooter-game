"""
I-M Siegel

Explosion graphics from https://www.explosiongenerator.com/, via Arcade
resources

Other images from Space Shooter (Redux, plus fonts and sounds) by Kenney
Vleugels (www.kenney.nl), licensed under Creative Commons.
https://kenney.nl/assets/space-shooter-redux

----------------------------------------------------------------------------
----------------------------------------------------------------------------

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

----------------------------------------------------------------------------
----------------------------------------------------------------------------

TODO:
    ------------------------------------
    STYLE
        - DEFENSIVE PROGRAMMING (at least in the method params, not name
        mangling)
        - PEP8 COMPLIANCE
        - general structure
        - COMMENTS
    ------------------------------------
    PRESENTATION
    ------------------------------------
    - change meteors: maybe only big and med ones at .5 scale (maybe small,
    too)
    - add lives?
    - add damage

    TODO: Install Python 3.10 after semester; allows for writing
    Union[int, float] as int | float

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
    - differing functions for resetting for new game and resetting for level
    (eg when points should be reset)
    - add levels and design levels
        - add shortcuts (cmd 1, cmd 2, cmd 3)
    - add sounds
    - type hints
    - __str__ to all
    - add start screen
    - add end screen
"""


# Program built with arcade library, extends arcade classes
import arcade

# Used for game logic
import math
import random

# For type hinting
from typing import List, Tuple, Union, Optional
import pyglet    # Although imported with arcade, needed for type hinting

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Space Shooter"

# File names for sprites
# Using globals so they're easy to change if someone wants to use different
# images or if the images are stored with a different filepath

# If images come from the same pack of resources, they may be able to scale
# together. In case any need different scaling, each has a global variable
# for its scale. Most are set equal to IMAGE_SCALE, but all can be changed
IMAGE_SCALE = .5

# Player ship filenames (3 string filenames: one for each level)
PLAYER_SHIPS = ("media/kenney_nl/spaceshooter/PNG/"
                "Player_ships/playerShip1_blue.png",
                "media/kenney_nl/spaceshooter/PNG/"
                "Player_ships/playerShip2_blue.png",
                "media/kenney_nl/spaceshooter/PNG/"
                "Player_ships/playerShip3_blue.png")
# In case image needs unique scaling
PLAYER_SHIP_SCALE = IMAGE_SCALE
PLAYER_SHIP_ROTATION = 0    # Degrees to rotate to face North

# Player laser filename (one string)
PLAYER_LASER = "media/kenney_nl/spaceshooter/PNG/Lasers/laserBlue01.png"
# In case image needs unique scaling
PLAYER_LASER_SCALE = IMAGE_SCALE
PLAYER_LASER_ROTATION = 0    # Degrees to rotate to face North


# Enemy Ship filenames (2 filename strings: one for each of levels 2 and 3)
ENEMY_SHIPS = ("media/kenney_nl/spaceshooter/PNG/Enemies/enemyRed1.png",
               "media/kenney_nl/spaceshooter/PNG/Enemies/enemyRed2.png")
ENEMY_SHIP_SCALE = IMAGE_SCALE
ENEMY_SHIP_ROTATION = 90    # Degrees to rotate to face East

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
ENEMY_LASER_ROTATION = -90    # Degrees to rotate to face East

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

    def __init__(self, image_filename: str, scale: Union[int, float],
                 image_rotation: Union[int, float], laser_filename: str,
                 laser_scale: Union[int, float],
                 laser_rotation: Union[int, float],
                 laser_list: arcade.SpriteList, window_dims: Tuple[int, int],
                 laser_fade_rate: Union[int, float] = 15,
                 laser_sound: Optional[arcade.Sound] = None):
        """
        Constructor. Sets attributes self.speed, self.angle_rate and
        self.forward_rate. Uses arcade.Sprite default settings for other
        attributes, including self.angle.
        """

        # Validate parameters
        if not isinstance(image_filename, str):
            raise TypeError("TypeError: image_filename must be a string")
        if not isinstance(scale, (int, float)):
            raise TypeError("TypeError: scale must be a numeric type")
        if scale <= 0:
            raise ValueError("ValueError: scale must be positive")
        if not isinstance(image_rotation, (int, float)):
            raise TypeError("TypeError: image_rotation must be a numeric type")
        if not isinstance(laser_filename, str):
            raise TypeError("TypeError: laser_filename must be a string")
        if not isinstance(laser_scale, (int, float)):
            raise TypeError("TypeError: laser_scale must be a numeric type")
        if laser_scale <= 0:
            raise ValueError("ValueError: laser_scale must be positive")
        if not isinstance(laser_rotation, (int, float)):
            raise TypeError("TypeError: laser_rotation must be a numeric type")
        if not isinstance(laser_list, arcade.SpriteList):
            raise TypeError("TypeError: laser_list must be an"
                            " arcade.SpriteList")
        if not isinstance(window_dims, tuple):
            raise TypeError("TypeError: window_dims must be a tuple")
        if len(window_dims) != 2:
            raise ValueError("ValueError: window_dims must have length 2")
        for dim in window_dims:
            if not isinstance(dim, int):
                raise TypeError("TypeError: window_dims elements must be ints")
            if dim <= 0:
                raise ValueError("ValueError: window_dim elements must be"
                                 " positive")
        if not isinstance(laser_fade_rate, (int, float)):
            raise TypeError("TypeError: laser_fade_rate must be numeric")
        if laser_fade_rate < 0:
            laser_fade_rate = 0
        if laser_fade_rate > 255:
            laser_fade_rate = 255
        if laser_sound and not isinstance(laser_sound, arcade.Sound):
            raise TypeError("TypeError: laser_sound must be an arcade.Sound")

        super().__init__(filename=image_filename, scale=scale)

        # Degrees the image needs to be rotated to face North
        self.image_rotation = image_rotation

        # Set the sprite's initial angle to face North
        self.angle = image_rotation

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
        self.laser_rotation = laser_rotation - self.image_rotation

        self.laser_fade_rate = laser_fade_rate

        self.laser_speed = 400

        # If the player is trying to shoot now
        self.shooting = False

        self.window_width = window_dims[0]
        self.window_height = window_dims[1]

        self.laser_sound = laser_sound

    def on_update(self, delta_time: float = 1 / 60) -> None:
        """
        Updates sprite's position by changing angle, center_x and center_y
        to animate sprite. Should be called at least 30 times per second.
        Uses delta_time as a factor in setting new position and angle to
        smooth movement in case of a delay in the frequency of calls to
        on_update. Otherwise, a call to on_update with delta_time of .5
        seconds would move the sprite the same amount as a call with
        delta_time of .01.
        :param delta_time: time since last call
        :return: None
        """

        # Validate parameters
        if not isinstance(delta_time, (int, float)):
            raise TypeError("TypeError: delta_time must be numeric")
        if delta_time < 0:
            raise ValueError("ValueError: delta_time must be non-negative")

        # Turn player and move forwards or backwards
        self.turn_and_move(delta_time)

        # Shoot lasers
        self.shoot_lasers()

    def turn_and_move(self, delta_time: float = 1 / 60) -> None:

        # Validate parameters
        if not isinstance(delta_time, (int, float)):
            raise TypeError("TypeError: delta_time must be numeric")
        if delta_time < 0:
            raise ValueError("ValueError: delta_time must be non-negative")

        # Update angle player is facing
        # Multiply by delta_time for smooth movement
        self.angle += self.change_angle * delta_time

        # Find change_x and change_y based on new angle (essentially a target
        # point). Default angle is North, so target point on unit circle
        # x-coordinate (change_x) is negative sin (not positive cos) and
        # y-coordinate (change_y) is cos (not sin)
        self.change_x = -math.sin(math.radians(
            self.angle - self.image_rotation))
        self.change_y = math.cos(math.radians(
            self.angle - self.image_rotation))

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

    def shoot_lasers(self) -> None:
        # Shoot lasers
        if self.shooting and self.reload_ticks <= 0:
            self.laser_list.append(Laser(self.center_x, self.center_y,
                                         self.laser_filename, self.laser_scale,
                                         angle=(self.angle
                                                + self.laser_rotation),
                                         speed=self.laser_speed,
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
    def __init__(self,  x: Union[int, float], y: Union[int, float],
                 image_filename: str, scale: Union[int, float],
                 angle: Union[int, float] = 0, speed: Union[int, float] = 200,
                 fade_rate: Union[int, float] = 0,
                 sound: Optional[arcade.Sound] = None):

        # Validate parameters
        if not isinstance(x, (int, float)):
            raise TypeError("TypeError: x must be a numeric type")
        if not isinstance(y, (int, float)):
            raise TypeError("TypeError: y must be a numeric type")
        if not isinstance(image_filename, str):
            raise TypeError("TypeError: image_filename must be a string")
        if not isinstance(scale, (int, float)):
            raise TypeError("TypeError: scale must be a numeric type")
        if scale <= 0:
            raise ValueError("ValueError: scale must be positive")
        if not isinstance(angle, (int, float)):
            raise TypeError("TypeError: angle must be a numeric type")
        if not isinstance(speed, (int, float)):
            raise TypeError("TypeError: speed must be a numeric type")
        if not isinstance(fade_rate, (int, float)):
            raise TypeError("TypeError: fade_rate must be a numeric type")
        if fade_rate < 0:
            fade_rate = 0
        if fade_rate > 255:
            fade_rate = 255
        if sound and not isinstance(sound, arcade.Sound):
            raise TypeError("TypeError: sound must be an arcade.Sound")

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

        # Validate parameters
        if not isinstance(delta_time, (int, float)):
            raise TypeError("TypeError: delta_time must be numeric")
        if delta_time < 0:
            raise ValueError("ValueError: delta_time must be non-negative")

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
                 file_rotation: int = 0,  target_x: Union[int, float] = 0,
                 target_y: Union[int, float] = 0):

        # Validate parameters
        if not isinstance(image_filename, str):
            raise TypeError("TypeError: image_filename must be a string")
        if not isinstance(scale, (int, float)):
            raise TypeError("TypeError: scale must be a numeric type")
        if scale <= 0:
            raise ValueError("ValueError: scale must be positive")
        if not isinstance(file_rotation, (int, float)):
            raise TypeError("TypeError: file_rotation must be a numeric type")
        if not isinstance(target_x, (int, float)):
            raise TypeError("TypeError: target_x must be a numeric type")
        if not isinstance(target_y, (int, float)):
            raise TypeError("TypeError: target_y must be a numeric type")

        super().__init__(filename=image_filename, scale=scale)

        # Initialize speed to not moving
        self.speed = 0

        # Initialize target point to center of screen
        self.target_x = target_x
        self.target_y = target_y

        # I'll be using attributes change_x and change_y to indicate how much
        # sprite should move along each direction with each update.
        # arcade.Sprite has those attributes, so I don't initialise them here

        # In case image source needs to be rotated to face right way
        self.image_rotation = file_rotation

        # Largest measurement for the sprite. Used to determine if can be
        # seen offscreen at any angle
        self.diagonal = int((self.width ** 2 + self.height ** 2) ** .5)

    def on_update(self, delta_time: float = 1 / 60) -> float:

        # Validate parameters
        if not isinstance(delta_time, (int, float)):
            raise TypeError("TypeError: delta_time must be numeric")
        if delta_time < 0:
            raise ValueError("ValueError: delta_time must be non-negative")

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

        # If at target point, just return current angle
        else:
            angle_rad = math.radians(self.angle - self.image_rotation)

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

        # This class doesn't adjust the sprite's angle, but descendent classes
        # might want to, so return the angle from the sprite to the target
        return angle_rad

    def set_target(self, x: Union[int, float], y: Union[int, float]) -> None:

        if not isinstance(x, (int, float)):
            raise TypeError("TypeError: x must be a numeric type")
        if not isinstance(y, (int, float)):
            raise TypeError("TypeError: y must be a numeric type")

        self.target_x = x
        self.target_y = y

    def get_random_offscreen_point(self, screen_width: Union[int, float],
                                   screen_height: Union[
                                       int, float]) -> Tuple[int, int]:
        """
        Returns the coordinates of a random point offscreen. Point is not
        far offscreen, but far enough to hid sprite.
        """
        # Validate parameters
        if not isinstance(screen_width, (int, float)):
            raise TypeError("TypeError: screen_width must be a numeric type")
        if screen_width <= 0:
            raise ValueError("ValueError: screen_width must be positive")
        if not isinstance(screen_height, (int, float)):
            raise TypeError("TypeError: screen_height must be a numeric type")
        if screen_height <= 0:
            raise ValueError("ValueError: screen_height must be positive")

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
            y = random.randrange(-self.diagonal,
                                 screen_height + self.diagonal)

        return x, y

    def set_random_offscreen_location(self, screen_width: Union[int, float],
                                      screen_height: Union[
                                          int, float]) -> None:
        """
        Sets sprite's location to random point offscreen point such that
        sprite won't be visible.
        """

        point = self.get_random_offscreen_point(screen_width, screen_height)

        self.center_x = point[0]
        self.center_y = point[1]

    @staticmethod
    def get_random_in_range(num_range: Union[int, Tuple[int], Tuple[int, int],
                                             Tuple[int, int, int]]) -> int:
        """
        Returns a random number within the given range. The range is slightly
        more flexible than the Python range() function, but its elements serve
        the same purpose: (start, stop, step). If only start is given, if start
        and stop are equal, or if the step is 0, then the return value will be
        equal start. Otherwise, it will return a random number within the given
        range. Ranges like (5, -3, 2), which are invalid for other range
        functions, will be rearranged to be valid, for example, (5, -3, 2) -->
        (5, -3, -2). Note: this method allows for negative return values.

        Used by class for set_speed_in_range() and set_random_spin().
        """

        # Validate parameters
        if not isinstance(num_range, (int, tuple)):
            raise TypeError("TypeError: num_range must be an int or a tuple"
                            " of ints")
        if isinstance(num_range, tuple):
            if not 1 <= len(num_range) <= 3:
                raise ValueError("ValueError: num_range must have length"
                                 " 1, 2 or 3")
            for num in num_range:
                if not isinstance(num, int):
                    raise TypeError("TypeError: num_range's elements must "
                                    "be integers")

        # If num_range isn't really a range because it's only one number or
        # because the start and end of the range are the same, set speed to
        # that number
        if isinstance(num_range, int):
            return num_range
        if len(num_range) == 1 or num_range[0] == num_range[1]:
            return num_range[0]

        # Set step
        if len(num_range) == 2:
            step = 1
        else:
            step = num_range[2]

            # If step is zero, then num_range can't be traversed, so make
            # speed first number in range
            if step == 0:
                return num_range[0]

        # The range from num_range[0] to num_range[1] must be able to be
        # traversed using the step size. Can only get from smaller number to
        # bigger number with positive steps, or from bigger to smaller using
        # negative steps. If the sign of the step doesn't match the given
        # range, change the sign of the step
        if not ((num_range[0] < num_range[1] and step > 0)
                or num_range[0] > num_range[1] and step < 0):
            step *= -1

        return random.randrange(num_range[0], num_range[1], step)

    def set_speed_in_range(self,
                           speed_range: Union[int, Tuple[int], Tuple[int, int],
                                              Tuple[int, int, int]]) -> None:
        """
        Sets the sprites speed to a number within the given range.
        Note: this method allows for negative speeds. That's intentional
        since later extensions may want the ability to move away from targets.
        """

        # Don't validate parameters here because validation is done in
        # get_random_in_range, which raises and handles the same errors this
        # should
        self.speed = self.get_random_in_range(speed_range)

    # Though this is currently only used by asteroid, not enemy, it could be
    # useful for a later extension of the class (eg to make enemies spin
    # out of control after getting shot)
    def set_random_spin(self,
                        speed_range: Union[
                            int, Tuple[int], Tuple[int, int],
                            Tuple[int, int, int]] = (-5, 6, 2)) -> None:
        """
        Sets the sprite's change_angle to a number within the given range.
        """

        # Don't validate parameters here because validation is done in
        # get_random_in_range, which raises and handles the same errors this
        # should
        self.change_angle = self.get_random_in_range(speed_range)

    def set_random_offscreen_target(self, screen_width: Union[int, float],
                                    screen_height: Union[int, float]) -> None:
        """
        Sets sprite's target to random point offscreen point such that
        sprite won't be visible once it reaches that point
        """

        # Don't validate parameters here because validation is done in
        # get_random_offscreen_point, which raises and handles the same errors
        # this should
        point = self.get_random_offscreen_point(screen_width, screen_height)

        self.target_x = point[0]
        self.target_y = point[1]

    # Asteroid uses this but EnemyShip doesn't. I think it's useful to have
    # here in case other classes extend this and need to cross the screen
    def set_random_cross_screen_target(self, screen_width: Union[int, float],
                                       screen_height: Union[
                                           int, float]) -> None:
        """
        Set sprite's target to random point across the screen. "Across the
        screen" means that the sprite will have to cross some part of the
        screen in order to reach the target.
        """

        # Validate parameters
        if not isinstance(screen_width, (int, float)):
            raise TypeError("TypeError: screen_width must be a numeric type")
        if screen_width <= 0:
            raise ValueError("ValueError: screen_width must be positive")
        if not isinstance(screen_height, (int, float)):
            raise TypeError("TypeError: screen_height must be a numeric type")
        if screen_height <= 0:
            raise ValueError("ValueError: screen_height must be positive")

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
    def __init__(self, image_filename: str, scale: Union[int, float]):

        # Validate parameters
        if not isinstance(image_filename, str):
            raise TypeError("TypeError: image_filename must be a string")
        if not isinstance(scale, (int, float)):
            raise TypeError("TypeError: scale must be a numeric type")
        if scale <= 0:
            raise ValueError("ValueError: scale must be positive")

        super().__init__(image_filename, scale)

    def on_update(self, delta_time: float = 1 / 60) -> None:

        # Validate parameters
        if not isinstance(delta_time, (int, float)):
            raise TypeError("TypeError: delta_time must be numeric")
        if delta_time < 0:
            raise ValueError("ValueError: delta_time must be non-negative")

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
                 image_rotation: Union[int, float], laser_filename: str,
                 laser_scale: Union[int, float],
                 laser_rotation: Union[int, float],
                 laser_list: arcade.SpriteList, laser_speed: int = 0,
                 laser_fade_rate: Union[int, float] = 40,
                 laser_sound: Optional[arcade.Sound] = None):

        # Validate parameters
        if not isinstance(image_filename, str):
            raise TypeError("TypeError: image_filename must be a string")
        if not isinstance(scale, (int, float)):
            raise TypeError("TypeError: scale must be a numeric type")
        if scale <= 0:
            raise ValueError("ValueError: scale must be positive")
        if not isinstance(image_rotation, (int, float)):
            raise TypeError("TypeError: image_rotation must be a numeric type")
        if not isinstance(laser_filename, str):
            raise TypeError("TypeError: laser_filename must be a string")
        if not isinstance(laser_scale, (int, float)):
            raise TypeError("TypeError: laser_scale must be a numeric type")
        if laser_scale <= 0:
            raise ValueError("ValueError: laser_scale must be positive")
        if not isinstance(laser_rotation, (int, float)):
            raise TypeError("TypeError: laser_rotation must be a numeric type")
        if not isinstance(laser_list, arcade.SpriteList):
            raise TypeError("TypeError: laser_list must be an "
                            "arcade.SpriteList")
        if not isinstance(laser_speed, int):
            raise TypeError("TypeError: laser_speed must be an int")
        if not isinstance(laser_fade_rate, (int, float)):
            raise TypeError("TypeError: laser_fade_rate must be numeric")
        # TODO: ASK -- things like this are also checked in laser. is it okay
        #  to check in both places? what's best practice?
        if laser_fade_rate < 0:
            laser_fade_rate = 0
        if laser_fade_rate > 255:
            laser_fade_rate = 255
        if laser_sound and not isinstance(laser_sound, arcade.Sound):
            raise TypeError("TypeError: laser_sound must be an arcade.Sound")

        super().__init__(image_filename, scale, file_rotation=image_rotation)

        # Pointer to game window's enemy_laser_list
        self.laser_list = laser_list

        # Laser image
        self.laser_filename = laser_filename
        self.laser_scale = laser_scale
        self.laser_rotation = laser_rotation - self.image_rotation
        self.laser_fade_rate = laser_fade_rate

        self.laser_speed = laser_speed

        # Ships should be able to shoot the moment they're created
        self.reload_time = laser_speed

        self.laser_sound = laser_sound

    def on_update(self, delta_time: float = 1 / 60) -> None:

        # Validate parameters
        if not isinstance(delta_time, (int, float)):
            raise TypeError("TypeError: delta_time must be numeric")
        if delta_time < 0:
            raise ValueError("ValueError: delta_time must be non-negative")

        # Moves sprite towards target point at speed, returns angle to target
        # TODO: ASK -- Technically this argument isn't necessary,
        #  but it adds clarity
        angle_rad = super().on_update(delta_time)

        # Set angle of ship to match angle of movement
        # angle_rad is the measured from the positive x axis, but image
        # initially faces down
        self.angle = math.degrees(angle_rad) + self.image_rotation

        # Periodically shoot at player, unless there's no reload time
        if self.reload_time is None:
            return
        self.reload_time -= 1
        if self.reload_time <= 0:
            self.laser_list.append(Laser(self.center_x, self.center_y,
                                         self.laser_filename,
                                         self.laser_scale,
                                         angle=(self.angle
                                                + self.laser_rotation),
                                         speed=self.laser_speed,
                                         fade_rate=self.laser_fade_rate,
                                         sound=self.laser_sound))
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

        # Validate parameters
        if not isinstance(textures, list):
            raise TypeError("TypeError: textures must be a list")
        if len(textures) <= 0:
            raise ValueError("ValueError: textures must have at least one "
                             "texture")
        for texture in textures:
            if not isinstance(texture, arcade.Texture):
                raise TypeError("TypeError: elements in textures must be "
                                "arcade.Textures")
        if not isinstance(center_x, (int, float)):
            raise TypeError("TypeError: center_x must be a numeric type")
        if not isinstance(center_y, (int, float)):
            raise TypeError("TypeError: center_y must be a numeric type")
        if not isinstance(scale, (int, float)):
            raise TypeError("TypeError: scale must be a numeric type")
        if scale <= 0:
            raise ValueError("ValueError: scale must be positive")
        if sound and not isinstance(sound, arcade.Sound):
            raise TypeError("TypeError: sound must be an arcade.Sound")

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

    # TODO: ASK if a method only has itself as a parameter, do I need to
    #  validate it?
    def update(self) -> None:
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


# Main game logic
class GameView(arcade.View):
    """
    Extends arcade.View with specifics for how this game runs. Inherits
    attributes and methods from arcade.Window that make a game possible.
    For example, as a descendent of an arcade.Window, MyGameWindow's on_draw
    and on_update methods automatically get called 60 times per second, which
    enables animation and gameplay.
    """
    def __init__(self, explosion_textures: Tuple[List[arcade.Texture],
                                                 Union[int, float]],
                 player_ship_image_files: Tuple[Tuple[str, str, str],
                                                Union[int, float],
                                                Union[int, float]],
                 player_laser_image_file: Tuple[str, Union[int, float],
                                                Union[int, float]],
                 enemy_ship_image_files: Tuple[Tuple[str, str],
                                               Union[int, float],
                                               Union[int, float]],
                 enemy_laser_image_file: Tuple[str, Union[int, float],
                                               Union[int, float]],
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
        """

        # Validate parameters

        # explosion_textures
        if not isinstance(explosion_textures, tuple):
            raise TypeError("TypeError: explosion_textures must be a tuple")
        if len(explosion_textures) < 2:
            raise ValueError("ValueError: explosion_textures needs at least "
                             "two elements")
        if not isinstance(explosion_textures[0], list):
            raise TypeError("TypeError: explosion_textures[0] must be a list")
        if len(explosion_textures[0]) <= 0:
            raise ValueError("ValueError: explosion_textures[0] must have at "
                             "least one texture")
        for texture in explosion_textures[0]:
            if not isinstance(texture, arcade.Texture):
                raise TypeError("TypeError: elements in explosion_textures[0]"
                                " must be arcade.Textures")
        if not isinstance(explosion_textures[1], (int, float)):
            raise TypeError("TypeError: explosion_textures[1] must be a "
                            "numeric type")
        if explosion_textures[1] <= 0:
            raise ValueError("ValueError: explosion_textures[1] must be "
                             "positive")

        # player_ship_image_files
        if not isinstance(player_ship_image_files, tuple):
            raise TypeError("TypeError: player_ship_image_files must be a "
                            "tuple")
        if len(player_ship_image_files) != 3:
            raise ValueError(
                "ValueError: player_ship_image_files must have three elements")
        if not isinstance(player_ship_image_files[0], tuple):
            raise TypeError(
                "TypeError: player_ship_image_files[0] must be a tuple")
        if len(player_ship_image_files[0]) != 3:
            raise ValueError(
                "ValueError: player_ship_image_files[0] must have three "
                "elements ")
        for filename in player_ship_image_files[0]:
            if not isinstance(filename, str):
                raise TypeError("TypeError: elements in "
                                "player_ship_image_files[0] must be strings")
        if not isinstance(player_ship_image_files[1], (int, float)):
            raise TypeError("TypeError: player_ship_image_files[1] must be a "
                            "numeric type")
        if player_ship_image_files[1] <= 0:
            raise ValueError("ValueError: player_ship_image_files[1] must be "
                             "positive")
        if not isinstance(player_ship_image_files[2], (int, float)):
            raise TypeError("TypeError: player_ship_image_files[2] must be a "
                            "numeric type")

        # player_laser_image_file
        if not isinstance(player_laser_image_file, tuple):
            raise TypeError("TypeError: player_laser_image_file must be a "
                            "tuple")
        if len(player_laser_image_file) != 3:
            raise ValueError(
                "ValueError: player_laser_image_file must have three elements")
        if not isinstance(player_laser_image_file[0], str):
            raise TypeError(
                "TypeError: player_laser_image_file[0] must be a string")
        if not isinstance(player_laser_image_file[1], (int, float)):
            raise TypeError(
                "TypeError: player_laser_image_file[1] must be a "
                "numeric type")
        if player_laser_image_file[1] <= 0:
            raise ValueError(
                "ValueError: player_laser_image_file[1] must be positive")
        if not isinstance(player_laser_image_file[2], (int, float)):
            raise TypeError(
                "TypeError: player_laser_image_file[2] must be a "
                "numeric type")

        # enemy_ship_image_files
        if not isinstance(enemy_ship_image_files, tuple):
            raise TypeError("TypeError: enemy_ship_image_files must be a "
                            "tuple")
        if len(enemy_ship_image_files) != 3:
            raise ValueError(
                "ValueError: enemy_ship_image_files must have three elements")
        if not isinstance(enemy_ship_image_files[0], tuple):
            raise TypeError(
                "TypeError: enemy_ship_image_files[0] must be a tuple")
        if len(enemy_ship_image_files[0]) < 2:
            raise ValueError(
                "ValueError: enemy_ship_image_files[0] must have at least"
                " two elements")
        for filename in enemy_ship_image_files[0]:
            if not isinstance(filename, str):
                raise TypeError("TypeError: elements in "
                                "enemy_ship_image_files[0] must be strings")
        if not isinstance(enemy_ship_image_files[1], (int, float)):
            raise TypeError(
                "TypeError: enemy_ship_image_files[1] must be a "
                "numeric type")
        if enemy_ship_image_files[1] <= 0:
            raise ValueError(
                "ValueError: enemy_ship_image_files[1] must be "
                "positive")
        if not isinstance(enemy_ship_image_files[2], (int, float)):
            raise TypeError(
                "TypeError: enemy_ship_image_files[2] must be a "
                "numeric type")

        # enemy_laser_image_file
        if not isinstance(enemy_laser_image_file, tuple):
            raise TypeError("TypeError: enemy_laser_image_file must be a "
                            "tuple")
        if len(enemy_laser_image_file) != 3:
            raise ValueError(
                "ValueError: enemy_laser_image_file must have three elements")
        if not isinstance(enemy_laser_image_file[0], str):
            raise TypeError(
                "TypeError: enemy_laser_image_file[0] must be a string")
        if not isinstance(enemy_laser_image_file[1], (int, float)):
            raise TypeError(
                "TypeError: enemy_laser_image_file[1] must be a "
                "numeric type")
        if enemy_laser_image_file[1] <= 0:
            raise ValueError(
                "ValueError: enemy_laser_image_file[1] must be positive")
        if not isinstance(enemy_laser_image_file[2], (int, float)):
            raise TypeError(
                "TypeError: enemy_laser_image_file[2] must be a "
                "numeric type")

        # asteroid_image_files
        if not isinstance(asteroid_image_files, tuple):
            raise TypeError("TypeError: asteroid_image_files must be a "
                            "tuple")
        if len(asteroid_image_files) != 2:
            raise ValueError(
                "ValueError: asteroid_image_files must have two elements")
        if not isinstance(asteroid_image_files[0], list):
            raise TypeError(
                "TypeError: asteroid_image_files[0] must be a list")
        if len(asteroid_image_files[0]) <= 0:
            raise ValueError("ValueError: asteroid_image_files[0] must have"
                             "at least one element")
        for filename in asteroid_image_files[0]:
            if not isinstance(filename, str):
                raise TypeError(
                    "TypeError: elements of asteroid_image_files[0]"
                    " must be strings")
        if not isinstance(asteroid_image_files[1], (int, float)):
            raise TypeError(
                "TypeError: asteroid_image_files[1] must be a "
                "numeric type")
        if asteroid_image_files[1] <= 0:
            raise ValueError(
                "ValueError: asteroid_image_files[1] must be positive")

        # Sounds
        if not isinstance(background_music, str):
            raise TypeError("TypeError: background_music must be a string")
        if not isinstance(player_laser_sound, str):
            raise TypeError("TypeError: player_laser_sound must be a string")
        if not isinstance(enemy_laser_sound, str):
            raise TypeError("TypeError: enemy_laser_sound must be a string")
        if not isinstance(explosion_sound, str):
            raise TypeError("TypeError: explosion_sound must be a string")
        if not isinstance(level_up_sound, str):
            raise TypeError("TypeError: level_up_sound must be a string")
        if not isinstance(lost_life_sound, str):
            raise TypeError("TypeError: lost_life_sound must be a string")
        if not isinstance(win_sound, str):
            raise TypeError("TypeError: win_sound must be a string")
        if not isinstance(game_over_sound, str):
            raise TypeError("TypeError: game_over_sound must be a string")

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
        self.lives = 2

        # Number of points player earns for each type of hit
        self.asteroid_points = 5
        self.enemy_points = 15

        # Whether the player is leveling up or dying. Allows for slight delay
        # in changing screen so last explosions can play out
        self.leveling_up = False
        self.dying = False
        self.switch_delay = 0    # Number of updates to delay switch

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
        self.player_ship_image_rotation = player_ship_image_files[2]

        self.player_laser_filename = player_laser_image_file[0]
        self.player_laser_image_scale = player_laser_image_file[1]
        self.player_laser_image_rotation = player_laser_image_file[2]

        self.enemy_ship_filenames = enemy_ship_image_files[0]
        self.enemy_ship_image_scale = enemy_ship_image_files[1]
        self.enemy_ship_image_rotation = enemy_ship_image_files[2]

        self.enemy_laser_filename = enemy_laser_image_file[0]
        self.enemy_laser_image_scale = enemy_laser_image_file[1]
        self.enemy_laser_image_rotation = enemy_laser_image_file[2]

        self.asteroid_filenames = asteroid_image_files[0]
        self.asteroid_image_scale = asteroid_image_files[1]

        # Load sounds

        # Sound
        self.background_music_sound = arcade.load_sound(background_music)
        # Sound player. Can be used to check if sound is playing or has ever
        # played. None means it's never been played.
        self.background_music_player = None

        self.player_laser_sound = arcade.load_sound(player_laser_sound)
        self.player_laser_player = None

        self.enemy_laser_sound = arcade.load_sound(enemy_laser_sound)
        self.enemy_laser_player = None

        self.explosion_sound = arcade.load_sound(explosion_sound)
        self.explosion_player = None

        self.level_up_sound = arcade.load_sound(level_up_sound)
        self.level_up_player = None

        self.lost_life_sound = arcade.load_sound(lost_life_sound)
        self.lost_life_player = None

        self.win_sound = arcade.load_sound(win_sound)
        self.win_player = None

        self.game_over_sound = arcade.load_sound(game_over_sound)
        self.game_over_player = None

        # Key press info
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.space_pressed = False

        # TODO: ASK
        #  - should be tuple of dictionaries or dictionary of tuples (current)?
        #  - should these be stored directly as attributes at the start of
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
            # per second
            'enemy spawn rate': (0, .5, .5),
            # pixels per second
            'enemy speed range': ((50, 100), (30, 80), (80, 130)),
            # amount alpha it loses at each update after 60 updates
            'enemy laser fade': (255, 40, 40),
            'starting asteroids': (10, 0, 10),
            'asteroid spawn rate': (1, 0, 1),
            'asteroid speed range': ((50, 200), (50, 200), (100, 200))}

        self.asteroids_spawning = None
        self.enemies_spawning = None

        # These are set up later in setup() because they're reset at each
        # death or new level
        # Player sprite
        self.player_sprite = None

        # Sprite lists for each group of sprites

        # Even though there's only one player, having having a list to add
        # that sprite to gives more flexibility with later code
        self.player_list = None
        self.player_laser_list = None

        self.asteroid_list = None

        self.enemy_list = None
        self.enemy_laser_list = None

        self.explosion_list = None

        # Most attribute values need to be reset if the player dies or levels
        # up. That's done in the setup function, so call that now.
        self.setup()

    def setup(self) -> None:
        """
        Sets or resets game when the window is opened or the game is
        restarted.
        :return: None
        """

        # Number of updates since level started
        self.updates_this_level = 0

        # At new level or new live, reset
        self.leveling_up = False
        self.dying = False
        self.switch_delay = 0

        if self.lost_life_player and not self.lost_life_sound.is_playing(
                self.lost_life_player):
            self.lost_life_player = None
        if self.level_up_player and not self.level_up_sound.is_playing(
                self.level_up_player):
            self.level_up_player = None

        # Start background sound. stop any previously playing background sound
        if (self.background_music_player
                and self.background_music_sound.is_playing(
                    self.background_music_player)):
            self.background_music_sound.stop(self.background_music_player)

        self.background_music_player = self.background_music_sound.play(
            loop=True)

        # Set number of updates before new asteroid or enemy is spawned
        # 60 updates per second
        if self.level_settings['starting asteroids'][self.level] > 0:
            self.asteroids_spawning = 60 // self.level_settings[
                'asteroid spawn rate'][self.level]
        if self.level_settings['starting enemies'][self.level] > 0:
            self.enemies_spawning = 60 // self.level_settings[
                'enemy spawn rate'][self.level]

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
        # noinspection PyTypeChecker
        self.player_sprite = Player(self.level_settings[
                                        'player ship'][self.level],
                                    self.player_ship_image_scale,
                                    self.player_ship_image_rotation,
                                    self.player_laser_filename,
                                    self.player_laser_image_scale,
                                    self.player_laser_image_rotation,
                                    self.player_laser_list,
                                    (self.width, self.height),
                                    laser_fade_rate=self.level_settings[
                                        'player laser fade'][self.level],
                                    laser_sound=self.player_laser_sound)

        self.player_sprite.center_x = self.width // 2
        self.player_sprite.center_y = self.height // 2

        # Though the player_list only holds one sprite, using a SpriteList
        # instead of the sprite itself for updating and drawing means that
        # MyGameWindow can have a player_sprite attribute without it getting
        # drawn or updated (eg after the player dies) if the sprite is just
        # removed from the list
        self.player_list.append(self.player_sprite)

        # Number of asteroids and enemies depends upon level

        # 'speed range' is a tuple, but it comes from the level_settings dict.
        # The values in level_settings are tuples of multiple types, but the
        # first listed is a tuple of ints (like 'starting asteroids'), so
        # PyCharm thinks all values in the tuples are ints and gives a
        # warning that 'speed range' is an int and the wrong type for the
        # make_asteroids parameter. This is wrong ('speed range is a tuple),
        # so I disabled the PyTypeChecker inspection for this statement
        # noinspection PyTypeChecker
        self.make_asteroids(self.level_settings[
                                'starting asteroids'][self.level],
                            self.level_settings[
                                'asteroid speed range'][self.level])
        # noinspection PyTypeChecker
        self.make_enemy_ships(self.level_settings[
                                  'starting enemies'][self.level],
                              self.level_settings[
                                  'enemy speed range'][self.level])

    def make_asteroids(self, num_asteroids: int,
                       speed_range: Union[int, Tuple[int], Tuple[int, int],
                                          Tuple[int, int, int]]) -> None:

        # Validate parameters
        if not isinstance(num_asteroids, int):
            raise TypeError("TypeError: num_asteroids must be an int")
        if num_asteroids <= 0:
            raise ValueError("ValueError: num_asteroids must be positive")
        if not isinstance(speed_range, (int, tuple)):
            raise TypeError("TypeError: speed_range must be an int or tuple")
        if isinstance(speed_range, tuple):
            if not 1 <= len(speed_range) <= 3:
                raise ValueError("ValueError: speed_range must have 1, 2 or 3"
                                 " elements")
            for elem in speed_range:
                if not isinstance(elem, int):
                    raise TypeError("TypeError: elements of speed_range must"
                                    " be integers")

        for i in range(num_asteroids):
            asteroid = Asteroid(random.choice(self.asteroid_filenames),
                                self.asteroid_image_scale)

            asteroid.set_random_offscreen_location(self.width, self.height)

            asteroid.set_speed_in_range(speed_range)

            asteroid.set_random_spin()

            # Set random target point for asteroid across screen
            asteroid.set_random_cross_screen_target(self.width, self.height)

            self.asteroid_list.append(asteroid)

    def make_enemy_ships(self, num_enemies: int,
                         speed_range: Union[int, Tuple[int], Tuple[int, int],
                                            Tuple[int, int, int]]) -> None:

        # Validate parameters
        if not isinstance(num_enemies, int):
            raise TypeError("TypeError: num_enemies must be an int")
        if num_enemies <= 0:
            raise ValueError("ValueError: num_enemies must be positive")
        if not isinstance(speed_range, (int, tuple)):
            raise TypeError("TypeError: speed_range must be an int or tuple")
        if isinstance(speed_range, tuple):
            if not 1 <= len(speed_range) <= 3:
                raise ValueError("ValueError: speed_range must have 1, 2 or 3"
                                 " elements")
            for elem in speed_range:
                if not isinstance(elem, int):
                    raise TypeError("TypeError: elements of speed_range must"
                                    " be integers")

        for i in range(num_enemies):
            # Pass laser list to enemy so enemy can fill it
            # Use the first image for levels 1 and 2, then switch for level 3
            # noinspection PyTypeChecker
            enemy = EnemyShip(self.level_settings['enemy ship'][self.level],
                              self.enemy_ship_image_scale,
                              self.enemy_ship_image_rotation,
                              self.enemy_laser_filename,
                              self.enemy_laser_image_scale,
                              self.enemy_laser_image_rotation,
                              self.enemy_laser_list,
                              laser_fade_rate=self.level_settings[
                                  'enemy laser fade'][self.level],
                              laser_sound=self.enemy_laser_sound)

            enemy.set_random_offscreen_location(self.width, self.height)

            enemy.set_speed_in_range(speed_range)

            enemy.laser_speed = max(3 * enemy.speed, 50)

            self.enemy_list.append(enemy)

    # TODO: ASK I THINK these and other window methods return None since I
    #  don't return anything, but there's some weird stuff going on with
    #  these inherited methods, like how on_update gets called with
    #  delta_time
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

    def on_update(self, delta_time: float = 1 / 60):
        """
        Main game logic
        """

        # Validate parameters
        if not isinstance(delta_time, (int, float)):
            raise TypeError("TypeError: delta_time must be numeric")
        if delta_time < 0:
            raise ValueError("ValueError: delta_time must be non-negative")

        # Check whether or not the player should level up and whether or not
        # they die before anything else because if either happens, everything
        # else gets reset and there's no point in updating movement that will
        # get reset

        # Do first so if player gets enough points to win as they get killed,
        # they still win. If they're already dying, they don't get to level up
        if not self.dying:
            self.update_level_based_on_points()

        # Check player collisions before player laser collisions so in the
        # case of the player and a laser both hitting a asteroid, the player
        # dies. Can't die while leveling up
        if not self.leveling_up:
            self.update_lives_based_on_hits()

        # Increment count of updates this level after level_up_if_points()
        # that calls setup, which returns to it, which returns to on_update,
        # which then continues, and we want to count this update
        self.updates_this_level += 1

        # Check collisions

        # Check collisions before moving sprites so on_draw  (and the player
        # seeing sprite positions) happens between sprites hitting each other
        # and getting deleted. Otherwise, sprites could be deleted based on
        # their new positions without those positions ever being drawn
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
                # If hasn't played sound and there is sound to play
                if not self.level_up_player and self.level_up_sound:
                    self.level_up_player = self.level_up_sound.play()
                # Slightly delay switch to next level so last explosions can
                # play out at this level
                if self.leveling_up is True and self.switch_delay == 30:
                    self.level += 1
                    self.setup()
                else:
                    self.leveling_up = True
                    self.switch_delay += 1
            else:
                # TODO DEFENSIVE CODING FOR ALL SOUNDS
                # Since background_music_player is None unless sound has been
                # played, if it is True, then background_music_player is True
                if (self.background_music_player
                        and self.background_music_sound.is_playing(
                            self.background_music_player)):
                    self.background_music_sound.stop(
                        self.background_music_player)

                # If hasn't played sound and there is sound to play
                if not self.win_player and self.win_sound:
                    self.win_player = self.win_sound.play()
                # Slightly delay switch to win screen so last explosions can
                # play out at this level
                if self.leveling_up is True and self.switch_delay == 30:
                    won_view = GameWonView(self.win_player, self.win_sound)
                    self.window.show_view(won_view)
                else:
                    self.leveling_up = True
                    self.switch_delay += 1

    def update_lives_based_on_hits(self) -> None:
        # If the player collides with any other sprite, they die
        # Use sprite list to check instead of self.player_sprite so that
        # collisions don't get checked if player dies and is removed from list

        if not self.dying:
            hits = []
            for player in self.player_list:
                h = arcade.check_for_collision_with_lists(
                    player, [self.asteroid_list, self.enemy_laser_list,
                             self.enemy_list])
                hits += h

            if hits:
                self.explosion_list.append(Explosion(
                    self.explosion_textures, self.player_sprite.center_x,
                    self.player_sprite.center_y, self.explosion_image_scale,
                    self.explosion_sound))

                for hit in hits:
                    hit.remove_from_sprite_lists()

                self.player_sprite.remove_from_sprite_lists()

                self.dying = True

        if self.dying:
            # If lives left, restart level
            if self.lives >= 1:
                # If hasn't played sound
                if not self.lost_life_player and self.lost_life_sound:
                    self.lost_life_player = self.lost_life_sound.play()

                # Slightly delay reset of level so last explosions can
                # play out
                if self.switch_delay == 60:
                    # Decrement lives left
                    self.lives -= 1
                    self.setup()
                else:
                    self.dying = True
                    self.switch_delay += 1

            # If out of lives go to ending screen
            else:
                # Since background_music_player is None unless sound has been
                # played, if it is True, then background_music_player is True
                if (self.background_music_player
                        and self.background_music_sound.is_playing(
                            self.background_music_player)):
                    self.background_music_sound.stop(
                        self.background_music_player)

                # If hasn't played sound and there is a sound to play
                if not self.game_over_player and self.game_over_sound:
                    self.game_over_player = self.game_over_sound.play()

                # Slightly delay switch to game over view so last explosions
                # can play out at this level
                if self.switch_delay == 60:
                    # Go to game over screen
                    game_lost_view = GameLostView()
                    self.window.show_view(game_lost_view)
                else:
                    self.dying = True
                    self.switch_delay += 1

    def update_points_based_on_strikes(self) -> None:
        # Check player laser collisions
        # Lists to track hit asteroids and enemies separately for scoring
        asteroids_hit = []
        enemies_hit = []

        # There's not a method to check for collisions between one SpriteList
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

                # Add these hit asteroids and enemies to lists of all hit
                # asteroids
                # and enemies
                asteroids_hit += a
                enemies_hit += e

        # Add points for each hit
        self.points += self.asteroid_points * len(asteroids_hit)
        self.points += self.enemy_points * len(enemies_hit)

        # Remove hit sprites. Leave explosions where they were
        self.remove_and_explode(asteroids_hit)
        self.remove_and_explode(enemies_hit)

    def remove_and_explode(self, sprite_list):
        """
        Removes all sprites from list, leaving explosions where they were.
        """

        # Validate parameters
        if not isinstance(sprite_list, arcade.SpriteList):
            raise TypeError("TypeError: sprite_list must be an "
                            "arcade.SpriteList")

        for sprite in sprite_list:
            self.explosion_list.append(Explosion(self.explosion_textures,
                                                 sprite.center_x,
                                                 sprite.center_y,
                                                 self.explosion_image_scale,
                                                 self.explosion_sound))
            sprite.remove_from_sprite_lists()

    def update_player_sprite_based_on_input(self) -> None:
        # Update player change_movement based on key presses
        # Default to no movement if keys aren't pressed
        self.player_sprite.change_angle = 0
        self.player_sprite.speed = 0

        # TODO: ASK -- why isn't this working for
        #  Issue where if L and U are pressed, D won't stop U/D movement

        # If opposite keys are pressed, movement shouldn't occur
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_angle = -self.player_sprite.angle_rate
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_angle = self.player_sprite.angle_rate
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.speed = self.player_sprite.forward_rate
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.speed = -self.player_sprite.forward_rate

        # Update player sprite's shooting attribute to match whether space
        # is pressed
        self.player_sprite.shooting = self.space_pressed

    # Although the code for refilling asteroids and enemies is almost
    # identical, it didn't seem practical to create a more generic function
    # that could be called once for each because the method would require
    # several parameters that, including ones that are passed by value, not
    # by reference, so so much extra code would have to be written to support
    # that generic refilling function that the result would be longer and
    # less clear than this method.
    def refill_asteroids_and_enemies(self) -> None:
        """
        Refill asteroids and enemies to starting number for level. Spawn
        replacements at the speed of their spawn rate.
        """
        # If there are asteroids on level, refill to starting num on interval
        if self.level_settings['starting asteroids'][self.level] > 0:
            if self.asteroids_spawning > 0:
                self.asteroids_spawning -= 1
            else:
                self.make_asteroids(1,
                                    self.level_settings[
                                        'asteroid speed range'][self.level])
                self.asteroids_spawning = 60 // self.level_settings[
                    'asteroid spawn rate'][self.level]

        # If there are enemies on level, refill to starting num on interval
        if self.level_settings['starting enemies'][self.level] > 0:
            if self.enemies_spawning > 0:
                self.enemies_spawning -= 1
            else:
                self.make_enemy_ships(1,
                                      self.level_settings[
                                          'enemy speed range'][self.level])
                self.enemies_spawning = 60 // self.level_settings[
                    'enemy spawn rate'][self.level]

    def set_targets_for_enemies(self) -> None:
        # Set enemies' new target point as player's current (soon-to-be-old)
        # location
        if len(self.player_list) >= 1:
            for enemy in self.enemy_list:
                enemy.set_target(self.player_sprite.center_x,
                                 self.player_sprite.center_y)

        # If player is dead, make enemies stop shooting and pause, then
        # retreat backwards slowly
        if len(self.player_list) == 0:
            for enemy in self.enemy_list:
                # Stop shooting
                enemy.reload_time = None
                # Pause before retreating.
                # Only visible if this delay is less than the time to restart
                # the level.
                # I don't want it visible now, but I want the ability to make
                # it visible in the future.
                if self.switch_delay > 60:
                    if enemy.speed >= 0:
                        enemy.speed -= 10
                    elif enemy.speed > -100:
                        enemy.speed *= 1.2

    # TODO: ASK Not sure about return values....I don't call this function
    def on_key_press(self, symbol: int, modifiers: int) -> None:

        # Validate parameters
        if not isinstance(symbol, int):
            raise TypeError("TypeError: symbol must be an integer")
        if not isinstance(modifiers, int):
            raise TypeError("TypeError: modifiers must be an integer")

        # Gracefully quit program
        if symbol == arcade.key.W and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            arcade.close_window()

        # Restart program
        if symbol == arcade.key.R and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            self.points = 0
            self.level = 0
            self.setup()

        # Pause game
        if symbol == arcade.key.T and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            pause = PauseView(self)
            self.window.show_view(pause)

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
            self.lives = 2
            self.points = 0
            self.setup()

        if symbol == arcade.key.KEY_2 and modifiers == arcade.key.MOD_COMMAND:
            self.level = 1
            self.lives = 2
            self.points = self.level_settings['points goal'][0]
            self.setup()

        if symbol == arcade.key.KEY_3 and modifiers == arcade.key.MOD_COMMAND:
            self.level = 2
            self.lives = 2
            self.points = self.level_settings['points goal'][1]
            self.setup()

        # Super cheat for getting to level three with only a few more points
        # needed to win
        if symbol == arcade.key.KEY_4 and modifiers == arcade.key.MOD_COMMAND:
            self.level = 2
            self.lives = 2
            self.points = self.level_settings['points goal'][2] - 15
            self.setup()

    def on_key_release(self, symbol: int, modifiers: int) -> None:

        # Validate parameters
        if not isinstance(symbol, int):
            raise TypeError("TypeError: symbol must be an integer")
        if not isinstance(modifiers, int):
            raise TypeError("TypeError: modifiers must be an integer")

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
        return ("<GameView: width = {}, height = {}, player_location = {},"
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


class FadingView(arcade.View):
    def __init__(self, fade_rate: int, alpha: int):

        # Validate parameters
        if not isinstance(fade_rate, int):
            raise TypeError("TypeError: fade_rate must be an integer")
        if fade_rate < 0:
            fade_rate = 0
        elif fade_rate > 255:
            fade_rate = 255
        if not isinstance(alpha, int):
            raise TypeError("TypeError: alpha must be an integer")
        if alpha < 0:
            alpha = 0
        elif alpha > 255:
            alpha = 255

        super().__init__()

        self.alpha = alpha
        self.fade_rate = fade_rate

    def fade_in(self) -> bool:
        self.alpha += self.fade_rate
        if self.alpha >= 255:
            self.alpha = 255
            return True
        else:
            return False

    def fade_out(self) -> bool:
        self.alpha -= self.fade_rate
        if self.alpha <= 0:
            self.alpha = 0
            return True
        else:
            return False

    def __str__(self) -> str:
        return ("<FadingView: window_width = {}, window_height = {},"
                " alpha = {}, fade_rate = {}>".format(self.window.width,
                                                      self.window.height,
                                                      self.alpha,
                                                      self.fade_rate))


class TitleView(FadingView):
    def __init__(self, game_view: GameView):

        if not isinstance(game_view, GameView):
            raise TypeError("game_view must be an instance of GameView")

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

    def on_update(self, delta_time: float = 1 / 60) -> None:

        # Validate parameters
        if not isinstance(delta_time, (int, float)):
            raise TypeError("TypeError: delta_time must be numeric")
        if delta_time < 0:
            raise ValueError("ValueError: delta_time must be non-negative")

        if self.faded_out:
            instructions = InstructionsView(self.game_view)
            self.window.show_view(instructions)
        if not self.faded_in:
            self.faded_in = self.fade_in()
        elif self.pause_count == 0:
            self.faded_out = self.fade_out()
        else:
            self.pause_count -= 1

    def on_draw(self) -> None:
        arcade.start_render()

        black = (0, 0, 0, self.alpha)
        blue = (0, 0, 205, self.alpha)
        self.bg_colors = (black, black, black, blue)
        background = arcade.create_rectangle_filled_with_colors(self.bg_points,
                                                                self.bg_colors)

        background.draw()

        arcade.draw_text(self.title_text, self.window.width / 2,
                         self.window.height / 2, (255, 255, 255, self.alpha),
                         anchor_x="center", anchor_y="center",
                         font_size=80, align="center", bold=True,
                         width=self.window.width, multiline=True)

    def on_key_press(self, symbol: int, modifiers: int) -> None:

        # Validate parameters
        if not isinstance(symbol, int):
            raise TypeError("TypeError: symbol must be an integer")
        if not isinstance(modifiers, int):
            raise TypeError("TypeError: modifiers must be an integer")

        if symbol == arcade.key.R and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            self.window.show_view(self.game_view)

        if symbol == arcade.key.W and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            arcade.close_window()

    def __str__(self) -> str:
        return ("<TitleView: faded_in = {}, pause_count = {}, faded_out = {},"
                " alpha = {}, fade_rate = {}>".format(self.faded_in,
                                                      self.pause_count,
                                                      self.faded_out,
                                                      self.alpha,
                                                      self.fade_rate))


class InstructionsView(FadingView):
    def __init__(self, game_view: GameView):

        if not isinstance(game_view, GameView):
            raise TypeError("game_view must be an instance of GameView")

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

    def on_update(self, delta_time: float = 1 / 60) -> None:

        # Validate parameters
        if not isinstance(delta_time, (int, float)):
            raise TypeError("TypeError: delta_time must be numeric")
        if delta_time < 0:
            raise ValueError("ValueError: delta_time must be non-negative")

        if not self.faded_in:
            self.faded_in = self.fade_in()

    def on_draw(self) -> None:
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

    def on_key_press(self, symbol: int, modifiers: int) -> None:

        # Validate parameters
        if not isinstance(symbol, int):
            raise TypeError("TypeError: symbol must be an integer")
        if not isinstance(modifiers, int):
            raise TypeError("TypeError: modifiers must be an integer")

        if symbol == arcade.key.SPACE:
            self.window.show_view(self.game_view)

        if symbol == arcade.key.R and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            self.window.show_view(self.game_view)

        if symbol == arcade.key.W and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            arcade.close_window()

    def __str__(self) -> str:
        return ("<InstructionsView: faded_in = {}, alpha = {}, fade_rate = {}"
                " game_view = {}>".format(self.faded_in, self.alpha,
                                          self.fade_rate, self.game_view))


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

    def on_draw(self) -> None:
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

        # Validate parameters
        if not isinstance(symbol, int):
            raise TypeError("TypeError: symbol must be an integer")
        if not isinstance(modifiers, int):
            raise TypeError("TypeError: modifiers must be an integer")

        # Gracefully quit program
        if symbol == arcade.key.W and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            arcade.close_window()

        # Restart program
        if symbol == arcade.key.R and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            game = GameView(*self.window.game_parameters)
            self.window.show_view(game)

        if symbol == arcade.key.W and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            arcade.close_window()

    def __str__(self) -> str:
        return "<GameLostView>"


class GameWonView(arcade.View):
    def __init__(self, player: pyglet.media.player.Player = None,
                 sound: arcade.Sound = None):

        # Validate parameters
        if not isinstance(player, pyglet.media.player.Player):
            raise TypeError("TypeError: player must be a "
                            "pyglet.media.player.Player")
        if not isinstance(sound, arcade.Sound):
            raise TypeError("TypeError: sound must be an arcade.Sound")

        super().__init__()

        arcade.set_background_color((0, 0, 0))

        self.game_won_text = "You won!"
        self.instruction_text = ("\n\nRestart with 'cmd + r' or 'ctrl + r'"
                                 "\n\nExit with 'cmd + w' or 'ctrl + w'")

        self.bg_colors = ((0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0))
        self.bg_points = ((0, 0), (self.window.width, 0),
                          (self.window.width, self.window.height),
                          (0, self.window.height))

        self.sound_player = player
        self.sound = sound

    def on_draw(self) -> None:
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

        # Validate parameters
        if not isinstance(symbol, int):
            raise TypeError("TypeError: symbol must be an integer")
        if not isinstance(modifiers, int):
            raise TypeError("TypeError: modifiers must be an integer")

        # Gracefully quit program
        if symbol == arcade.key.W and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            arcade.close_window()

        # Restart program
        if symbol == arcade.key.R and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            if self.sound_player and self.sound.is_playing(self.sound_player):
                self.sound.stop(self.sound_player)
            game = GameView(*self.window.game_parameters)
            self.window.show_view(game)

    def __str__(self) -> str:
        return "<GameWonView>"


class PauseView(arcade.View):
    def __init__(self, game_view: GameView):

        if not isinstance(game_view, GameView):
            raise TypeError("game_view must be an instance of GameView")

        super().__init__()

        self.game_view = game_view
        self.sound_time = 0

        # If music, get it's current position and stop it
        if (self.game_view.background_music_sound
                and self.game_view.background_music_player):
            if self.game_view.background_music_sound.is_playing(
                    self.game_view.background_music_player):
                self.sound_time = self.game_view.background_music_player.time
                self.game_view.background_music_sound.stop(
                    self.game_view.background_music_player)

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

    def on_draw(self) -> None:
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

        # Validate parameters
        if not isinstance(symbol, int):
            raise TypeError("TypeError: symbol must be an integer")
        if not isinstance(modifiers, int):
            raise TypeError("TypeError: modifiers must be an integer")

        # Gracefully quit program
        if symbol == arcade.key.W and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            arcade.close_window()

        # Restart program
        if symbol == arcade.key.R and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):

            game = GameView(*self.window.game_parameters)
            self.window.show_view(game)

        if symbol == arcade.key.T and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            # If music, restart it
            if (self.game_view.background_music_sound
                    and self.game_view.background_music_player):
                self.game_view.background_music_player = \
                    self.game_view.background_music_sound.play()
                # Learned from looking at arcade examples (Pyglet code)
                self.game_view.background_music_player.seek(self.sound_time)

            self.window.show_view(self.game_view)

    def __str__(self) -> str:
        return "<PauseView: game_view = {}, sound_time = {}>".format(
            self.game_view, self.sound_time)


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
    if texture_width <= 0:
        raise TypeError("texture_width must be positive")
    if not isinstance(texture_height, int):
        raise TypeError("texture_height must be an integer")
    if texture_height <= 0:
        raise TypeError("texture_height must be positive")
    if not isinstance(columns, int):
        raise TypeError("columns must be an integer")
    if columns <= 0:
        raise TypeError("columns must be positive")
    if not isinstance(num_textures, int):
        raise TypeError("num_textures must be an integer")
    if num_textures < 0:
        raise TypeError("num_textures must be non-negative")
    if not isinstance(skip_rate, int):
        raise TypeError("skip_rate must be an integer")
    if num_textures <= 0:
        raise TypeError("skip_rate must be positive")

    # List of textures (frames of an animation; ways the sprite can look, eg
    # standing facing right vs crouching)
    textures = []

    # Don't throw an error for 0 textures, but return before calling range()
    if num_textures == 0:
        return textures

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
    player_ship_data = (PLAYER_SHIPS, PLAYER_SHIP_SCALE, PLAYER_SHIP_ROTATION)
    player_laser_data = (PLAYER_LASER, PLAYER_LASER_SCALE,
                         PLAYER_LASER_ROTATION)
    enemy_ship_data = (ENEMY_SHIPS, ENEMY_SHIP_SCALE, ENEMY_SHIP_ROTATION)
    enemy_laser_data = (ENEMY_LASER, ENEMY_LASER_SCALE, ENEMY_LASER_ROTATION)
    asteroid_data = (asteroid_filenames, ASTEROID_SCALE)

    # Explosion has already been processed into list of arcade Textures
    # so it's a tuple of Textures and scale
    explosion_data = (explosion_textures, EXPLOSION_SCALE)

    # Create a window object to hold the views
    # All view objects can access it as one of their attributes without
    # being explicitly passed it as a parameter
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    game_parameters = (explosion_data, player_ship_data, player_laser_data,
                       enemy_ship_data, enemy_laser_data, asteroid_data,
                       BACKGROUND_SOUND, PLAYER_LASER_SOUND,
                       ENEMY_LASER_SOUND, EXPLOSION_SOUND, LEVEL_UP_SOUND,
                       LOST_LIFE_SOUND, WIN_SOUND, GAME_OVER_SOUND)

    # The asterisk unpacks the tuple so it's like I'm passing it 14 arguments
    game_view = GameView(*game_parameters)
    game_view.setup()
    # TODO IS THIS OKAY PRACTICE OR DO I NEED TO PASS IT AS A PARAM FROM ONE
    #  TO THE NEXT?
    # Store game_parameters as Window attribute so all view objects can access
    window.game_parameters = game_parameters
    # Start with title view, which calls the next view, which calls the next...
    title_view = TitleView(game_view)
    window.show_view(title_view)
    arcade.run()


if __name__ == "__main__":
    main()
