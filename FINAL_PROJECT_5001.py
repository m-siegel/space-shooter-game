"""
I-M Siegel

This program runs a space-shooter computer game and contains several classes
that can be imported and used by other programs to make other games.

----------------------------------------------------------------------------

The contents of this file may be split into three sections:
- Sprite classes
- View classes, and GameView
- Global variables, helper functions and main()

Sprite classes:
This program contains six classes that extend the arcade.Sprite class. These
represent 'sprites' on the screen, which include the primary elements of the
game like the player's character, enemy space ships, lasers, explosions, etc.
These sprites don't access global variables, and, with the exception of
Player sprites and EnemyShip sprites, which both create instances of Laser
sprites, the sprites don't call each other. This means that the sprites can
be imported into other programs to be used as independent elements of other
games.

View classes:
The program contains seven classes that extend the arcade.View class. These
represent the various screens that a user sees (title, instructions, main
game, game over, etc.).

These classes are interconnected (for example, a GameView may create a
PauseView object if the user hits pause, a GameLostView if the player loses,
or a GameWonView if the player wins, and each of these may create instances
of GameView). This means that, except for FadingView, these classes can't be
imported into other projects independently of each other, but most of the
View subclasses may serve as templates for title, instruction, pause, and
game over screens for other games.

GameView:
The primary logic for the game is controlled by the GameView class. This
class manages interactions between the user and the game, translates keyboard
input into sprite movement, creates sprites, tracks game levels and lives,
etc.

In this game, the user spins and moves their space ship, and tries to shoot
asteroids and enemy ships without crashing or getting shot. GameView decides
what player input leads to what action on the part of the Player sprite. It
also determines level settings, like how many asteroids or enemy ships should
appear on each level and how fast they should go, and how many points the
player needs to get in order to advance.

GameView creates instances of various Sprite subclasses and directly accesses
their attributes, meaning that it cannot be used independently of the sprites.
However, all of the View subclasses do operate independently of the program's
global variables.

Global Variables, Helper Functions, and Main:
This program's global variables and main function determine much of the look
and sound of the game. The global variables hold the data concerning which
images to use for each sprite (eg deciding if the player looks like a space
ship or a dragon), and what sounds to use for each event (lase shots,
leveling up, etc). Main collects the data from the global variables to pass
to View subclasses that run the game. The images and sounds can easily be
changed by changing the filenames stored in the global variables, and the
result will be a game with the same logic, but a different setting and feel.

----------------------------------------------------------------------------

Sources:

Arcade:
This program was built with the Arcade library, which was copyrighted by
Paul Vincent Craven and is licensed under the MIT License.
- License: https://github.com/pythonarcade/arcade/blob/maintenance/license.rst

In addition to its powerful classes, the Arcade library has many examples,
clear documentation,and accessible source code that make it easy to learn.
I spent days reading through documentation and source code, and experimenting
with the library. I learned a lot from looking at the example code, the
documentation, and by digging into the source code (including the code for
libraries, like Pyglet, that Arcade is built on). I highly recommend checking
out Arcade.
- Website: https://api.arcade.academy/en/latest/
- Documentation: https://api.arcade.academy/en/latest/arcade.html
- Examples: https://api.arcade.academy/en/latest/examples/index.html
- Github: https://github.com/pythonarcade/arcade/tree/maintenance

AtiByte:
Before downloading and digging into the Arcade code and docs, I learned the
basics of Arcade from some YouTube videos by AtiByte. The videos walked
through arcade docs and demonstated how to open arcade windows, draw shapes,
and use keyboard input.
- AtiByte's page:
https://www.youtube.com/playlist?list=PL1P11yPQAo7pPlDlFEaL3IUbcWnnPcALI

Graphics:
- Explosion graphics from https://www.explosiongenerator.com/, via Arcade
resources folder.
- Other images from Space Shooter (Redux, plus fonts and sounds) by Kenney
Vleugels (www.kenney.nl), licensed under Creative Commons.
https://kenney.nl/assets/space-shooter-redux

Sounds:
- Background music and game won music come from the Apple iMovie library.
- Other sounds come from Kenny Vleugels (www.kenney.nl), see above.
"""


# Program built with arcade library, extends arcade classes
import arcade

# Used for game logic and in some classes
import math
import random

# For type hinting
from typing import List, Tuple, Union, Optional
import pyglet


# Settings - these can be changed to alter the look and feel of the game

# Window settings
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Spin and Shoot"


# Media

# Using globals so they're easy to change if someone wants to use different
# images or sounds, or if the files are moved to have a different filepath

# Images

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

# Factor by which to grow/shrink the image, in case image needs unique scaling
PLAYER_SHIP_SCALE = IMAGE_SCALE

# Degrees images need to rotate counterclockwise to face North
PLAYER_SHIP_ROTATION = 0

# Player laser filename (one string)
PLAYER_LASER = "media/kenney_nl/spaceshooter/PNG/Lasers/laserBlue01.png"
PLAYER_LASER_SCALE = IMAGE_SCALE

# Degrees images need to rotate counterclockwise to face North
PLAYER_LASER_ROTATION = 0

# Enemy Ship filenames (2 filename strings: one for each of levels 2 and 3)
ENEMY_SHIPS = ("media/kenney_nl/spaceshooter/PNG/Enemies/enemyRed1.png",
               "media/kenney_nl/spaceshooter/PNG/Enemies/enemyRed2.png")
ENEMY_SHIP_SCALE = IMAGE_SCALE

# Degrees to rotate counterclockwise to face East
ENEMY_SHIP_ROTATION = 90

# Used in main() to get variations on base filename using iteration
# For example, "spaceshooter/PNG/Meteors/meteorBrown_big3.png"
# NOTE: main expects 4 files named big 1-4, 2 files names med, 2 named small,
# and 2 named tiny
# If make changes to this, must also change main
ASTEROID_FILENAME_BASE = ("media/kenney_nl/spaceshooter/PNG/"
                          "Meteors/meteorBrown_{}.png")
ASTEROID_SCALE = 1

# Enemy laser filename (one string)
ENEMY_LASER = "media/kenney_nl/spaceshooter/PNG/Lasers/laserRed01.png"
ENEMY_LASER_SCALE = IMAGE_SCALE

# Degrees to rotate counterclockwise to face East
ENEMY_LASER_ROTATION = -90

# Explosion textures are stored in a grid in a spritesheet
# As long as this is replaced with another spritesheet grid, main doesn't need
# to be adjusted
EXPLOSION_FILE = {"filename": "media/explosion.png", "texture_width": 256,
                  "texture_height": 256, "columns": 16,
                  "num_textures": 221}
EXPLOSION_SCALE = 1

# If the spritesheet has many textures, you may only want to include a
# fraction of them to speed up animation
# Since the file has so many textures, only include one out of every two
# for a shorter animation
EXPLOSION_SKIP_RATE = 2

# Sound files
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
    Player inherits from arcade.Sprite to represent the player
    onscreen. Makes use of arcade.Sprite attributes and methods, and
    ability to be placed in an arcade.SpriteList to update (move or change)
    the sprite's position in response to player input and interactions with
    other sprites, check collisions with other sprites, draw the sprite on
    the screen, etc.

    Attributes:
    (These are the attributes that I create or inherit and use for Player.
    For other arcade.Sprite attributes that Player doesn't use, see
    arcade.Sprite.)
        :angle: (numeric) Angle of the sprite (0 is North).
        :angle_rate: (numeric) Degrees the sprite can turn per second.
        :center_x: (numeric) x-coordinate of the sprite's center point on the
            screen.
        :center_y: (numeric) y-coordinate of the sprite's center point on the
            screen.
        :change_angle: (numeric) Number of degrees and direction (positive is
            counterclockwise) to change sprite's angle in on_update().
            Set equal to 0, angle_rate or -angle_rate.
        :change_x: (numeric) Number of pixels and direction (positive is
            right) to change sprite's center_x in on_update().
        :change_y: (numeric) Number of pixels and direction (positive is
            up) to change sprite's center_y in on_update().
        :diagonal_size: (numeric) Diagonal measurement of sprite in pixels.
        :forward_rate: (numeric) Like angle_rate; number of pixels to move
            sprite forward per second.
        :image_rotation: (numeric) Degrees that the original sprite image
            needs to be rotated to face North.
        :laser_fade_rate: (numeric) amount to subtract from laser's alpha
            (making it transparent) on each update after 60. 255 makes it
            instantly disappear; 0 makes it never disappear.
        :laser_filename: (str) Image filename for laser sprite.
        :laser_list: (arcade.SpriteList) SpriteList to which to add lasers.
            Passed by reference so can be shared between objects if needed.
        :laser_rotation: (numeric) Degrees that the original laser image
            needs to be rotated to face North.
        :laser_scale: (numeric) Size of the laser relative to source image.
        :laser_sound: (arcade.Sound) Sound to play when laser is instantiated.
        :laser_speed: (numeric) Pixels per second to move laser forward.
        :reload_ticks: (int) Updates until next laser will shoot.
        :reload_time: (int) Number of updates between lasers shot if player
            is continuously trying to shoot (holding down trigger).
        :shooting: (bool) Whether player is trying to shoot.
        :speed: (numeric) Pixels per second to move sprite forward in
            on_update. Set equal to 0, forward_rate or -forward_rate.
        :window_width: (numeric) Width of window running game.
        :window_height: (numeric) Height of window running game.
    """

    def __init__(self, image_filename: str, scale: Union[int, float],
                 image_rotation: Union[int, float], laser_filename: str,
                 laser_scale: Union[int, float],
                 laser_rotation: Union[int, float],
                 laser_list: arcade.SpriteList, window_dims: Tuple[int, int],
                 laser_fade_rate: Union[int, float] = 15,
                 laser_sound: Optional[arcade.Sound] = None):
        """
        Constructor. Creates Player object with given image data and laser
        data. Sprite's center defaults to point is at the center of the
        screen.

        :param str image_filename: Filename of sprite's source image.
        :param numeric scale: Size of the sprite relative to source image.
        :param numeric image_rotation: Degrees that the original image needs
            to be rotated counterclockwise to face North.
        :param str laser_filename: Image filename for laser sprite.
        :param numeric laser_scale: Size of the laser relative to source.
        :param numeric laser_rotation: Degrees that the original laser image
            needs to be rotated to face North.
        :param arcade.SpriteList laser_list: SpriteList to which to add
            lasers.
        :param Tuple[int, int] window_dims: Dimensions of window.
        :param numeric laser_fade_rate: amount to subtract from laser's
            alpha (making it transparent) on each update after 60. 255 makes
            it instantly disappear; 0 makes it never disappear.
        :param arcade.Sound laser_sound: Sound to play when laser is
            instantiated.
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

        # Don't raise an error too large/small fade rates, just correct them
        if laser_fade_rate < 0:
            laser_fade_rate = 0
        if laser_fade_rate > 255:
            laser_fade_rate = 255
        if laser_sound and not isinstance(laser_sound, arcade.Sound):
            raise TypeError("TypeError: laser_sound must be an arcade.Sound")

        # Call super to create sprite object at the center of the screen
        super().__init__(filename=image_filename, scale=scale,
                         center_x=window_dims[0] / 2,
                         center_y=window_dims[1] / 2)

        # Degrees the image needs to be rotated to face North
        self.image_rotation = image_rotation

        # Need to know diagonal size to completely hide sprite offscreen at
        # at any angle
        self.diagonal_size = (self.width ** 2 + self.height ** 2) ** .5

        # Rates per second, not per update (approx rates of 5 per update)
        # Attributes, not global constants, so they can be updated with level
        # changes
        self.angle_rate = 360
        self.forward_rate = 360

        # Set the sprite's initial angle to face North
        self.angle = image_rotation

        # Set starting speed
        self.speed = 0

        # The GameView's laser list, passed by reference so the Player sprite
        # can add to it, and the GameView's main logic can manipulate them
        # Learned from arcade example: sprite_bullets_periodic.py,
        # accessible in the downloaded arcade package or online at
        # (https://api.arcade.academy/en/latest/examples/
        # sprite_bullets_periodic.html#sprite-bullets-periodic
        self.laser_list = laser_list

        # Laser image data
        self.laser_filename = laser_filename
        self.laser_scale = laser_scale
        self.laser_rotation = laser_rotation - self.image_rotation

        # Laser movement data
        self.laser_fade_rate = laser_fade_rate
        self.laser_speed = 400

        # How long in updates/frames (1/60 sec) it takes player's lasers to
        # reload and shoot again if player holds down the trigger
        # Slow enough reload time that player could do it faster by
        # repeatedly hitting space, but fast enough to be fun
        self.reload_time = 10

        # Counter counting down frames since last shot
        self.reload_ticks = self.reload_time

        # If the player is trying to shoot now
        self.shooting = False

        self.laser_sound = laser_sound

        # Window dimensions
        self.window_width = window_dims[0]
        self.window_height = window_dims[1]

    def on_update(self, delta_time: float = 1 / 60) -> None:
        """
        Updates the sprite's location and angle, and shoots lasers.

        :param float delta_time:  Time since last update.
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
        """
        Updates sprite's position by changing angle, center_x and center_y
        to animate sprite. Should be called at least 30 times per second.
        Uses delta_time as a factor in setting new position and angle to
        smooth movement in case of a delay in the frequency of calls to
        on_update. Otherwise, a call to on_update with delta_time of .5
        seconds would move the sprite the same amount as a call with
        delta_time of .01.

        :param float delta_time: Time since last update.
        :return: None
        """

        # Validate parameters
        if not isinstance(delta_time, (int, float)):
            raise TypeError("TypeError: delta_time must be numeric")
        if delta_time < 0:
            raise ValueError("ValueError: delta_time must be non-negative")

        # Update angle sprite is facing (turn sprite)
        # Multiply by delta_time for smooth movement
        self.angle += self.change_angle * delta_time

        # Find change_x and change_y based on new angle (essentially a target
        # point along the direction now facing; how much to move along x- and
        # y-axes relative to each other to move along line sprite is facing).
        # Default angle is North, so target point on unit circle x-coordinate
        # (change_x) is negative sin (not positive cos) and y-coordinate
        # (change_y) is cos (not sin).
        # Learned from arcade example code sprite_move_angle.py, lines
        # 45-46, accessible in the downloaded arcade package or online at
        # (https://api.arcade.academy/en/latest/examples/
        # sprite_move_angle.html#sprite-move-angle)
        self.change_x = -math.sin(math.radians(
            self.angle - self.image_rotation))
        self.change_y = math.cos(math.radians(
            self.angle - self.image_rotation))

        # Move sprite in direction it's facing, as determined above.
        # Multiply by delta_time for smooth movement, so if an update is
        # delayed, the movement speed across the screen doesn't change
        # speed * delta time gives smooth speed, and change_x and change_y
        # determine angle of movement.
        # Learned from AtiByte's YouTube video, "Python Arcade Library p04
        # - on_update and the delta time," available at
        # (https://www.youtube.com/
        # watch?v=68NnL5NJ7zY&list=PL1P11yPQAo7pPlDlFEaL3IUbcWnnPcALI&index=5)
        self.center_x += self.change_x * self.speed * delta_time
        self.center_y += self.change_y * self.speed * delta_time

        # Let sprite go just far enough offscreen that sprite is hidden at
        # any angle (thus measuring with diagonal_size) so player feels like
        # they can get lost, but keep sprite from going far so player can
        # bring it back onto screen immediately.
        if self.center_x < -1 * self.diagonal_size / 2:
            self.center_x = -1 * self.diagonal_size / 2
        if self.center_x > self.window_width + self.diagonal_size / 2:
            self.center_x = self.window_width + self.diagonal_size / 2
        if self.center_y < -1 * self.diagonal_size / 2:
            self.center_y = -1 * self.diagonal_size / 2
        if self.center_y > self.window_height + self.diagonal_size / 2:
            self.center_y = self.window_height + self.diagonal_size / 2

    def shoot_lasers(self) -> None:
        """
        Shoot lasers if player is trying to shoot. If the player tries to
        shoot continuously (ie holding down the trigger), only shoots
        shoots periodically after reload time. If player releases trigger
        to shoot repeatedly, but not constantly, shoots has quickly as player
        can hit the trigger.

        :return: None
        """

        # Reload immediately if player isn't holding trigger
        if not self.shooting:
            self.reload_ticks = 0

        # If player is holding trigger, pause before shooting again
        elif self.shooting and self.reload_ticks <= 0:

            # Create laser object and add it to laser_list
            # Laser's initial position and angle are the same as Player's
            # current position and angle. Find Laser's absolute angle based
            # on Player's angle and laser_rotation.
            self.laser_list.append(Laser(self.center_x, self.center_y,
                                         self.laser_filename, self.laser_scale,
                                         angle=(self.angle
                                                + self.laser_rotation),
                                         speed=self.laser_speed,
                                         fade_rate=self.laser_fade_rate,
                                         sound=self.laser_sound))

            # Reset reload time after shooting
            self.reload_ticks = self.reload_time

        # If player is holding down trigger and reload_time updates haven't
        # elapsed, count down another tick.
        else:
            self.reload_ticks -= 1

    def __str__(self) -> str:
        """
        Returns string representation of Player object.

        :return str: String representation of Player object.
        """
        return ("<Player: center_x = {}, center_y = {}, speed = {}, "
                "angle = {}, change_x = {}, change_y = {}>".format(
                    self.center_x, self.center_y, self.speed, self.angle,
                    self.change_x, self.change_y))


class Laser(arcade.Sprite):
    """
    Laser inherits from arcade.Sprite to represent lasers onscreen. Lasers
    are instantiated a a given location and angle, and move forward from their
    starting position. Depending upon its fade_rate, a laser may fade and
    disappear at different rates.

    Attributes (that are used here):
        :alpha: (numeric) Transparency of the sprite. 255 is completely
            visible, 0 is invisible
        :center_x: (numeric) x-coordinate of the sprite's center point on the
            screen.
        :center_y: (numeric) y-coordinate of the sprite's center point on the
            screen.
        :change_x: (numeric) Number of pixels and direction (positive is
            right) to change sprite's center_x in on_update().
        :change_y: (numeric) Number of pixels and direction (positive is
            up) to change sprite's center_y in on_update().
        :fade_rate: (numeric) amount to subtract from sprite's alpha
            (making it transparent) on each update after 60. 255 makes it
            instantly disappear; 0 makes it never disappear.
        :frames: (int) Number of updates since sprite's initialization.
        :player: (pyglet.media.player.Player) Sound player for playing sound.
        :sound: (arcade.Sound) Sound to play when laser is instantiated.
        :speed: (numeric) Pixels per second to move sprite forward in
            on_update. Set equal to 0, forward_rate or -forward_rate.
    """

    def __init__(self,  x: Union[int, float], y: Union[int, float],
                 image_filename: str, scale: Union[int, float],
                 angle: Union[int, float] = 0, speed: Union[int, float] = 200,
                 fade_rate: Union[int, float] = 0,
                 sound: Optional[arcade.Sound] = None):
        """
        Constructor.
        Creates instance of Laser at given point, facing given direction
        and starts playing sound. Sets sprite's speed and fade_rate.

        :param numeric x: X-coordinate of sprite's starting center point.
        :param numeric y: Y-coordinate of sprite's starting center point.
        :param str image_filename: Filename of sprite's source image.
        :param numeric scale: Size of the sprite relative to source image.
        :param numeric angle: Sprite's angle.
        :param numeric speed: Sprite's movement speed in pixels per second.
        :param numeric fade_rate: Amount to subtract from sprite's alpha
            (making it transparent) on each update after 60. 255 makes it
            instantly disappear; 0 makes it never disappear.
        :param arcade.Sound sound: Sound to play when laser is instantiated.
        """

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

        # Call super to create sprite at given location, angle and scale.
        super().__init__(filename=image_filename, scale=scale, center_x=x,
                         center_y=y, angle=angle, )

        # Sprite's movement speed
        self.speed = speed

        # Set movement angle based on angle sprite's facing.
        # self.angle is initialized in super's __init__()
        self.change_x = -math.sin(math.radians(self.angle))
        self.change_y = math.cos(math.radians(self.angle))

        # Frames since initialization
        self.frames = 0

        # How quickly the laser should disappear
        self.fade_rate = fade_rate

        # If there is a sound, play it once when laser is created
        self.sound = sound
        self.player = None
        if self.sound:
            self.player = sound.play()

    def on_update(self, delta_time: float = 1 / 60) -> None:
        """
        Updates the sprite's location based on speed and delta_time.

        :param float delta_time:  Time since last update.
        :return: None
        """

        # Validate parameters
        if not isinstance(delta_time, (int, float)):
            raise TypeError("TypeError: delta_time must be numeric")
        if delta_time < 0:
            raise ValueError("ValueError: delta_time must be non-negative")

        # Increment count of updates/frames since Laser was instantiated
        self.frames += 1

        # Always move in the same direction at the same rate
        self.center_x += self.change_x * self.speed * delta_time
        self.center_y += self.change_y * self.speed * delta_time

        # Remove very faint lasers
        # (feels weird to destroy an obstacle with almost invisible laser)
        if self.alpha <= 20:
            self.remove_from_sprite_lists()

        # Fade player_lasers out after firing
        if self.frames > 60:

            # alpha can't be less than 0
            try:
                self.alpha -= self.fade_rate

            # Remove sprites once their alpha is less than 0
            except ValueError:
                self.remove_from_sprite_lists()

        # Start fading more slowly than eventual fade rate 10 updates before
        elif self.frames > 50:
            try:
                self.alpha -= self.fade_rate // 3
            except ValueError:
                self.remove_from_sprite_lists()

    def __str__(self) -> str:
        """
        Returns string representation of Player object.

        :return str: String representation of Player object.
        """
        return ("<Laser: center_x = {}, center_y = {}, speed = {}, "
                "change_x = {}, change_y = {}, fade_rate = {}>".format(
                    self.center_x, self.center_y, self.speed, self.change_x,
                    self.change_y, self.fade_rate))


class TargetingSprite(arcade.Sprite):
    """
    Inherits from arcade.Sprite. Generic class for representing non-player
    sprites onscreen, giving them directed motion. Facilitates randomization
    of starting locations, speed, target, etc. to give variety to a group of
    TargetingSprites. Superclass for Asteroid and EnemyShip classes.

    A TargetingSprite has a target point that it always moves toward. This
    point may be updated to make the sprite follow the player, the mouse, or
    any another sprite, or it may stay the same to have the sprite move in
    a single direction.

    To facilitate variety in TargetingSprites instantiated en masse, the class
    allows for specific or random values to be set for location, speed, etc.
    TargetingSprites may be given specific initial locations, or they may be
    given random offscreen locations using set_random_offscreen_location().
    They may be given specific targets, or random targets offscreen.
    Offscreen targets may be entirely random, set with set_target() and
    get_random_offscreen_point(), or, if the sprite is currently offscreen,
    a target point may be randomly chosen such that the sprite will have to
    visibly cross the screen to reach it (set_random_cross_screen_target()).
    Sprites may be given exact speeds or spins, or random ones within a given
    range.

    This class does not change the sprite's angle to face the target point.
    That's intentional because it allows subclasses to add that capability if
    they need it, but doesn't force it on subclasses that don't want it.

    Attributes:
    These are just the ones that TargetingSprite actively uses. It has
    others that it inherits from arcade.Sprite.
        :angle: (numeric) Angle of the sprite (0 is East).
        :center_x: (numeric) x-coordinate of the sprite's center point on the
            screen.
        :center_y: (numeric) y-coordinate of the sprite's center point on the
            screen.
        :change_angle: (numeric) Number of degrees and direction (positive is
            counterclockwise) to change sprite's angle in on_update().
        :change_x: (numeric) Number of pixels and direction (positive is
            right) to change sprite's center_x in on_update().
        :change_y: (numeric) Number of pixels and direction (positive is
            up) to change sprite's center_y in on_update().
        :diagonal: (numeric) Diagonal measurement of sprite in pixels.
        :image_rotation: (numeric) Degrees that the original sprite image
            needs to be rotated to face East.
        :speed: (numeric) Pixels per second to move sprite forward in
            on_update. Set equal to 0, forward_rate or -forward_rate.
        :target_x: (numeric) X-coordinate of target point.
        :target_y: (numeric) Y-coordinate of target point.
    """

    def __init__(self, image_filename: str, scale: Union[int, float],
                 file_rotation: int = 0,  target_x: Union[int, float] = 0,
                 target_y: Union[int, float] = 0):
        """
        Constructor. Creates object and sets target.

        Sprite's location defaults to (0, 0), which is the bottom left corner
        in an Arcade window. To have the sprite appear at any other location,
        set the location after instantiating the sprite, either by explicitly
        setting center_x and center_y or with set_random_offscreen_location().

        :param str image_filename: Filename of sprite's source image.
        :param numeric scale: Size of the sprite relative to source image.
        :param numeric file_rotation: Degrees that the original image needs
            to be rotated counterclockwise to face East.
        :param numeric target_x: X-coordinate of target point.
        :param numeric target_y: Y-coordinate of target point.
        """

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

        # Super's __init__() creates a sprite whose center is at (0, 0)
        # I don't change that because where subclasses may want their sprites
        # to always appear at a different point, or to appear at random
        # points. Since there's no one location that's better to set than
        # (0, 0), I just keep the super's default.
        super().__init__(filename=image_filename, scale=scale)

        # Since the superclass has attributes center_x, change_x, etc., and
        # I don't want to assign values to them other than the defaults, I
        # don't initialize them again here.

        # Initialize speed and target point. These are easily changed after
        # instantiation, but need to be created here in order to exist.
        self.speed = 0
        self.target_x = target_x
        self.target_y = target_y

        # In case image source needs to be rotated to face right way
        self.image_rotation = file_rotation

        # Largest measurement for the sprite. Used to determine if can be
        # seen offscreen at any angle
        self.diagonal = int((self.width ** 2 + self.height ** 2) ** .5)

    def on_update(self, delta_time: float = 1 / 60) -> float:
        """
        Move sprite towards target point at rate of self.speed per second.
        Returns angle from sprite's current point to target point. Angle is
        measured in radians, counterclockwise from East.

        :param float delta_time: Time since last update.
        :return float angle_rad: Angle in radians from sprite's location to
            target point. Measured counterclockwise from East.
        """

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

            # Degree from sprite's center to target, in radians.
            # Angle between -pi and pi, formed by pos x axis and vector to
            # target. Handles situations that would raise ZeroDivisionError
            # with math.tan
            angle_rad = math.atan2(y_distance, x_distance)

            # Since angle's initial side is pos x axis, use normal trig
            # functions to find changes in x and y per unit of 1
            # Note: math trig functions need angles in radians
            self.change_x = math.cos(angle_rad)
            self.change_y = math.sin(angle_rad)

            # Arcade's sprite has methods to do something similar to this
            # (getting the change in x and y from the angle and updating
            # sprite's position), but it doesn't factor in delta_time

            # Factor in rate per second (speed * delta_time) to changes in
            # x and y
            self.change_x *= self.speed * delta_time
            self.change_y *= self.speed * delta_time

        # If at target point, don't move, but get current angle in radians
        # to return.
        else:

            # Undo image_rotation to calculate absolute angle from East
            # since math.atan2() calculated and without image rotation
            angle_rad = math.radians(self.angle - self.image_rotation)

        # Move to target if within range, otherwise move towards target
        # Set new center_x
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
        """
        Set target coordinates for sprite.

        :param numeric x: X-coordinate of target point.
        :param numeric y: Y-coordinate of target point.
        :return: None
        """

        # Validate parameters
        if not isinstance(x, (int, float)):
            raise TypeError("TypeError: x must be a numeric type")
        if not isinstance(y, (int, float)):
            raise TypeError("TypeError: y must be a numeric type")

        # Set target
        self.target_x = x
        self.target_y = y

    def get_random_offscreen_point(self, screen_width: Union[int, float],
                                   screen_height: Union[
                                       int, float]) -> Tuple[int, int]:
        """
        Returns the coordinates of a pseudorandom point offscreen. Point is
        not far offscreen, but far enough to hide sprite at any angle.

        Currently used by set_random_offscreen_location(), and by
        set_random_offscreen_target() but can easily be used by other methods.

        :param numeric screen_width: Width of arcade.Window displaying sprite.
        :param numeric screen_height: Height of arcade.Window.
        :return Tuple[int, int]: Coordinates of offscreen point (x, y).
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

        # Convert measurements to ints to use in random.randrange
        # Always round up to be sure sprite can be invisible at return point
        screen_width = math.ceil(screen_width)
        screen_height = math.ceil(screen_height)
        sprite_diagonal = math.ceil(self.diagonal)

        # Get coordinates of random point offscreen by getting a random
        # x and a corresponding y that makes it work

        # x can be anywhere in the range from one half of the screen width
        # to the left of the screen to one half of the screen width to the
        # right
        # Use integer division because randrange only takes ints
        x = random.randrange(screen_width // -2, 3 * screen_height // 2)

        # If x coordinate is within range of visible x's (ie anywhere within
        # the screen's width or half a diagonal measurement of the sprite
        # beyond the screen), place y-coordinate offscreen
        if -sprite_diagonal // 2 <= x <= screen_width + sprite_diagonal // 2:

            # How far away from edge of screen y will be
            y_offset = random.randrange(sprite_diagonal, 5 * sprite_diagonal)

            # Whether y will be above or below screen
            y_sign = random.choice([1, -1])

            # Place y above or below edge of screen
            if y_sign > 0:
                y = screen_height + y_offset
            else:
                y = -y_offset

        # If x-coordinate is offscreen, place y-coordinate within,
        # range of visible y-coordinates, or a little beyond
        else:
            y = random.randrange(-sprite_diagonal,
                                 screen_height + sprite_diagonal)

        return x, y

    def set_random_offscreen_location(self, screen_width: Union[int, float],
                                      screen_height: Union[
                                          int, float]) -> None:
        """
        Sets sprite's location to random point offscreen point such that
        sprite won't be visible.

        :param numeric screen_width: Width of arcade.Window displaying sprite.
        :param numeric screen_height: Height of arcade.Window.
        :return: None
        """

        # Get random int tuple representing offscreen point
        # Don't need to validate parameters here because
        # get_random_offscreen_point validates exactly as this would
        point = self.get_random_offscreen_point(screen_width, screen_height)

        # Set sprite's center coordinates to match point
        self.center_x = point[0]
        self.center_y = point[1]

    @staticmethod
    def get_random_in_range(num_range: Union[int, Tuple[int], Tuple[int, int],
                                             Tuple[int, int, int]]) -> int:
        """
        Returns a random number within the given range. This range is more
        flexible than the Python range() function, but its elements serve the
        same purpose: (start, stop, step). If only start is given, if start
        and stop are equal, or if the step is 0, then the return value will
        be equal start. Otherwise, it will return a random number within the
        given range. Ranges like (5, -3, 2), which are invalid for other range
        functions, will be rearranged to be valid, for example, (5, -3, 2) -->
        (5, -3, -2).

        Used by class for set_speed_in_range() and set_random_spin(), but
        can be used by other methods in this class, or other classes and
        functions as well.

        :param int or int tuple num_range: Range of integers to choose from.
        :return int: Pseudorandom integer.
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
        # because the start and end of the range are the same, return that
        # number
        if isinstance(num_range, int):
            return num_range
        if len(num_range) == 1 or num_range[0] == num_range[1]:
            return num_range[0]

        # Set step
        if len(num_range) == 2:
            step = 1
        else:
            step = num_range[2]

            # If step is zero, then num_range can't be traversed, so return
            # the first number in the range
            if step == 0:
                return num_range[0]

        # The range from num_range[0] to num_range[1] must be able to be
        # traversed using the step size. Can only get from smaller number to
        # bigger number with positive steps, or from bigger to smaller using
        # negative steps. If the sign of the step doesn't match the given
        # range, change the sign of the step to make the range traversable
        if not ((num_range[0] < num_range[1] and step > 0)
                or num_range[0] > num_range[1] and step < 0):
            step *= -1

        # Return random number in range
        return random.randrange(num_range[0], num_range[1], step)

    def set_speed_in_range(self,
                           speed_range: Union[int, Tuple[int], Tuple[int, int],
                                              Tuple[int, int, int]]) -> None:
        """
        Sets the sprites speed to a random number within the given range.
        Note: this method allows for negative speeds. That's intentional
        since later extensions may want the ability to move away from targets.

        :param int or int tuple speed_range: Range of integer speeds to
            choose from.
        :return: None
        """

        # Don't validate parameters here because validation is done in
        # get_random_in_range, which raises and handles the same errors this
        # would
        # Set speed to random number speed_range
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

        :param int or int tuple speed_range: Range of integer speeds to
            choose from.
        :return: None
        """

        # Don't validate parameters here because validation is done in
        # get_random_in_range, which raises and handles the same errors this
        # should
        # Set change_angle to random integer within speed_range
        self.change_angle = self.get_random_in_range(speed_range)

    def set_random_offscreen_target(self, screen_width: Union[int, float],
                                    screen_height: Union[int, float]) -> None:
        """
        Sets sprite's target to random point offscreen such that sprite won't
        be visible once it reaches that point.

        :param numeric screen_width: Width of arcade.Window displaying sprite.
        :param numeric screen_height: Height of arcade.Window.
        :return: None
        """

        # Get random offscreen point
        point = self.get_random_offscreen_point(screen_width, screen_height)

        # Set sprite's target point
        self.target_x = point[0]
        self.target_y = point[1]

    # Asteroid uses this but EnemyShip doesn't. I think it's useful to have
    # here in case other classes extend this and need to cross the screen
    def set_random_cross_screen_target(self, screen_width: Union[int, float],
                                       screen_height: Union[
                                           int, float]) -> None:
        """
        If the sprite's current location is offscreen, sets the sprite's
        target to random point across the screen. "Across the screen" means
        that the sprite will have to cross part of the screen in order to
        reach the target. Useful for making sure movement by sprites from
        one offscreen point to another is visible to the player on the screen.
        If the sprite is currently onscreen, then the target will be set to
        a random point onscreen.

        :param numeric screen_width: Width of arcade.Window displaying sprite.
        :param numeric screen_height: Height of arcade.Window.
        :return: None
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

        # Convert measurements to ints to use in random.randrange
        screen_width = math.ceil(screen_width)
        screen_height = math.ceil(screen_height)
        sprite_diagonal = math.ceil(self.diagonal)

        # If the sprite's current x is on one side or the other of the screen,
        # set its target x to be on the other side. That way, when it moves
        # to the target, the sprite will have to cross from one side of the
        # screen to the other.
        if self.center_x < 0:
            self.target_x = screen_width + sprite_diagonal
        elif self.center_x > screen_width:
            self.target_x = -sprite_diagonal

        # If the current x is within the screen's width, set its target x
        # to be within the screen's width, too. Since the sprite's current
        # location should be offscreen, then the current y coordinate must
        # be above or below the screen and the target y will be set so the
        # sprite has to cross from top to bottom or bottom to top. In order
        # to make that movement visible onscreen, the x-coordinate has to
        # be set to a value within the width of the screen. Otherwise, a
        # a sprite could move from top to bottom, to the side of the screen
        # and never become visible.
        else:
            self.target_x = random.randrange(screen_width)

        # If the sprite's center y value is offscreen, set its target value
        # offscreen on the other side so it must cross.
        if self.center_y < 0:
            self.target_y = screen_height + sprite_diagonal
        elif self.center_y > screen_height:
            self.target_y = -sprite_diagonal

        # If the y value is currently visible within the screen height, then
        # make the target also within the screen's height so the sprite will
        # appear on the screen as it crosses from left to right.
        else:
            self.target_y = random.randrange(screen_height)

    def __str__(self) -> str:
        """
        Returns string representation of TargetingSprite object.

        :return str: String representation of TargetingSprite object.
        """
        return ("<TargetingSprite: center_x = {}, center_y = {}, speed = {}, "
                "target_x = {}, target_y = {}, change_x = {},"
                " change_y = {}>".format(self.center_x, self.center_y,
                                         self.speed, self.target_x,
                                         self.target_y, self.change_x,
                                         self.change_y))


class Asteroid(TargetingSprite):
    """
    Extends TargetingSprite to represent an asteroid on the screen.
    Moves across the screen from one offscreen point to another at a random
    speed and with a random spin. Disappears when it reaches its offscreen
    target.

    Makes use of many TargetingSprite attributes and methods.

    Attributes:
    These are just the ones that Asteroid actively uses. It has others
    that it inherits from TargetingSprite and arcade.Sprite.
        :angle: (numeric) Angle of the sprite (0 is East).
        :center_x: (numeric) x-coordinate of the sprite's center point on the
            screen.
        :center_y: (numeric) y-coordinate of the sprite's center point on the
            screen.
        :change_angle: (numeric) Number of degrees and direction (positive is
            counterclockwise) to change sprite's angle in on_update().
        :change_x: (numeric) Number of pixels and direction (positive is
            right) to change sprite's center_x in on_update().
        :change_y: (numeric) Number of pixels and direction (positive is
            up) to change sprite's center_y in on_update().
        :diagonal: (numeric) Diagonal measurement of sprite in pixels.
        :speed: (numeric) Pixels per second to move sprite forward in
            on_update. Set equal to 0, forward_rate or -forward_rate.
        :target_x: (numeric) X-coordinate of target point.
        :target_y: (numeric) Y-coordinate of target point.
    """

    def __init__(self, image_filename: str, scale: Union[int, float],
                 screen_width: Union[int, float],
                 screen_height: Union[int, float],
                 speed_range: Union[int, Tuple[int], Tuple[int, int],
                                    Tuple[int, int, int]]):
        """
        Constructor. Instantiate sprite at random offscreen location and set
        random cross-screen target. Set random speed in given range and
        random spin in default range.

        :param str image_filename: Filename of sprite's source image.
        :param numeric scale: Size of the sprite relative to source image.
        :param numeric screen_width: Width of arcade.Window displaying sprite.
        :param numeric screen_height: Height of arcade.Window.
        :param int or int tuple speed_range: Range for sprite's speed to fall
            in.
        """

        # Validate parameters
        if not isinstance(image_filename, str):
            raise TypeError("TypeError: image_filename must be a string")
        if not isinstance(scale, (int, float)):
            raise TypeError("TypeError: scale must be a numeric type")
        if scale <= 0:
            raise ValueError("ValueError: scale must be positive")
        if not isinstance(screen_width, (int, float)):
            raise TypeError("TypeError: screen_width must be a numeric type")
        if screen_width <= 0:
            raise ValueError("ValueError: screen_width must be positive")
        if not isinstance(screen_height, (int, float)):
            raise TypeError("TypeError: screen_height must be a numeric type")
        if screen_height <= 0:
            raise ValueError("ValueError: screen_height must be positive")
        # Don't validate speed_range because set_speed_in_range() raises and
        # handles errors in the same way I would here

        # Instantiate TargetingSprite object
        super().__init__(image_filename, scale)

        # Set random offscreen starting location and cross-screen target
        self.set_random_offscreen_location(screen_width, screen_height)
        self.set_random_cross_screen_target(screen_width, screen_height)

        # Set random speed and spin
        self.set_speed_in_range(speed_range)
        self.set_random_spin()

    def on_update(self, delta_time: float = 1 / 60) -> None:
        """
        Move sprite towards target point at rate of self.speed pixels per
        second and spin sprite at rate of change_angle degrees per update
        (60 * change_angle degrees per second).

        :param float delta_time: Time since last update.
        :return: None
        """

        # Validate parameters
        if not isinstance(delta_time, (int, float)):
            raise TypeError("TypeError: delta_time must be numeric")
        if delta_time < 0:
            raise ValueError("ValueError: delta_time must be non-negative")

        # Call super's method to move the sprite towards the target
        super().on_update(delta_time)

        # Spin asteroid sprite
        self.angle += self.change_angle

        # Eliminate asteroids once they disappear offscreen (reach target)
        if self.center_x == self.target_x and self.center_y == self.target_y:
            self.remove_from_sprite_lists()

    def __str__(self) -> str:
        """
        Returns string representation of Asteroid object.

        :return str: String representation of Asteroid object.
        """
        return ("<Asteroid: center_x = {}, center_y = {}, speed = {}, "
                "target_x = {}, target_y = {}, change_x = {},"
                " change_y = {}>".format(self.center_x, self.center_y,
                                         self.speed, self.target_x,
                                         self.target_y, self.change_x,
                                         self.change_y))


class EnemyShip(TargetingSprite):
    """
    Extends TargetingSprite to represent an enemy ship on the screen. Starts
    at a random point offscreen and always moves towards target point.
    Periodically shoots lasers towards target point. In order for target
    point to change (for example, to follow the player's sprite), the
    target's coordinates must be updated by the caller.

    Makes use of many TargetingSprite attributes and methods.

    Attributes:
    These are just the ones that Asteroid actively uses. It has others
    that it inherits from TargetingSprite and arcade.Sprite.
        :angle: (numeric) Angle of the sprite (0 is East).
        :center_x: (numeric) x-coordinate of the sprite's center point on the
            screen.
        :center_y: (numeric) y-coordinate of the sprite's center point on the
            screen.
        :change_angle: (numeric) Number of degrees and direction (positive is
            counterclockwise) to change sprite's angle in on_update().
        :change_x: (numeric) Number of pixels and direction (positive is
            right) to change sprite's center_x in on_update().
        :change_y: (numeric) Number of pixels and direction (positive is
            up) to change sprite's center_y in on_update().
        :diagonal: (numeric) Diagonal measurement of sprite in pixels.
        :image_rotation: (numeric) Degrees that the original sprite image
            needs to be rotated to face North.
        :laser_fade_rate: (numeric) amount to subtract from laser's alpha
            (making it transparent) on each update after 60. 255 makes it
            instantly disappear; 0 makes it never disappear.
        :laser_filename: (str) Image filename for laser sprite.
        :laser_list: (arcade.SpriteList) SpriteList to which to add lasers.
            Passed by reference so can be shared between objects if needed.
        :laser_rotation: (numeric) Degrees that the original laser image
            needs to be rotated to face North.
        :laser_scale: (numeric) Size of the laser relative to source image.
        :laser_sound: (arcade.Sound) Sound to play when laser is instantiated.
        :laser_speed: (numeric) Pixels per second to move laser forward.
        :reload_time: (int) Number of updates left before sprite shoots
            again. Set equal to laser_speed.
        :speed: (numeric) Pixels per second to move sprite forward in
            on_update. Set equal to 0, forward_rate or -forward_rate.
        :target_x: (numeric) X-coordinate of target point.
        :target_y: (numeric) Y-coordinate of target point.
    """

    def __init__(self, image_filename: str, scale: Union[int, float],
                 image_rotation: Union[int, float],
                 speed_range: Union[int, Tuple[int], Tuple[int, int],
                                    Tuple[int, int, int]],
                 laser_filename: str,
                 laser_scale: Union[int, float],
                 laser_rotation: Union[int, float],
                 laser_list: arcade.SpriteList,
                 laser_fade_rate: Union[int, float] = 40,
                 laser_sound: Optional[arcade.Sound] = None):
        """
        Constructor. Instantiate the sprite at default sprite location (0, 0)
        with default target point (0, 0), and a random speed. Caller must
        set a different starting location and target point after
        instantiation, either specifically or by calling
        set_random_offscreen_location(), etc. This is intentional because,
        in some situations, the caller may not want EnemyShips to appear
        randomly offscreen, so I don't want to waste time calling that
        function during __init__() to have the location be reset immediately.

        :param str image_filename: Filename of sprite's source image.
        :param numeric scale: Size of the sprite relative to source image.
        :param numeric image_rotation: Degrees that the original image needs
            to be rotated counterclockwise to face East.
        :param int or int tuple speed_range: Range of possible integer speeds
            for sprite.
        :param str laser_filename: Image filename for laser sprite.
        :param numeric laser_scale: Size of the laser relative to source.
        :param numeric laser_rotation: Degrees that the original laser image
            needs to be rotated to face East.
        :param arcade.SpriteList laser_list: SpriteList to which to add
            lasers.
        :param numeric laser_fade_rate: amount to subtract from laser's
            alpha (making it transparent) on each update after 60. 255 makes
            it instantly disappear; 0 makes it never disappear.
        :param arcade.Sound laser_sound: Sound to play when laser is
            instantiated.
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

        # Although these are validated by the laser class when instantiated,
        # I want to validate them here so an enemy doesn't get created with
        # invalid attribute values
        if not isinstance(laser_fade_rate, (int, float)):
            raise TypeError("TypeError: laser_fade_rate must be numeric")
        if laser_fade_rate < 0:
            laser_fade_rate = 0
        if laser_fade_rate > 255:
            laser_fade_rate = 255
        if laser_sound and not isinstance(laser_sound, arcade.Sound):
            raise TypeError("TypeError: laser_sound must be an arcade.Sound")

        super().__init__(image_filename, scale, file_rotation=image_rotation)

        # Set random speed for sprite
        self.set_speed_in_range(speed_range)

        # Pointer (pointer?) to game window's enemy_laser_list
        self.laser_list = laser_list

        # Laser data
        self.laser_filename = laser_filename
        self.laser_scale = laser_scale
        self.laser_sound = laser_sound
        self.laser_fade_rate = laser_fade_rate

        # Rotation of Laser source image relative to EnemyShip source image
        self.laser_rotation = laser_rotation - self.image_rotation

        # Lasers should always be faster than ships, and anything slower
        # than 50 just looks too slow. Also, if an EnemyShip's speed is
        # negative (moving away from target while facing it), it should still
        # shoot towards target
        self.laser_speed = max(3 * self.speed, 50)

        # Ships should be able to shoot the moment they're created
        self.reload_time = 0

    def on_update(self, delta_time: float = 1 / 60) -> None:
        """
        Updates the sprite's location and angle, and shoots lasers.

        :param float delta_time:  Time since last update.
        :return: None
        """

        # Validate parameters
        if not isinstance(delta_time, (int, float)):
            raise TypeError("TypeError: delta_time must be numeric")
        if delta_time < 0:
            raise ValueError("ValueError: delta_time must be non-negative")

        # Moves sprite towards target point at speed, returns angle to target
        angle_rad = super().on_update(delta_time)

        # Set angle of ship to match angle of movement, accounting for
        # source image rotation
        # This instantly turns enemies towards target instead of rotating
        # time slowly.
        self.angle = math.degrees(angle_rad) + self.image_rotation

        # If reload time is None, don't shoot any lasers. This allows for
        # non-shooting EnemyShips to exist
        if self.reload_time is None:
            return

        # Decrement reload_time and shoot laser once it reaches zero
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

            # Reset reload_time
            self.reload_time = self.laser_speed

    def __str__(self) -> str:
        """
        Returns string representation of EnemyShip object.

        :return str: String representation of EnemyShip object.
        """
        return ("<EnemyShip: center_x = {}, center_y = {}, speed = {}, "
                "target_x = {}, target_y = {}, change_x = {},"
                " change_y = {}, laser_speed = {}, reload_time = {}>".format(
                    self.center_x, self.center_y, self.speed, self.target_x,
                    self.target_y, self.change_x, self.change_y,
                    self.laser_speed, self.reload_time))


class Explosion(arcade.Sprite):
    """
    Extends arcade.Sprite to represent an animated explosion onscreen.
    An Explosion sprite has many textures (like frames in an animation),
    which the sprite swaps through to animate the explosion. The sprite
    stays in one location and then disappears once the animation is over.

    Utilizes arcade.Sprite's texture and textures attributes for animation.

    Attributes:
        This isn't a list of all attributes that Explosion has (it has manu
        inherited ones that aren't used here. These are just the attributes
        used in this class).
        :center_x: (numeric) x-coordinate of the Explosion's center point on
            the screen.
        :center_y: (numeric) y-coordinate of the Explosion's center point on
            the screen.
        :cur_texture_index: (int) Index in the textures list of the Texture
            currently assigned to self.texture.
        :scale: (numeric) Size of the explosion onscreen relative to source
            image.
        :player: (pyglet.media.player.Player) Sound player for playing sound.
        :sound: (arcade.Sound) Sound to play when Explosion is instantiated.
        :texture: (arcade.Texture) Current Texture (image) that's being
            displayed for the sprite.
        :textures: (List[arcade.Texture]) List of Textures for sprite.
    """

    def __init__(self, textures: List[arcade.Texture],
                 center_x: Union[int, float], center_y: Union[int, float],
                 scale: Union[int, float] = 1,
                 sound: Optional[arcade.Sound] = None):
        """
        Constructor.
        Creates an instance of Explosion at the given location and starts
        playing the Explosion sound.

        :param List[arcade.Texture] textures: List of Textures (like frames
            in an animation) for sprite.
        :param numeric center_x: X-coordinate of sprite's center point.
        :param numeric center_y: Y-coordinate of sprite's center point.
        :param numeric scale: Size of the sprite relative to source image.
        :param arcade.Sound sound: Sound to play when Explosion is
            instantiated.
        """

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

        # List of Textures (like frames) for animation
        self.textures = textures

        # Initialize current texture and texture index
        # Already confirmed there's at least one Texture in the list, so
        # won't get IndexErrors indexing into it
        self.cur_texture_index = 0
        self.texture = self.textures[self.cur_texture_index]

        # Set player to None in case there isn't a sound
        self.player = None

        # If there is a sound, play it once, at the start
        self.sound = sound
        if self.sound:
            self.player = sound.play()

    def update(self) -> None:
        """
        Change current texture to next Texture in textures list. After
        iterating over the list once, remove the sprite.

        :return: None
        """

        # Animate explosion
        # Make sure index is within range before indexing into the list.
        # Change current texture to the next one in the list and increment
        # index counter.
        if self.cur_texture_index < len(self.textures):
            self.texture = self.textures[self.cur_texture_index]
            self.cur_texture_index += 1

        # If finished iterating over list, remove sprite from SpriteLists.
        else:
            self.remove_from_sprite_lists()

    def __str__(self) -> str:
        """
        Returns string representation of Explosion object.

        :return str: String representation of Explosion object.
        """
        return ("<Explosion: center_x = {}, center_y = {},"
                "number of textures = {}>".format(self.center_x, self.center_y,
                                                  len(self.textures)))


# Main game logic
class GameView(arcade.View):
    """
    Represents the game screen in the open window. Contains the primary game
    logic and controls gameplay. Manages player input (translates key presses
    into sprite creation and movement). Creates sprites, updates their
    locations, angles and textures, and checks for collisions and removes
    destroyed sprites. Manages player lives, points, and leveling up, and
    calls PauseView, GameLostView and GameWonView as needed. Determines level
    settings, like the number of enemies that a player faces, their speeds and
    where they come from.

    Extends arcade.View with specifics for how this game runs. Inherits
    methods from arcade.View that make a game possible.
    For example, as a subclass of arcade.View, GameView's on_draw
    and on_update methods get called 60 times per second without my code
    explicitly doing so. This enables animation and gameplay. Similarly, the
    inherited on_key_press and on_key_release methods get called whenever
    those events occur. Arcade inherits these methods from Pyglet.

    Attributes:
        These are just the attributes used by GameView. It inherits other
        attributes from arcade.View that aren't used here. Information about
        them can be found in the Arcade documentation.

        :asteroid_filenames: (List[str]) Filenames for Asteroid sprites'
            source images.
        :asteroid_image_scale: (numeric) Size of Asteroid sprites relative to
            size of source images.
        :asteroid_list: (SpriteList) SpriteList of Asteroids.
        :asteroid_points: (int) Points player gains for each Asteroid hit.
        :asteroids_spawning: (int) Like switch_delay; number of updates
            until next Asteroid is spawned (gets decremented then reset).
        :background_music_player: (pyglet.media.player.Player) Sound player
            for playing background_music_sound.
        :background_music_sound: (arcade.Sound) Background sound for game.
        :down_pressed: (bool) Whether the down arrow key is pressed.
        :dying: (bool) Whether the player is in the process of dying.
        :enemy_laser_filename: (str) Filename for EnemyShip sprites' Laser
            source image.
        :enemies_spawning: (int) Like switch_delay; number of updates
            until next EnemyShip is spawned (gets decremented then reset).
        :enemy_laser_image_rotation: (numeric) Degrees source image needs to
            rotate clockwise to face East.
        :enemy_laser_image_scale: (numeric) Size of EnemyShip sprites' Lasers
            relative to size of source images.
        :enemy_laser_list: (SpriteList) SpriteList of EnemyShips' Lasers.
        :enemy_laser_player: (pyglet.media.player.Player) Sound player
            for playing enemy_laser_sound.
        :enemy_laser_sound: (arcade.Sound) EnemyShip's Laser firing sound.
        :enemy_list: (SpriteList) SpriteList of EnemyShips.
        :enemy_points: (int) Points player gains for each EnemyShip hit.
        :enemy_ship_filenames: (Tuple[str, str]) Filenames for EnemyShip
            sprite source images.
        :enemy_ship_image_rotation: (numeric) Degrees source images need to
            rotate clockwise to face East.
        :enemy_ship_image_scale: (numeric) Size of EnemyShip sprite relative to
            size of source images.
        :explosion_image_scale: (numeric) Size of Explosion sprite relative to
            size of source images.
        :explosion_list: (SpriteList) SpriteList of active Explosions.
        :explosion_player: (pyglet.media.player.Player) Sound player
            for playing explosion_sound.
        :explosion_sound: (arcade.Sound) Sound of Explosions.
        :explosion_textures: (List[arcade.Texture]) List of textures to
            animate Explosion sprites.
        :game_over_player: (pyglet.media.player.Player) Sound player
            for playing game_over_sound.
        :game_over_sound: (arcade.Sound) Sound when player loses the game.
        :height: (numeric) Height of the associated window.
        :left_pressed: (bool) Whether the left arrow key is pressed.
        :level: (int) The current level. Used for indexing into the tuples
            in the level_settings dictionary.
        :level_limit: (int) Maximum number of levels in the game. Since
            levels are counted starting at 0, this should be one more than
            the highest value of self.level. Used to verify that each tuple
            in level_settings is long enough to be used at each level.
        :level_up_player: (pyglet.media.player.Player) Sound player
            for playing level_up_sound.
        :level_settings: (Dict[Tuple[Union[str, int, float]]]) Dictionary
            of settings for each level:
                'points goal' - The number of points needed to beat the level.
                'player ship' - Which image file to use for the Player sprite.
                'player laser fade' - How quickly the Player's lasers fade.
                'enemy ship' - Which image file to use for EnemyShips.
                'starting enemies' - Number of EnemyShips at the start of the
                    level.
                'enemy spawn rate' - How quickly new EnemyShips spawn.
                'enemy speed range' - Speed range for EnemyShip movement.
                'enemy laser fade' - How quickly the EnemyShips' lasers fade.
                'starting asteroids' - Number of Asteroids at the start of the
                    level.
                'asteroid spawn rate' - How quickly new Asteroids spawn.
                'asteroid speed range' - Speed range for EnemyShip movement.
        :level_up_sound: (arcade.Sound) Sound of player moving to next level.
        :leveling_up: (bool) Whether the player is in the process of leveling
            up.
        :lives: (int) Number of extra lives the player has left.
        :lost_life_player: (pyglet.media.player.Player) Sound player
            for playing lost_life_sound.
        :lost_life_sound: (arcade.Sound) Sound of player losing a life.
        :player_laser_filename: (str) Filename for Player sprites' Laser
            source image.
        :player_laser_image_rotation: (numeric) Degrees source image needs to
            rotate clockwise to face North.
        :player_laser_image_scale: (numeric) Size of Player sprites' Laser
            sprites relative to size of source image.
        :player_laser_list: (SpriteList) SpriteList of Player's Lasers.
        :player_laser_player: (pyglet.media.player.Player) Sound player
            for playing player_laser_sound.
        :player_laser_sound: (arcade.Sound) Player's Laser firing sound.
        :player_list: (SpriteList) to hold the Player sprite.
        :player_ship_filenames: (Tuple[str, str, str]) Filenames for Player
            sprite source images.
        :player_ship_image_rotation: (numeric) Degrees source images need to
            rotate clockwise to face North.
        :player_ship_image_scale: (numeric) Size of Player sprite relative to
            size of source images.
        :player_sprite: (Player) the Player sprite representing the player.
        :points: (int) Number of total points the player has earned.
        :right_pressed: (bool) Whether the right arrow key is pressed.
        :space_pressed: (bool) Whether the space bar is pressed.
        :switch_delay: (int) Number of updates since leveling_up or dying
            became True. Used to delay the switch to the next level or
            to restarting this level (if the player dies) to let sound effects
            and explosions play out for a smoother-feeling transition.
        :up_pressed: (bool) Whether the up arrow key is pressed.
        :updates_this_level: (int) Number of times on_update has been called
            for the current level.
        :width: (numeric) Width of the associated window.
        :win_player: (pyglet.media.player.Player) Sound player
            for playing win_sound.
        :win_sound: (arcade.Sound) Sound when player wins the game.
        :window: (arcade.Window) Window with which this View is associated.
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
        Sets background color and assigns attributes that don't change, like
        width, height, level_settings, and all sprite image and sound data.
        Initializes attributes that change dynamically during play, like
        points, lives, and up_pressed. Also initializes attributes like
        updates_this_level and explosion_list that get reset at the beginning
        of every level. Initializes the SpriteLists to None, then calls
        setup() to fill them in and fill out the level's components based
        on the level settings.

        :param tuple explosion_textures: Tuple whole
            first element is a List of arcade.Textures to animate the
            Explosion sprites, and whose second element is the scale for those
            textures.
        :param tuple player_ship_image_files: Tuple with three elements:
            1) Three string tuple representing the source files for Player
                images,
            2) number representing size of sprite relative to source images,
            3) number representing counterclockwise degrees to rotate source
                image to face North.
        :param tuple player_laser_image_file: Tuple with three elements:
            1) String representing the source file for Player's Laser image,
            2) number representing size of sprite relative to source image,
            3) number representing counterclockwise degrees to rotate source
                image to face North.
        :param tuple enemy_ship_image_files: Tuple with three elements:
            1) Three string tuple representing the source files for
                EnemyShips' images,
            2) number representing size of sprite relative to source images,
            3) number representing counterclockwise degrees to rotate source
                image to face East.
        :param tuple enemy_laser_image_file: Tuple with three elements:
            1) String representing the source file for EnemyShips' Laser image,
            2) number representing size of sprite relative to source image,
            3) number representing counterclockwise degrees to rotate source
                image to face East.
        :param tuple asteroid_image_files: Tuple with two elements:
            1) List of strings representing the source files for Asteroids'
                images,
            2) number representing size of sprite relative to source images,
        :param str background_music: Filename of source for background_music
            sound
        :param str player_laser_sound: Filename of source for
            player_laser_sound sound
        :param str enemy_laser_sound: Filename of source for enemy_laser_sound
            sound
        :param str explosion_sound: Filename of source for explosion_sound
            sound
        :param str level_up_sound: Filename of source for level_up_sound sound
        :param str lost_life_sound: Filename of source for lost_life_sound
            sound
        :param str win_sound: Filename of source for win_sound sound
        :param str game_over_sound: Filename of source for game_over_sound
            sound
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

        # General game attributes that don't change

        # Window dimensions
        self.width = self.window.width
        self.height = self.window.height

        # Background color
        arcade.set_background_color((0, 0, 0))

        # Images - Store all sprite image, scale and rotation data

        # Pre-loaded list of arcade.Textures for explosion sprite
        self.explosion_textures = explosion_textures[0]
        self.explosion_image_scale = explosion_textures[1]

        # Filenames, scale and rotation for sprite images
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

        # No need for rotation for asteroids since they have no definite
        # direction they face, and since they spin
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

        # Game settings

        # Number of points player earns for each type of hit
        self.asteroid_points = 5
        self.enemy_points = 15

        # Highest level in the game (start counting at level 1, not 0)
        self.level_limit = 3

        # Level settings store specific settings (which ship image to
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

        # Confirm that there are settings for every level
        # self.level (below, starts at 0) is used to index into each tuple
        # in the level_settings dict, so verify that it won't try to index
        # out of bounds. self.level won't be incremented to reach
        # self.level_limit
        for key in self.level_settings:
            if len(self.level_settings[key]) < self.level_limit:
                raise ValueError("ValueError: level_settings must have {}"
                                 " elements for {}".format(self.level_limit,
                                                           key))

        # Attributes that change dynamically during play

        # Start with 0 points
        self.points = 0

        # Lives - counts down to zero (for a total of three)
        self.lives = 2

        # Whether the player is leveling up or dying. Allows for slight delay
        # in changing screen so last explosions can play out
        self.leveling_up = False
        self.dying = False

        # Counts updates after leveling_up or dying is made True to facilitate
        # slight delay before switching levels or dying
        self.switch_delay = 0

        # Which keys are pressed/held down at any given time
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.space_pressed = False

        # Used for indexing into level settings, so start at zero
        self.level = 0

        # Attributes that change based on the level and are reset at each
        # restarted level

        # Number of updates
        self.updates_this_level = 0

        # These all get assigned non-None values by the setup() function
        # when an object is created, or the player starts/restarts a level

        # For counting down updates until the next asteroid or enemy is
        # spawned
        self.asteroids_spawning = None
        self.enemies_spawning = None

        # Player sprite
        self.player_sprite = None

        # Sprite lists for each group of sprites to efficiently call the
        # same methods or do the same things to each set

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
        Sets or resets to the start of the level indicated by self.level.
        Resets updates_this_level, leveling_up, dying, and switch_delay.
        Resets sounds that are playing. Sets all attributes that hold
        SpriteLists to hold empty SpriteLists. Creates an instance of Player
        and instances of Asteroid and EnemyShip based on current level's
        settings.

        :return: None
        """

        # Number of updates since level started
        self.updates_this_level = 0

        # At new level or new life, reset
        self.leveling_up = False
        self.dying = False
        self.switch_delay = 0

        # If playing the lost life or level-up sound, stop it
        # Don't have to check that the sound exists because the only way the
        # player can exist is if the sound does
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

        # Although background_music_sound isn't an optional parameter, code
        # defensively in case a later iteration of the program makes it
        # optional
        if self.background_music_sound:

            # Restart background music
            self.background_music_player = self.background_music_sound.play(
                loop=True)

        # Set number of updates before new asteroid or enemy is spawned
        # 60 updates per second
        if self.level_settings['asteroid spawn rate'][self.level] > 0:
            self.asteroids_spawning = 60 // self.level_settings[
                'asteroid spawn rate'][self.level]
        if self.level_settings['enemy spawn rate'][self.level] > 0:
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
        # PyCharm is confused by this first element because it comes from
        # a dictionary whose first value is a tuple of ints and PyCharm thinks
        # all values from that dict are int tuples, but this is a string
        # noinspection PyTypeChecker
        self.player_sprite = Player(

            # Player ship depends upon level
            self.level_settings['player ship'][self.level],
            self.player_ship_image_scale, self.player_ship_image_rotation,
            self.player_laser_filename, self.player_laser_image_scale,
            self.player_laser_image_rotation, self.player_laser_list,
            (self.width, self.height),

            # Fade rate depends upon the level
            laser_fade_rate=self.level_settings[
                'player laser fade'][self.level],
            laser_sound=self.player_laser_sound)

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
        """
        Appends num_asteroids number of Asteroid objects that move at speeds
        within speed_range to self.asteroid_list.

        :param int num_asteroids: Number of Astroids to create.
        :param int or int tuple speed_range: Range of ints in which
            Asteroids' speeds should fall.
        :return: None
        """

        # Validate parameters
        if not isinstance(num_asteroids, int):
            raise TypeError("TypeError: num_asteroids must be an int")
        if num_asteroids < 0:
            raise ValueError("ValueError: num_asteroids must be non-negative")
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

            # This class init method makes sure there's at least one file in
            # self.asteroid_filenames. Choose random image to be asteroid in
            # order to have variety.
            self.asteroid_list.append(
                Asteroid(random.choice(self.asteroid_filenames),
                         self.asteroid_image_scale, self.width, self.height,
                         speed_range))

    def make_enemy_ships(self, num_enemies: int,
                         speed_range: Union[int, Tuple[int], Tuple[int, int],
                                            Tuple[int, int, int]]) -> None:
        """
        Appends num_enemies number of EnemyShip objects that move at speeds
        within speed_range to self.enemy_list.

        :param int num_enemies: Number of EnemyShip to create.
        :param int or int tuple speed_range: Range of ints in which
            EnemyShips' speeds should fall.
        :return: None
        """

        # Validate parameters
        if not isinstance(num_enemies, int):
            raise TypeError("TypeError: num_enemies must be an int")
        if num_enemies < 0:
            raise ValueError("ValueError: num_enemies must be non-negative")
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

            # Pass laser list to enemy so enemy can append to it
            # Use the first image for levels 1 and 2, then switch for level 3
            # noinspection PyTypeChecker
            enemy = EnemyShip(self.level_settings['enemy ship'][self.level],
                              self.enemy_ship_image_scale,
                              self.enemy_ship_image_rotation,
                              speed_range,
                              self.enemy_laser_filename,
                              self.enemy_laser_image_scale,
                              self.enemy_laser_image_rotation,
                              self.enemy_laser_list,
                              laser_fade_rate=self.level_settings[
                                  'enemy laser fade'][self.level],
                              laser_sound=self.enemy_laser_sound)

            # Set starting location offscreen
            enemy.set_random_offscreen_location(self.width, self.height)

            self.enemy_list.append(enemy)

    def on_draw(self) -> None:
        """
        Draws window background and all sprites to the screen. Gets called
        60 times a second and is the visual partner of on_update that
        displays the animated movement in the game.

        This is an inherited method and it utilizes the draw() method of
        SpriteLists, which draws all sprites in a SpriteList.

        :return: None
        """

        # This clears the screen for the following drawings to work.
        arcade.start_render()

        # Utilize arcade.SpriteList draw() method to efficiently draw sprites.

        # Drawing with SpriteList means anything outside the viewport won't
        # be drawn.
        # Put asteroids in the background.
        self.asteroid_list.draw()

        # Draw lasers before ships so lasers are covered by ships and look
        # like they're growing out from the space ships as they move.
        self.player_laser_list.draw()
        self.enemy_laser_list.draw()

        # Draw space ships above their lasers.
        self.enemy_list.draw()

        # Draw player in front of enemies, asteroids and lasers
        # If I were to draw the sprite directly, not using the list, it would
        # be drawn as long as self.player_sprite wasn't None, so I'd have to
        # set self.player_sprite to None when the player died, but trying
        # to call the draw() method on None would raise an error, so I'd
        # first have to check that self.player_sprite wasn't None. Drawing
        # with the list avoids all of that since, if there's a sprite in the
        # list, it gets drawn, and if there's no sprite in the list (after the
        # player dies), nothing gets drawn.
        self.player_list.draw()

        # Draw explosions in front of all other sprites.
        self.explosion_list.draw()

        # Draw writing last so it can be seen in front of everything.
        arcade.draw_text("Points: {}".format(self.points), 20,
                         self.height - 30, font_size=14, bold=True)
        arcade.draw_text("Level: {}".format(self.level + 1), 20,
                         self.height - 60, font_size=14, bold=True)
        arcade.draw_text("Extra Lives: {}".format(self.lives), 20,
                         self.height - 90, font_size=14, bold=True)

    def on_update(self, delta_time: float = 1 / 60) -> None:
        """
        Main game logic.
        Switches to the next level or the winning screen if the player has
        enough points. Restarts current level with or switches to game lost
        screen if player has been hit. Both processes take several updates
        to play out, for a smoother transition, so this method begins or
        continues one of the processes. Leveling up and dying are mutually
        exclusive, with leveling up taking precedence if the criteria for
        both are met at the same time.
        Updates player lives. Updates player points based on what they've
        shot. Updates Player's location and angle, and whether they're
        shooting. Spawns new Asteroids and EnemyShips as needed. Updates
        Asteroid and EnemyShips' locations, and EnemyShips' target point,
        direction they're facing, and shoots Lasers. Removes sprites that
        have collided with each other and replaces them with Explosions.
        Updates all sprites, including Laser positions and Explosion
        animations.
        Does all this by calling helper methods.

        :param float delta_time: Time since last update.
        :return: None
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

        # Increment count of updates this level after
        # update_level_based_on_points() and update_lives_based_on_hits()
        # because they call setup(), which returns to them, and they return
        # to on_update, which then continues, and I want to count this update.
        self.updates_this_level += 1

        # Check collisions for points
        # Check collisions before moving sprites so on_draw  (and the player
        # seeing sprite positions) happens between sprites hitting each other
        # and getting deleted. Otherwise, sprites could be deleted based on
        # their new positions without those positions ever being drawn
        self.update_points_based_on_strikes()

        # Update Player sprite's movement attributes based on GameView
        # attributes that track player input (like whether UP is pressed).
        self.update_player_speed_angle_change_based_on_input()

        # Spawn new asteroids and enemies as fast as their spawn_rates
        self.spawn_asteroids_and_enemies()

        # Set targets for enemy sprites
        self.set_targets_for_enemies()

        # Update all sprite lists
        # An arcade.SpriteList object has a list attribute that holds all the
        # sprites in the SpriteList. on_update() iterates through the list
        # with a for loop, calling the on_update() method of each sprite.
        # The sprites' on_update positions change their locations and angles,
        # and textures as needed, animating sprite movement.
        # See each sprite's on_update or update method for execution details.
        self.player_list.on_update(delta_time)
        self.player_laser_list.on_update(delta_time)
        self.asteroid_list.on_update(delta_time)
        self.enemy_list.on_update(delta_time)
        self.enemy_laser_list.on_update(delta_time)
        self.explosion_list.update()

    def update_level_based_on_points(self) -> None:
        """
        Checks whether the player has enough points to beat the current level.
        If so, and there's a higher level, starts or continues transition to
        the next level. If the current level is the highest in the game,
        starts or continues the transition to a GameWonView.

        The switch to a new level after meeting the criteria to level up is
        slightly delayed to allow last Explosions to play out, and to start
        the level-up or game-won sounds before changing screen. This gives
        a smoother feeling to the level transitions.

        If the criteria for leveling up or winning is met, begin the
        transition process if it has not already begun. If the transition
        is already in progress, count updates until it's time to switch
        levels and then switch.

        :return: None
        """

        # If points goal reached for this level, jump to the next one
        if self.points >= self.level_settings['points goal'][self.level]:

            # Check that the current level is not the highest in the game.
            # level is used to index into level_settings tuples, but
            # level_limit is the minimum length of those tuples, so level
            # must always be at least one less than level_settings
            if self.level < self.level_limit - 1:

                # If hasn't played sound and there is sound to play, play it.
                if not self.level_up_player and self.level_up_sound:
                    self.level_up_player = self.level_up_sound.play()

                # Slightly delay switch to next level so last explosions can
                # play out at this level.
                # After delay, switch levels
                if self.leveling_up is True and self.switch_delay == 30:
                    self.level += 1
                    self.setup()

                # Count updates since switch began to facilitate delay
                else:
                    self.leveling_up = True
                    self.switch_delay += 1

            # If the current level is the game's highest
            else:

                # Stop playing game background music
                # Since background_music_player is None unless sound has been
                # played, if it is not None, then background_music_player is
                # also not None and stop() method can be called without error.
                if (self.background_music_player
                        and self.background_music_sound.is_playing(
                            self.background_music_player)):
                    self.background_music_sound.stop(
                        self.background_music_player)

                # If hasn't played win sound and there's one to play, play it.
                if not self.win_player and self.win_sound:
                    self.win_player = self.win_sound.play()

                # Slightly delay switch to win screen so last explosions can
                # play out at this level
                if self.leveling_up is True and self.switch_delay == 30:

                    # After delay, create and show an instance of GameWonView
                    won_view = GameWonView(self.win_player, self.win_sound)
                    self.window.show_view(won_view)

                # If delay threshold hasn't been met, increment count of
                # updates since transition began
                else:
                    self.leveling_up = True
                    self.switch_delay += 1

    def update_lives_based_on_hits(self) -> None:
        """
        Checks whether the player has been hit and needs to lose a life.
        If so, and there are lives left, starts or continues transition to
        restarting current level with one less life. If there are no more
        lives left, starts or continues the transition to a GameLostView.

        The switch to restarting the level or losing the game after meeting
        the criteria to do so is slightly delayed to allow last Explosions to
        play out, and to start the lost-life or game-lost sounds before
        changing screen. This gives a smoother feeling to the transitions.

        If the criteria for restarting a level or losing the game is met,
        begin the transition process if it has not already begun. If the
        transition is already in progress, count updates until it's time to
        switch levels and then switch.

        :return: None
        """

        # If the player hasn't already been hit and is dying, check if they've
        # been hit this time
        if not self.dying:

            # List of total hits from each iteration of the loop below
            hits = []

            # If the player collides with any other sprite, they die
            # Like with draw() method, use SpriteList to check instead of
            # self.player_sprite so that collisions don't get checked if
            # player dies and is removed from SpriteList
            for player in self.player_list:

                # arcade function that checks for collisions between a Sprite
                # and a list of SpriteLists
                h = arcade.check_for_collision_with_lists(
                    player, [self.asteroid_list, self.enemy_laser_list,
                             self.enemy_list])
                hits += h

            # If there are hits, it's because something (or some things) have
            # hit the player, so create an Explosion at their location
            if hits:
                self.explosion_list.append(Explosion(
                    self.explosion_textures, self.player_sprite.center_x,
                    self.player_sprite.center_y, self.explosion_image_scale,
                    self.explosion_sound))

                # Remove all Sprites in collision (they shouldn't still be
                # visible and movable if they've been destroyed in an
                # explosion)
                for hit in hits:
                    hit.remove_from_sprite_lists()

                # Remove the player sprite from lists, too, so it can't be
                # drawn, moved, or hit by anything
                self.player_sprite.remove_from_sprite_lists()

                # If the Player is hit, then the dying process begins
                self.dying = True

        # If the player is dying, including from a hit on this update
        if self.dying:

            # If lives left, restart level (remember, self.lives starts at 0)
            if self.lives >= 1:

                # If there is a sound, but it hasn't been played, play it
                if not self.lost_life_player and self.lost_life_sound:
                    self.lost_life_player = self.lost_life_sound.play()

                # Slightly delay reset of level so last explosions can
                # play out
                if self.switch_delay == 60:

                    # Decrement lives left
                    self.lives -= 1

                    # Restart this level
                    self.setup()

                # If not ready to switch, count updates since dying started
                else:
                    self.dying = True
                    self.switch_delay += 1

            # If out of lives go to ending screen
            else:

                # Stop background music
                # Since background_music_player is None unless sound has been
                # played, if it is True, then background_music_sound must
                # exist, so it can be stopped
                if (self.background_music_player
                        and self.background_music_sound.is_playing(
                            self.background_music_player)):
                    self.background_music_sound.stop(
                        self.background_music_player)

                # If hasn't played game-over sound and there is one to play,
                # play it (only want it to play once)
                if not self.game_over_player and self.game_over_sound:
                    self.game_over_player = self.game_over_sound.play()

                # Slightly delay switch to game over view so last explosions
                # can play out at this level
                if self.switch_delay == 60:

                    # Go to game over screen
                    game_lost_view = GameLostView()
                    self.window.show_view(game_lost_view)

                # If not switching yet, count updates that switch has been
                # delayed
                else:
                    self.dying = True
                    self.switch_delay += 1

    def update_points_based_on_strikes(self) -> None:
        """
        Count collisions between Player's Lasers and Asteroids, and Player's
        Lasers and EnemyShips. Add points for each hit to self.points total.

        :return: None
        """

        # Check player laser collisions
        # Lists to track hit asteroids and enemies separately for scoring
        asteroids_hit = []
        enemies_hit = []

        # There's not a method to check for collisions between one SpriteList
        # and one or more others, so must iterate over player_laser_list

        # Iterate backwards over list of lasers to avoid IndexErrors as
        # sprites are removed
        for i in range(len(self.player_laser_list) - 1, -1, -1):

            # Get asteroids this laser has collided with
            asteroids = arcade.check_for_collision_with_list(
                self.player_laser_list[i], self.asteroid_list)

            # Get enemies this laser has collided with
            enemies = arcade.check_for_collision_with_list(
                self.player_laser_list[i], self.enemy_list)

            # Remove laser if it hit anything
            if asteroids or enemies:
                self.player_laser_list[i].remove_from_sprite_lists()

                # Add these hit asteroids and enemies to lists of all hit
                # asteroids and enemies
                asteroids_hit += asteroids
                enemies_hit += enemies

        # Add points for each hit
        # Eg, if each Asteroid is worth 5 and 10 were hit, add 50 points
        self.points += self.asteroid_points * len(asteroids_hit)
        self.points += self.enemy_points * len(enemies_hit)

        # Remove hit sprites. Leave explosions where they were
        self.remove_and_explode(asteroids_hit)
        self.remove_and_explode(enemies_hit)

    def remove_and_explode(self, list_o_sprites: List[arcade.Sprite]) -> None:
        """
        Removes all sprites in given list from all SpriteLists and leaves
        Explosions where they were.

        :param List[arcade.Sprite] list_o_sprites: List of Sprites (including
            subclasses of arcade.Sprite). Didn't want to call the list of
            sprites sprite_list because it could be confused with a SpriteList
        :return: None
        """

        # Validate parameters
        if not isinstance(list_o_sprites, list):
            raise TypeError("TypeError: list_o_sprites must be a list")

        # Iterate over given list
        for sprite in list_o_sprites:

            # Put an Explosion object in the sprite's location
            self.explosion_list.append(Explosion(self.explosion_textures,
                                                 sprite.center_x,
                                                 sprite.center_y,
                                                 self.explosion_image_scale,
                                                 self.explosion_sound))

            # Remove sprite from SpriteLists
            sprite.remove_from_sprite_lists()

    def update_player_speed_angle_change_based_on_input(self) -> None:
        """
        Updates Player's speed, change_angle and shooting attributes based
        on GameView attributes that track user input. For example, translates
        self.up_pressed into forward speed for the Player sprite, which
        translates into actual forward movement in the Player sprite's
        on_update.

        :return: None
        """

        # Default to no movement if keys aren't pressed or opposite keys are
        # pressed
        self.player_sprite.change_angle = 0
        self.player_sprite.speed = 0

        # TODO: ASK -- why isn't this working for
        #  Issue where if L and U are pressed, D won't stop U/D movement

        # Movement should only happen if one of a pair of directions
        # (left/right or up/down) is indicated.
        # If opposite keys are pressed, movement shouldn't occur

        # This works such that the player can spin in place with left or
        # right, move straight with up or down, and move in curves with
        # one of left/right and one of up/down. If up and down are pressed,
        # the player doesn't move forward or back, and if left and right are
        # pressed, the player doesn't spin.

        # If three directions are indicated (eg left, right and up), then
        # the two opposite ones (eg left and right) should cancel out,
        # leaving the third to be the only one to have any effect. For
        # example, if left, right, and up are pressed, then left and right
        # should cancel out so there's no spin, and the Player should just
        # move forward as if only up were pressed. However, there's a bug
        # that makes it so this doesn't happen. Currently, if two directions
        # are indicated, and then a third is made True (eg if on one update
        # left and up had been True and on the next update left, right, and
        # up were True), then the third direction doesn't register. I haven't
        # been able to track down this bug (it may be in my keyboard, my code,
        # or the underlying Pyglet code), but there's no reason for a player
        # to ever try to try to move in three directions at once, so the bug
        # doesn't impact gameplay.

        # Turning left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_angle = -self.player_sprite.angle_rate
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_angle = self.player_sprite.angle_rate

        # Moving forward/back
        if self.up_pressed and not self.down_pressed:
            self.player_sprite.speed = self.player_sprite.forward_rate
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.speed = -self.player_sprite.forward_rate

        # Update player sprite's shooting attribute to match whether space
        # is pressed
        self.player_sprite.shooting = self.space_pressed

    def spawn_asteroids_and_enemies(self) -> None:
        """
        Spawn new Asteroids and EnemyShips at the intervals indicated by their
        spawn rates. Works on all levels, including ones with no Asteroids
        or EnemyShips.

        Although the code for refilling asteroids and enemies is almost
        identical, it didn't seem practical to create a more generic function
        that could be called once for each because the method would require
        many parameters, including ones that are passed by value, not
        by reference. So much extra code would have to be written to support
        that generic refilling function that the result would be longer and
        less clear than this method.

        :return: None
        """

        # If there Asteroids to spawn on level, add a new one at the rate
        # of their spawn rate
        if self.level_settings['asteroid spawn rate'][self.level] > 0:

            # Count down updates until it's time to spawn another Asteroid
            if self.asteroids_spawning > 0:
                self.asteroids_spawning -= 1
            else:

                # When it's time to spawn another Asteroid, call make_asteroids
                # to make an instance of Asteroid and append it to the asteroid
                # list.
                self.make_asteroids(1,
                                    self.level_settings[
                                        'asteroid speed range'][self.level])

                # Reset asteroids_spawning to start countdown to next
                # Asteroid's creation
                self.asteroids_spawning = 60 // self.level_settings[
                    'asteroid spawn rate'][self.level]

        # If there EnemyShips to spawn on level, add a new one at the rate
        # of their spawn rate
        if self.level_settings['enemy spawn rate'][self.level] > 0:

            # Count down updates until it's time to spawn another EnemyShip
            if self.enemies_spawning > 0:
                self.enemies_spawning -= 1
            else:

                # When it's time to spawn another EnemyShip, call
                # make_enemy_ships to make an instance of EnemyShip and
                # append it to the enemy list.
                self.make_enemy_ships(1,
                                      self.level_settings[
                                          'enemy speed range'][self.level])

                # Reset asteroids_spawning to start countdown to next
                # Asteroid's creation
                self.enemies_spawning = 60 // self.level_settings[
                    'enemy spawn rate'][self.level]

    def set_targets_for_enemies(self) -> None:
        """
        For all EnemyShips in enemy_list, updates target point to be Player
        sprite's current center point. This is what allows EnemyShip's
        on_update method to make EnemyShips follow the Player around and
        shoot directly at it.

        If player_list is empty (because Player is dead), stop EnemyShips
        from shooting and slow their speeds to a stop. After a pause, change
        set EnemyShips' speeds to negative so they retreat backwards in the
        direction from whence they came.

        :return: None
        """

        # Set enemies' new target point as player's current (soon-to-be-old)
        # location
        if len(self.player_list) >= 1:
            for enemy in self.enemy_list:
                enemy.set_target(self.player_sprite.center_x,
                                 self.player_sprite.center_y)

        # If player is dead, make enemies stop shooting and pause, then
        # retreat backwards slowly

        # Amount to subtract from EnemyShips' speeds when slowing to stop
        slow_rate = 10

        # Number of updates before starting to slow EnemyShips to stop
        time_to_stop = 40

        # Number of updates before making EnemyShips retreat
        time_to_retreat = time_to_stop + 30

        # If player_list is empty, it's because Player sprite has been hit
        # This is when I want the EnemyShips to slow and retreat
        if len(self.player_list) == 0:
            for enemy in self.enemy_list:

                # Stop shooting
                enemy.reload_time = None

                # Retreat backwards from where Player died.
                # Only visible if time_to_retreat is less than the time
                # to restart the level. I don't want it visible now, but I
                # want the ability to make it visible in the future.
                if self.switch_delay > time_to_retreat and enemy.speed >= 0:

                    # Set reverse speeds in same range as forwads speeds for
                    # the level
                    enemy.set_speed_in_range(self.level_settings[
                                                 'enemy speed range'][
                                                 self.level])
                    enemy.speed *= -1

                # Slow to a stop
                # Only visible if time_to_stop is less than the time to
                # restart the level.
                elif self.switch_delay > time_to_stop:
                    if enemy.speed >= 0:
                        enemy.speed -= slow_rate
                        if enemy.speed < 0:
                            enemy.speed = 0

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """
        Inherited method from pyglet.window.Window through Arcade gets called
        whenever keys are pressed. Responds to certain key presses.
        Updates values for GameView key press attributes (up_pressed, etc.)
        so GameView's on_update can translate presses into sprite actions.
        Executes game or window commands to close the window, restart or pause
        the game.

        Cmd + W or Ctrl + W: Close window.
        Cmd + R or Ctrl + R: Restart game from level 1.
        Cmd + T or Ctrl + T: Create and show PauseView object to pause game.

        Up, down, left and right arrow presses make GameView up_pressed,
        down_pressed, left_pressed, and right_pressed attributes True.
        Space bar press makes GameView space_pressed attribute True.

        Cmd + 1: Go to level 1 with all lives and necessary points.
        Cmd + 2: Go to level 2 with all lives and necessary points.
        Cmd + 3: Go to level 3 with all lives and necessary points.
        Cmd + 4: Level 3 with all lives and 15 more points needed to win.

        :param int symbol: Integer representation of regular key pressed.
        :param int modifiers: Integer representing bitwise combination of all
            modifier keys pressed during event.
        :return: None
        """

        # Validate parameters
        if not isinstance(symbol, int):
            raise TypeError("TypeError: symbol must be an integer")
        if not isinstance(modifiers, int):
            raise TypeError("TypeError: modifiers must be an integer")

        # Gracefully quit program.
        if symbol == arcade.key.W and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):

            # Closes window and runs garbage collection.
            arcade.close_window()

        # Restart game.
        if symbol == arcade.key.R and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):

            # Reset points and level, then restart at the correct level.
            self.points = 0
            self.level = 0
            self.setup()

        # Pause game.
        if symbol == arcade.key.T and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):

            # Pass this view to PauseView object so PauseView can restart play
            # from the same place when the game is un-paused.
            pause = PauseView(self)
            self.window.show_view(pause)

        # Key presses to translate into player movement and shooting in
        # update_player_speed_angle_change_based_on_input().
        # This allows for continuous movement as long as the key is pressed
        # and for GameView to decide whether opposite key presses should
        # cancel out.
        # Learned this from AtiByte's video, "Python Arcade Library p05, -
        # keyboard input and smooth movement," accessible at
        # (https://www.youtube.com/
        # watch?v=em6WphBQbh0&list=PL1P11yPQAo7pPlDlFEaL3IUbcWnnPcALI&index=6)
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

        # For cheating: jumping to levels 1, 2 or 3 with full lives and
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
        # needed to win (to be able to demo win screen during presentation
        # since I die a lot while playing)
        if symbol == arcade.key.KEY_4 and modifiers == arcade.key.MOD_COMMAND:
            self.level = 2
            self.lives = 2
            self.points = self.level_settings['points goal'][2] - 15
            self.setup()

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """
        Responds to certain key releases (is called whenever a key is
        released). Updates values for GameView key press attributes
        (up_pressed, etc.) so GameView's on_update can translate presses into
        sprite actions. Up, down, left and right arrow releases make GameView
        up_pressed, down_pressed, left_pressed, and right_pressed attributes
        False. Space bar release makes GameView space_pressed attribute False.

        :param int symbol: Integer representation of regular key released.
        :param int modifiers: Integer representing bitwise combination of all
            modifier keys released during event.
        :return: None
        """

        # Validate parameters
        if not isinstance(symbol, int):
            raise TypeError("TypeError: symbol must be an integer")
        if not isinstance(modifiers, int):
            raise TypeError("TypeError: modifiers must be an integer")

        # Key releases to translate into (lack of) player movement and
        # shooting in update_player_speed_angle_change_based_on_input()
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
        """
        Returns string representation of GameView object.

        :return str: String representation of GameView object.
        """
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


class TextView(arcade.View):
    """
    Extends arcade.View to provide easy text and background drawing
    functionality. Includes attributes for a main string of text and a
    secondary string of text to potentially have different sizes, colors
    and y-anchor points. Text is always horizontally centered and wraps.
    Includes attributes to have different colors in each corner of the screen,
    fading and mixing in the center. Draws background colors and text. Also
    has on_key_press method with basic functionality to start/restart the game
    from level 1, and to close the window. If a sound is given to as a
    parameter to TextView, TextView will stop playing it when cmd/ctrl + r is
    pressed to restart the game.

    Note: Subclasses may want to utilize TextView's method for drawing
    a colorful rectangle with text on top of it, on top of other shapes that
    the subclass has already drawn. In such cases, the subclass may call
    _on_draw(), which will draw the colorful rectangle and text without first
    clearing the screen. In such cases, the subclass's on_draw() method must
    start with arcade.start_render(). If you don't need to draw shapes or
    text underneath the rectangle and text drawn by TextView, you do not
    need to override on_draw() at all. If your subclass doesn't start it's
    on_draw method with arcade.start_render(), make sure to call this class's
    on_draw method, not the _on_draw() method.

    Attributes:
        Attributes in addition to those of arcade.View.
        :bg_colors: (4-tuple of color tuples) Colors of the four corners of
            the rectangle. NOTE: This is reset every time _on_draw is called
            to the following: bottom_left_color, bottom_right_color,
            top_right_color, top_left_color.
        :bg_points: (4-tuple of 2-tuples of ints) Represents the vertices of
            the background rectangle. Points and their colors should appear
            in the same order: bottom left, bottom right, top right, top left.
            Defaults to corners of the window.
        :bottom_left_color: (3-tuple or 4-tuple of ints) Color of the bottom
            left corner of the background rectangle. Defaults to black.
        :bottom_right_color: (3-tuple or 4-tuple of ints) Color of the bottom
            right corner of the background rectangle. Defaults to black.
        :main_text_anchor_y: (int) What part of text is aligned with
            y-coordinate of anchor point (center, baseline, bottom, or top).
            Defaults to bottom.
        :main_text: (str) First text to draw.
        :main_text_color: (3-tuple or 4-tuple of ints) Color of main_text.
            Defaults to white.
        :main_text_scale_denominator: (int) By default, text size is scaled to
            window height. This is what to divide window height by to get font
            size.
        :main_text_size: (float) Font size. Defaults to 12.
        :main_text_start_y: (float) Y-coordinate of text's anchor point.
            Defaults to 1/2 of window height.
        :secondary_text: (str) Second text to draw. Defaults to information
            about key combinations to restart the game and close the window.
        :secondary_text_anchor_y: (int) What part of text is aligned with
            y-coordinate of anchor point (center, baseline, bottom, or top).
            Defaults to baseline.
        :secondary_text_color: (3-tuple or 4-tuple of ints) Color of
            secondary_text. Defaults to white.
        :secondary_text_scale_denominator: (int) By default, text size is
            scaled to window height. This is what to divide window height by
            to get font size. Defaults to 40.
        :secondary_text_size: (float) Font size.
        :secondary_text_start_y: (float) Y-coordinate of text's anchor point.
            Defaults to 1/2 of window height - font size.
        :sound: (arcade.Sound) Sound that started playing before TextView was
            instantiated and should be stopped playing if game is restarted.
        :sound_player: (pyglet.media.player.Player) Player playing the sound.
        :top_left_color: (3-tuple or 4-tuple of ints) Color of the top right
            corner of the background rectangle. Defaults to black.
        :top_right_color: (3-tuple or 4-tuple of ints) Color of the top left
            corner of the background rectangle. Defaults to black.
        :window: (arcade.Window) Window that this view is associated with.
    """

    def __init__(self, player: pyglet.media.player.Player = None,
                 sound: arcade.Sound = None):
        """
        Constructor. Sets attributes to default values (listed above).

        :param pyglet.media.player.Player player: Player that's playing sound.
        :param arcade.Sound sound: Sound that's being played
        """

        # Validate parameters
        if (player is not None
                and not isinstance(player, pyglet.media.player.Player)):
            raise TypeError("TypeError: player must be a "
                            "pyglet.media.player.Player")
        if (sound is not None
                and not isinstance(sound, arcade.Sound)):
            raise TypeError("TypeError: sound must be an arcade.Sound")

        super().__init__()

        # Set background color behind drawings
        arcade.set_background_color((0, 0, 0))    # Black

        # Main text and settings
        self.main_text = ""
        self.main_text_color = (255, 255, 255)    # White
        self.main_text_scale_denominator = 12
        self.main_text_size = (self.window.height
                               / self.main_text_scale_denominator)
        self.main_text_start_y = self.window.height / 2
        self.main_text_anchor_y = "bottom"

        # Secondary text and settings
        # Many subclasses will have this secondary text
        self.secondary_text = ("\n\nRestart with 'cmd + r' or 'ctrl + r'"
                               "\n\nExit with 'cmd + w' or 'ctrl + w'")
        self.secondary_text_color = (255, 255, 255)
        self.secondary_text_scale_denominator = 40
        self.secondary_text_size = (self.window.height
                                    / self.secondary_text_scale_denominator)
        self.secondary_text_start_y = (self.window.height / 2
                                       - self.secondary_text_size)
        self.secondary_text_anchor_y = "baseline"

        # Colors for all four corners default to black
        self.bottom_left_color = (0, 0, 0)
        self.bottom_right_color = (0, 0, 0)
        self.top_right_color = (0, 0, 0)
        self.top_left_color = (0, 0, 0)

        # Colors and vertices for background rectangle
        # Also in on_draw to accommodate dynamic changes to colors
        self.bg_colors = (self.bottom_left_color, self.bottom_right_color,
                          self.top_right_color, self.top_left_color)
        self.bg_points = ((0, 0), (self.window.width, 0),
                          (self.window.width, self.window.height),
                          (0, self.window.height))

        # Sound, if there is one
        self.sound_player = player
        self.sound = sound

    def on_draw(self) -> None:
        """
        Draw background rectangle and text.

        :return: None
        """

        # Since _on_draw() doesn't have an arcade.start_render() statement, it
        # can't be used on its own for rendering the screen. Start render
        # here and let _on_draw do the rest. (See _on_draw for more info.)
        arcade.start_render()
        self._on_draw()

    def _on_draw(self) -> None:
        """
        Draws background rectangle and text to the screen ON TOP OF whatever
        is already there.

        This method does not have an arcade.start_render() statement to clear
        the screen before drawing. That means that it can be used by
        subclasses as part of their on_draw() methods to draw on top of
        something existing on the screen. This method's effect is
        unpredictable if used on its own, so it should only be used in
        conjunction with an on_draw method that calls arcade.start_render()
        sometime before calling this method. (For an example, see PauseView.)

        :return: None
        """

        # Normally this would be called on_draw, and its first statement
        # would be a call to arcade.start_render to clear the screen and
        # prepare it for drawing. I'm leaving out arcade.start_render so
        # subclasses can call _on_draw to make use of the statements here
        # without erasing anything else they've already drawn (eg the way
        # PauseView does).
        # However, if this were in the on_draw() method, it would be risky
        # because the screen won't render properly without
        # arcade.start_render() being called first. To prevent potential
        # subclasses from relying on this method to draw their screens without
        # first calling start_render(), I've tried name mangling. Subclasses
        # and instances of this class don't need to know _on_draw is missing
        # that key function call because they'll automatically call on_draw,
        # which calls arcade.start_render before calling this method.
        # Subclasses that want to draw to the screen entirely on their own,
        # or that want to draw to the screen before calling this method to
        # finish drawing a rectangle and text can do so by overriding on_draw
        # and then calling this method from their override of on_draw.

        # Create background rectangle each time to accommodate changes in
        # colors
        self.bg_colors = (self.bottom_left_color, self.bottom_right_color,
                          self.top_right_color, self.top_left_color)
        background = arcade.create_rectangle_filled_with_colors(
            self.bg_points, self.bg_colors)

        # Draw background rectangle
        background.draw()

        # Use variables for many of the arguments to draw_text() in order
        # to be general enough to be used in situations requiring different
        # text, font sizes, locations, etc.
        # A different version of this class could include even more variables
        # to be even more broadly applicable, but these are the only ones
        # I need for this project.
        arcade.draw_text(self.main_text, self.window.width / 2,
                         self.main_text_start_y, self.main_text_color,
                         anchor_x="center", anchor_y=self.main_text_anchor_y,
                         font_size=self.main_text_size,
                         align="center", bold=True,
                         width=self.window.width, multiline=True)

        arcade.draw_text(self.secondary_text, self.window.width / 2,
                         self.secondary_text_start_y,
                         self.secondary_text_color, anchor_x="center",
                         anchor_y=self.secondary_text_anchor_y,
                         font_size=self.secondary_text_size,
                         align="center", bold=True,
                         width=self.window.width, multiline=True)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """
        Executes commands to close the window or restart the game if the
        player presses the correct key combination.
        Cmd + W or Ctrl + W: Close window.
        Cmd + R or Ctrl + R: Restart game from level 1.

        :param int symbol: Integer representation of regular key pressed.
        :param int modifiers: Integer representing bitwise combination of all
            modifier keys pressed during event.
        :return: None
        """

        # Validate parameters
        if not isinstance(symbol, int):
            raise TypeError("TypeError: symbol must be an integer")
        if not isinstance(modifiers, int):
            raise TypeError("TypeError: modifiers must be an integer")

        # Gracefully quit program
        if symbol == arcade.key.W and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):

            # Closes window and runs garbage collection
            arcade.close_window()

        # Restart the game
        if symbol == arcade.key.R and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):

            # Stop playing a sound if there is one
            if self.sound_player and self.sound:
                if self.sound.is_playing(self.sound_player):
                    self.sound.stop(self.sound_player)

            # Create a new instance of GameView and show it
            # The asterisk unpacks the values in the tuple so its like
            # writing out all 14 required arguments, but much neater.
            game = GameView(*self.window.game_parameters)
            self.window.show_view(game)

    def __str__(self) -> str:
        return ("<TextView: main_text = {}, main_text_scale_denominator = {},"
                "secondary_text = {}, secondary_text_scale_denominator = {}"
                ">".format(self.main_text, self.main_text_scale_denominator,
                           self.secondary_text,
                           self.secondary_text_scale_denominator))


class FadingView(TextView):
    """
    Extends arcade.View to provide fading functionality. FadingView has
    methods to adjust its transparency (alpha) to make itself fade in or
    out.

    Note: This class isn't meant to be instantiated. It is only meant to be
    subclassed. FadingView doesn't overide the arcade.View on_draw method,
    meaning that it won't be visible on its own. Additionally, alpha's
    existence doesn't change the transparency of objects on the screen; it
    must be used in the on_draw methods of subclasses to control transparency.

    Attributes:
        Attributes in addition to those of arcade.View.
        :alpha: (int) Int to represent transparency of objects onscreen. 255
            is opaque and 0 is invisible.
        :fade_rate: (int) Amount to add or subtract from alpha each time
            fade_in or fade_out is called.
    """

    def __init__(self, fade_rate: int, alpha: int):
        """
        Constructor. Creates a FadingView object with given fade_rate and
        alpha.

        :param int fade_rate: Int to represent transparency of objects
            onscreen. 255 is opaque and 0 is invisible.
        :param int alpha: Amount to add or subtract from alpha each time
            fade_in or fade_out is called.
        """

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
        """
        Adds fade_rate to current alpha, maxing out when alpha is 255.
        Returns True when alpha equals 255, returns False otherwise. When
        called repeatedly, as from an update or on_update method, can be
        used to fade in objects from invisible to fully opaque.

        :return bool: True if alpha is 255, False otherwise.
        """

        # Since alpha is an attribute I created, it's okay for self.alpha to
        # rise above 255 as long as it's corrected down before it's used to
        # draw, since the draw() methods require an alpha <= 255
        self.alpha += self.fade_rate
        if self.alpha >= 255:
            self.alpha = 255
            return True
        else:
            return False

    def fade_out(self) -> bool:
        """
        Subtracts fade_rate from current alpha, stopping when alpha is 0.
        Returns True when alpha equals 0, returns False otherwise. When
        called repeatedly, as from an update or on_update method, can be
        used to fade out objects from fully opaque to invisible.

        :return bool: True if alpha is 0, False otherwise.
        """

        # It's okay for self.alpha to dip below 0 as long as it's corrected
        # before it's used to draw, since draw() methods require an alpha >= 0
        self.alpha -= self.fade_rate
        if self.alpha <= 0:
            self.alpha = 0
            return True
        else:
            return False

    def __str__(self) -> str:
        """
        Returns string representation of FadingView object.

        :return str: String representation of FadingView object.
        """
        return ("<FadingView: window_width = {}, window_height = {},"
                " alpha = {}, fade_rate = {}>".format(self.window.width,
                                                      self.window.height,
                                                      self.alpha,
                                                      self.fade_rate))


class TitleView(FadingView):
    def __init__(self):

        super().__init__(5, 0)

        # Set text and settings (these come from TextView)
        self.main_text = "Spin\n&\nShoot"
        self.main_text_scale_denominator = 10
        self.main_text_size = (self.window.height
                               / self.main_text_scale_denominator)
        self.main_text_anchor_y = "center"

        # Set secondary_text to empty string since TextView has text in it
        self.secondary_text = ""

        # Attributes to facilitate fading in, pausing and fading out
        self.faded_in = False
        self.pause_count = 60
        self.faded_out = False

        # Colors. Alpha is the transparency of the color
        self.main_text_color = (255, 255, 255, self.alpha)
        self.bottom_left_color = (0, 0, 0, self.alpha)
        self.bottom_right_color = (0, 0, 0, self.alpha)
        self.top_right_color = (0, 0, 0, self.alpha)
        self.top_left_color = (0, 0, 205, self.alpha)    # Blue

    def on_update(self, delta_time: float = 1 / 60) -> None:

        # Validate parameters
        if not isinstance(delta_time, (int, float)):
            raise TypeError("TypeError: delta_time must be numeric")
        if delta_time < 0:
            raise ValueError("ValueError: delta_time must be non-negative")

        # Update self.alpha to fade in and out

        # After fading out, create and show an InstructionsView object
        if self.faded_out:
            instructions = InstructionsView()
            self.window.show_view(instructions)

        # Fade in until faded_in is True to indicate fully opaque
        if not self.faded_in:
            self.faded_in = self.fade_in()

        # After pausing (after fading in), fade out
        elif self.pause_count == 0:
            self.faded_out = self.fade_out()

        # Pause after fading in
        # Count down updates after being fully faded in before starting to
        # fade out
        else:
            self.pause_count -= 1

        # Update color transparency with alpha
        self.main_text_color = (255, 255, 255, self.alpha)
        self.bottom_left_color = (0, 0, 0, self.alpha)
        self.bottom_right_color = (0, 0, 0, self.alpha)
        self.top_right_color = (0, 0, 0, self.alpha)
        self.top_left_color = (0, 0, 205, self.alpha)

    def __str__(self) -> str:
        return ("<TitleView: faded_in = {}, pause_count = {}, faded_out = {},"
                " alpha = {}, fade_rate = {}>".format(self.faded_in,
                                                      self.pause_count,
                                                      self.faded_out,
                                                      self.alpha,
                                                      self.fade_rate))


class InstructionsView(FadingView):
    def __init__(self):

        super().__init__(5, 0)

        # Set text and settings
        self.main_text = ("INSTRUCTIONS:"
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
        self.main_text_scale_denominator = 40
        self.main_text_size = (self.window.height
                               / self.main_text_scale_denominator)
        self.main_text_anchor_y = "center"

        # Set secondary_text to empty string since TextView has text in it
        self.secondary_text = ""

        # Attribute to facilitate fading in, pausing and fading out
        self.faded_in = False

        # Colors. Alpha is the transparency of the color
        self.main_text_color = (255, 255, 255, self.alpha)
        self.bottom_left_color = (0, 0, 0, self.alpha)
        self.bottom_right_color = (65, 44, 129, self.alpha)    # Purple
        self.top_right_color = (0, 0, 0, self.alpha)
        self.top_left_color = (0, 0, 205, self.alpha)    # Blue

    def on_update(self, delta_time: float = 1 / 60) -> None:

        # Validate parameters
        if not isinstance(delta_time, (int, float)):
            raise TypeError("TypeError: delta_time must be numeric")
        if delta_time < 0:
            raise ValueError("ValueError: delta_time must be non-negative")

        # Fade in until faded_in is True to indicate fully opaque
        if not self.faded_in:
            self.faded_in = self.fade_in()

        # Update color transparency with alpha
        self.main_text_color = (255, 255, 255, self.alpha)
        self.bottom_left_color = (0, 0, 0, self.alpha)
        self.bottom_right_color = (65, 44, 129, self.alpha)
        self.top_right_color = (0, 0, 0, self.alpha)
        self.top_left_color = (0, 0, 205, self.alpha)

    def on_key_press(self, symbol: int, modifiers: int) -> None:

        # Validate parameters
        if not isinstance(symbol, int):
            raise TypeError("TypeError: symbol must be an integer")
        if not isinstance(modifiers, int):
            raise TypeError("TypeError: modifiers must be an integer")

        # Call TextView's on_key_press since it comes first
        super().on_key_press(symbol, modifiers)

        if symbol == arcade.key.SPACE:
            game = GameView(*self.window.game_parameters)
            self.window.show_view(game)

    def __str__(self) -> str:
        return ("<InstructionsView: faded_in = {}, alpha = {}, "
                "fade_rate = {}>".format(self.faded_in, self.alpha,
                                         self.fade_rate))


class GameLostView(TextView):
    """
    Extends TextView. Doesn't create new attributes or methods, but assigns
    specific values to TextView attributes so GameLostView objects can be
    instantiated easily, without having to change many values of TextView upon
    each instantiation.
    """

    def __init__(self, player: pyglet.media.player.Player = None,
                 sound: arcade.Sound = None):
        super().__init__(player, sound)

        # Change specifics of text
        self.main_text = "Game Over"

        # Change background colors
        self.bottom_left_color = (0, 0, 0)
        self.bottom_right_color = (128, 0, 0)    # Red
        self.top_right_color = (0, 0, 0)
        self.top_left_color = (0, 0, 205)    # Blue
        self.bg_colors = (self.bottom_left_color, self.bottom_right_color,
                          self.top_right_color, self.top_left_color)


class GameWonView(TextView):
    """
    Extends TextView. Doesn't create new attributes or methods, but assigns
    specific values to TextView attributes so GameWonView objects can be
    instantiated easily, without caller having to change many values of
    TextView upon each instantiation.
    """

    def __init__(self, player: pyglet.media.player.Player = None,
                 sound: arcade.Sound = None):
        super().__init__(player, sound)

        # Change specifics of text
        self.main_text = "You won!"

        # Change background colors
        self.bottom_left_color = (0, 0, 0)
        self.bottom_right_color = (0, 0, 205)    # Blue
        self.top_right_color = (0, 0, 0)
        self.top_left_color = (180, 100, 240)   # Pink
        self.bg_colors = (self.bottom_left_color, self.bottom_right_color,
                          self.top_right_color, self.top_left_color)


class PauseView(TextView):

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

        # This doesn't pause sound effects like leveling up, dying, or
        # explosions

        self.main_text = "Paused"
        self.secondary_text = ("\n\nResume play with 'cmd + t' or 'ctrl + t'"
                               + self.secondary_text)

        # Transparent white color to fill rectangle with for pause screen
        # frozen-behind-veil visual effect
        self.bottom_left_color = (255, 255, 255, 100)
        self.bottom_right_color = (255, 255, 255, 100)
        self.top_right_color = (255, 255, 255, 100)
        self.top_left_color = (255, 255, 255, 100)
        self.bg_colors = (self.bottom_left_color, self.bottom_right_color,
                          self.top_right_color, self.top_left_color)

        # Sprite lists to draw
        self.player_list = game_view.player_list
        self.asteroid_list = game_view.asteroid_list
        self.enemy_list = game_view.enemy_list
        self.player_lasers = game_view.player_laser_list
        self.enemy_lasers = game_view.enemy_laser_list

    def on_draw(self) -> None:
        # TextView doesn't have start_render in its on_draw method, so this
        # MUST be called before calling the super's on_draw
        arcade.start_render()

        # Draw sprites from SpriteLists so they're visible behind transparent
        # white rectangle
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

        # Since TextView doesn't have a start_render() statement in
        # _on_draw, can call super's _on_draw method to draw the transparent
        # rectangle and the text
        super()._on_draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:

        # Use super to handle other common key presses (cmd + r and cmd + w)
        super().on_key_press(symbol, modifiers)

        # Unpause key combination
        if symbol == arcade.key.T and (modifiers == arcade.key.MOD_COMMAND
                                       or modifiers == arcade.key.MOD_CTRL):
            # If there's music playing, restart it at the same point
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

    # Store game_parameters as Window attribute so all view objects can access
    window.game_parameters = game_parameters
    # Start with title view, which calls the next view, which calls the next...
    title_view = TitleView()
    window.show_view(title_view)
    arcade.run()


if __name__ == "__main__":
    main()
