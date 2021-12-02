"""
I-M Siegel

Images from Space Shooter (Redux, plus fonts and sounds) by Kenney Vleugels
(www.kenney.nl), licensed under Creative Commons.
https://kenney.nl/assets/space-shooter-redux


Practice:
    Done - moving with angles (eg space ship)
    - colliding sprites with lists (enemies, enemy shooters)
    - disappear (after shot)
    - spawning (already done, but can check how they do)

TODO:
    - add a compass so player can see where they're facing
"""


import arcade
import math
import random


SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Space Shooter"

LASER_IMAGE = "spaceshooter/PNG/Lasers/laserBlue01.png"
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
                 angle=0):
        super().__init__(filename=image, scale=scale, center_x=x, center_y=y,
                         angle=angle)

        self.speed = 500

        # Set direction angle
        self.change_x = -math.sin(math.radians(self.angle))
        self.change_y = math.cos(math.radians(self.angle))

        # Bullets start invisible until spawned
        # redundant if not drawing spawning bullets in separate list
        self.visible = True

        # Frames since initialization
        self.frames = 0

    def on_update(self, delta_time: float = 1 / 60):
        # used to track when to spawn laser and when it should die
        self.frames += 1
        # Always move in the same direction at the same rate
        self.center_x += self.change_x * self.speed * delta_time
        self.center_y += self.change_y * self.speed * delta_time


class Meteor(arcade.Sprite):
    # TODO: maybe a list of meteor speeds at different levels
    def __init__(self, image, scale=IMAGE_SCALE):
        super().__init__(filename=image, scale=scale)

        # Initialize speed to not moving
        self.speed = 0

        # Initialize target point to center of screen
        self.target_x = SCREEN_WIDTH / 2
        self.target_y = SCREEN_HEIGHT / 2

    def on_update(self, delta_time: float = 1 / 60):
        """
        This version makes meteors move in straight-ish lines, not go directly
        toward the player.
        """
        # Move to target if within range, otherwise move towards target

        # Set new center_x
        x_distance = self.target_x - self.center_x
        if abs(x_distance) <= self.speed * delta_time:
            self.center_x = self.target_x
        else:
            # If the target is greater than the current position, then
            # dividing distance by abs(distance) gives 1. If the target is
            # less than the current position, dividing by abs(distance) will
            # give negative 1.
            direction = x_distance / abs(x_distance)
            self.center_x += direction * self.speed * delta_time

        # Set new center_y
        y_distance = self.target_y - self.center_y
        if abs(y_distance) <= self.speed * delta_time:
            self.center_y = self.target_y
        else:
            # If the target is greater than the current position, then
            # dividing distance by abs(distance) gives 1. If the target is
            # less than the current position, dividing by abs(distance) will
            # give negative 1.
            direction = y_distance / abs(y_distance)
            self.center_y += direction * self.speed * delta_time

    def set_target(self, x, y):
        self.target_x = x
        self.target_y = y


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

        # Radius of circumscribed circle describes farthest possible visible
        # point
        self.circumscribed = ((width ** 2) + (height ** 2)) ** .5

        # Start at level 1
        self.level = 1

        # Player ships to change each level
        self.ships = ["spaceshooter/PNG/Player_ships/playerShip1_blue.png",
                      "spaceshooter/PNG/Player_ships/playerShip2_blue.png",
                      "spaceshooter/PNG/Player_ships/playerShip3_blue.png"]

        # Set up list of images to use for meteors
        self.meteor_images = []
        meteor_base_name = "spaceshooter/PNG/Meteors/meteorBrown_{}.png"
        for i in range(1, 5):
            self.meteor_images.append(meteor_base_name.format(
                "big{}".format(i)))
        for i in range(1, 3):
            self.meteor_images.append(meteor_base_name.format(
                "med{}".format(i)))
            self.meteor_images.append(meteor_base_name.format(
                "small{}".format(i)))
            self.meteor_images.append(meteor_base_name.format(
                "tiny{}".format(i)))

        self.player_sprite = None
        self.player_list = None

        self.laser_list = None
        self.meteor_list = None

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

        self.laser_list = arcade.SpriteList()

        self.meteor_list = arcade.SpriteList()

        # Number of meteors depends upon level
        self.make_meteors(10, (50, 200))

    def make_meteors(self, num_meteors, speed_range):
        for i in range(num_meteors):
            self.meteor_list.append(Meteor(random.choice(self.meteor_images)))
            # Get diagonal size of meteor to hide it offscreen
            diagonal = int((self.meteor_list[-1].width ** 2
                            + self.meteor_list[-1].height ** 2) ** .5)

            # Get coordinates of random point offscreen by getting a random
            # x and a corresponding y that makes it work
            x = random.randrange(-1 * SCREEN_WIDTH, 2 * SCREEN_WIDTH)

            # To make sure meteors always start offscreen, the meteor's
            # center must be at least [the radius of the circumscribed
            # circle + the diagonal of the meteor] away from the center of
            # the screen

            # TODO: COMPLEX NUM ISSUE
            try:
                y_min = int(((self.circumscribed + diagonal) ** 2 - (x ** 2))
                            ** .5)
            except TypeError:
                # If x is bigger than self.circumscribed + diagonal, y_min
                # would be a complex number, which int() can't convert
                # In that case, y can be any real number, since the x-value
                # puts the meteor offscreen anyway
                y_min = 0

            # Randomly pick whether y will be positive or negative
            y_sign = random.choice([1, -1])

            # Second parameter to random.randrange() must be larger than
            # than the first, unless the step is set. Account for instance
            # when x-value is very low so y_min may be larger than 2 *
            # SCREEN_HEIGHT
            y_max = max(2 * SCREEN_HEIGHT, 2 * y_min)
            y = y_sign * random.randrange(y_min, y_max)

            # Set coordinates of meteor
            self.meteor_list[-1].center_x = x
            self.meteor_list[-1].center_y = y

            # Set random speed of meteor within range
            self.meteor_list[-1].speed = random.randrange(speed_range[0],
                                                          speed_range[1])


    def on_draw(self):
        arcade.start_render()

        # Draw lasers first so covered by player and look like they're growing
        # out from space ship
        self.laser_list.draw()
        self.player_list.draw()

        # Drawing with SpriteList means anything outside the viewport won't
        # be drawn
        self.meteor_list.draw()

    def on_update(self, delta_time):
        """
        Main game logic
        :param delta_time:
        :return:
        """

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

        # Shoot lasers periodically while space is pressed
        self.reloading -= 1
        if self.space_pressed and self.reloading <= 0:
            self.laser_list.append(Laser(self.player_sprite.center_x,
                                         self.player_sprite.center_y,
                                         angle=self.player_sprite.angle))
            # Slow enough reload time that player could do it faster by
            # repeatedly hitting space, but fast enough to be fun
            self.reloading = 10

        # Fade lasers out after firing
        for laser in self.laser_list:
            # TODO: Is this an okay use of try-except?
            if laser.frames > 60:
                try:
                    laser.alpha -= 30
                except ValueError:
                    laser.remove_from_sprite_lists()
            elif laser.frames > 50:
                laser.alpha -= 10

        # Set meteor's new target point as player's current (soon-to-be-old)
        # location
        for meteor in self.meteor_list:
            meteor.set_target(self.player_sprite.center_x,
                              self.player_sprite.center_y)

        self.player_list.on_update(delta_time)
        self.laser_list.on_update(delta_time)
        self.meteor_list.on_update(delta_time)

    def on_key_press(self, symbol, modifiers):
        # Gracefully quit program
        if symbol == arcade.key.W and modifiers == arcade.key.MOD_COMMAND:
            arcade.close_window()

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

        # TODO: DELETE -- JUST USED FOR DEBUGGING
        for meteor in self.meteor_list:
            print("{}, {}\n{}, {}\n{}\n".format(meteor.center_x,
                                                meteor.center_y,
                                                meteor.target_x,
                                                meteor.target_y,
                                                meteor.speed))
        print("-" * 50)

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

