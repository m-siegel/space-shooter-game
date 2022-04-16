# Space Shooter Game

This is a simple space-shooter game that I created for an intro-to-coding
class. It may be downloaded and played, or its classes may be imported and
used in other projects.

![A screenshot of the game. The player ship shoots as it is surrounded
 by asteroids, enemy ships and an explosion.](/imagesForReadme/Game.jpg)

## Use 1: Playing the Game
This program is compatable with Python 3.8.5 with the
[Arcade Library](https://api.arcade.academy/en/latest/index.html) installed.
Download the FINAL_PROJECT_5001.py file and the media folder, then run the
program and enjoy!

![A screenshot of the instructions](/imagesForReadme/Instructions.jpg)

### Changing the look and feel
This program's global variables and main function determine much of the look
and sound of the game. The global variables hold the data concerning which
images to use for each sprite (eg deciding if the player looks like a space
ship or a dragon), and what sounds to use for each event (lase shots,
leveling up, etc). Users who can read code can easily update these global
settings to change the look and feel of the game.

## Use 2: Importing Classes for Use in Other Projects
This program has two primary categories of classes that you may find useful in
your own projects:
- Sprite classes, and
- View classes, excluding GameView.

### Sprite classes:
This program contains six classes that extend the arcade.Sprite class. These
represent 'sprites' on the screen, which include the primary elements of the
game like the player's character, enemy space ships, lasers, explosions, etc.
These sprites don't access global variables, and, with the exception of
Player sprites and EnemyShip sprites, which both create instances of Laser
sprites, the sprites don't call each other. This means that the sprites can
be imported into other programs to be used as independent elements of other
games.

### View classes:
The program contains eight classes that extend the arcade.View class. These
represent the various screens that a user sees (title, instructions, main
game, game over, etc.).

Most of these classes are interconnected (for example, a GameView may create
a PauseView object if the user hits pause, a GameLostView if the player loses,
or a GameWonView if the player wins, and each of these may create instances
of GameView). This means that, except for TextView and FadingView, these
classes can't be imported into other projects independently of each other,
but most of the View subclasses may serve as templates for title,
instruction, pause, and game over screens for other games.

TextView and FadingView may be imported and used in other contexts since they
provide generally useful functionality. They may also serve as models for
other View subclasses with even more functionality.

## Credits

### Arcade Library and Tutorials:
This program was built with the Arcade library, which was copyrighted by
Paul Vincent Craven and is [licensed under the MIT License.](https://github.com/pythonarcade/arcade/blob/maintenance/license.rst)

In addition to its powerful classes, the Arcade library has many examples,
clear documentation,and accessible source code that make it easy to learn.
I spent days reading through documentation and source code, and experimenting
with the library. I learned a lot from looking at the example code, the
documentation, and by digging into the source code (including the code for
libraries, like Pyglet, that Arcade is built on). I highly recommend checking
out Arcade.
- [Website](https://api.arcade.academy/en/latest/)
- [Documentation](https://api.arcade.academy/en/latest/arcade.html)
- [Examples](https://api.arcade.academy/en/latest/examples/index.html)
- [Github](https://github.com/pythonarcade/arcade/tree/maintenance)

### AtiByte Tutorials:
Before downloading and digging into the Arcade code and docs, I learned the
basics of Arcade from some YouTube videos by 
[AtiByte](https://www.youtube.com/playlist?list=PL1P11yPQAo7pPlDlFEaL3IUbcWnnPcALI).
The videos walked through arcade docs and demonstrated how to open arcade
windows, draw shapes, and use keyboard input.


### Graphics:
- Explosion graphics from https://www.explosiongenerator.com/, via Arcade
resources folder.
- Other images from Space Shooter (Redux, plus fonts and sounds) by [Kenney
Vleugels](www.kenney.nl), 
[licensed under Creative Commons](https://kenney.nl/assets/space-shooter-redux).


### Sounds:
- Background music and game won music come from the Apple iMovie library.
- Other sounds come from [Kenny Vleugels](www.kenney.nl), see above.


## A last note about the code
I learned about classes and inheritance through this project, and gained
experience reading sourcecode. At the time of this project, I had not yet
learned about packages, encapsulation or MVC architecture. If I were to write
this program again, I would employ those principles.

Comments in the code were initially meant just for myself, so they are verbose.