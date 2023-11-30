Benjamin Wootten
bwootten@udel.edu

I want to create a 3d puzzle game where the player can rotate the level
by panning the mouse and can interact with different types of blocks in order to
move one or more blue blocks to the green goal point.
Currently, I have decided on white, immovable blocks that serve as obstacles;
red, scalable blocks that can be grown and shrunk by the player and used to push the
blue blocks around the level; in addition to the blue and green blocks previously
mentioned. I may add more types allowing more creative level designs,
but these are my fundamentals.
The scalable red blocks are the player's main means of interacting with the level,
and a very direct usage of the theme 'SCALE'.

To run this program you need to install the library NumPy

![Sketch demonstrating the level with each type of block present](https://github.com/BenjaminWootten/Final-Project-CISC-108-honors/blob/main/Images/CISC108%20final%20project%20sketch.png)

Phase 1 task list:
- [x] The 3d level base can be panned around by the player
- [x] Function to create a box on the level base and declare its type
- [x] 1 basic level for testing mechanics exists
- [x] Red boxes can be scaled by the player clicking on them
- [x] Scaling up one red box will scale all others back to their original size,
        meaning only one can be scaled up at a time

Milestone 1: https://youtu.be/d-GdJBqEhjQ

Phase 2 task list:
This will likely be the most difficult part of the project as I will need to create
some sort of collision system for the 3d objects
- [x] Blue boxes can be pushed by red boxes
- [x] Red and blue boxes can be stopped by white boxes blocking them
- [x] Blue boxes can detect a level completion when they contact green boxes

Milestone 2: https://youtu.be/sCeHHbo-zNE

Phase 3 task list:
- [x] System for creating levels easily
- [x] Actual creation of 10 or so levels
- [x] Reset level button
- [x] Main menu
- [x] Level select screen
- [x] Track completed and uncompleted levels on level select screen
- [x] Return to level select upon completing a level
- [x] Victory screen upon all levels being completed
- [ ] Game instructions on main menu

Extra task list:
- [ ] New types of blocks
- [ ] New levels utilizing these