Growth Matrix

Final Project for CISC 108
To run this program you need to install the libraries NumPy and Designer

Growth Matrix is a 3d puzzle game about using scalable boxes to push other boxes to the goal.

About:
In Growth Matrix the player can rotate the level  by panning the mouse and can interact with different types of blocks
in order to move one or more blue blocks to the green goal point. It has white, immovable blocks that serve as
obstacles; red, scalable blocks that can be grown and shrunk by the player and used to push the blue blocks around the
level; in addition to the blue and green blocks previously mentioned. The scalable red blocks are the player's main
means of interacting with the level, and a very direct usage of the theme 'SCALE'.

Preview: https://youtu.be/rJGWBwJ9VzI

Instructions:
The matrix can be panned around by clicking and dragging the mouse.
Red boxes can be grown by clicking on them.
Only one Red box can be grown at a time.
Blue boxes can be pushed by growing Red boxes or by other Blue boxes.
White boxes can block the growth of Red boxes in one or two directions.
To complete each matrix all Green boxes must be filled in with Blue boxes.
Filled Green boxes will turn Purple.

Author:
Benjamin Wootten
bwootten@udel.edu

Acknowledgements:
Designer documentation: https://designer-edu.github.io/designer/contents.html
3D projection method: Pythonista_ on YouTube https://www.youtube.com/watch?v=qw0oY6Ld-L0

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
- [x] Game instructions on main menu

Extra task list:
- [ ] New types of blocks
- [ ] New levels utilizing these

concept image
![Sketch demonstrating the level with each type of block present](https://github.com/BenjaminWootten/Final-Project-CISC-108-honors/blob/main/Images/CISC108%20final%20project%20sketch.png)