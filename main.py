from designer import *
import numpy as np
import math as m
from dataclasses import dataclass
from levels import change_level

@dataclass
class Box:
    color: str
    size: list[float] # [x,y,z]
    center: list[float] # [x,y,z]
    points: list[list[float]] # [[x,y,z]]
    projected_points: list[list[float]] # [[x,y]]
    vertices: list[DesignerObject]
    lines: list[DesignerObject]
    faces: list[DesignerObject]
    is_moving: bool
    movement: list[float] # [x,y,z]


@dataclass
class World:
    base: Box
    boxes: list[list[Box]] # [[Red], [White], [Blue], [Green]]
    box_render_order: list[Box]
    angle: list[float] # [x, y, z]
    pan_pos: list[int]
    is_panning: bool
    is_clicking_interactable: bool
    scaled_up_red_box: Box
    previously_scaled_up_red_box: Box
    is_scaling: bool

level_number = 4

CENTER = [get_width()/2, get_height()/2]
SCALE = 50.0 # Scale for rendering
SCALE_MAX = 3.0 # Max size of red boxes
SCALE_SPEED = 0.05 # Scale speed of red boxes

PROJECTION_MATRIX = np.matrix([
    [1, 0, 0],
    [0, 1, 0]
])


def generate_points(size: list[float], position: list[float]) -> list[[]]:
    '''
    This function generates a set of 3d coordinates representing the 8 vertices of a box

    Args:
        size (list[float]): a list of 3 floats representing the x, y, and z sizes of the box
        position (list[float]): a list of 3 floats representing the x, y, and z positions of the box

    Returns:
        list[[]]: A list of 8 3x1 NumPy matrices, representing the x, y, and z position of the 8 vertices
    '''
    points = []
    xpos = position[0]
    ypos = position[1]
    zpos = position[2]
    xsize = size[0]
    ysize = size[1]
    zsize = size[2]
    #top 4 points
    points.append(np.matrix([xpos - xsize / 2, ypos - ysize / 2, zpos + zsize / 2]))
    points.append(np.matrix([xpos + xsize / 2, ypos - ysize / 2, zpos + zsize / 2]))
    points.append(np.matrix([xpos + xsize / 2, ypos + ysize / 2, zpos + zsize / 2]))
    points.append(np.matrix([xpos - xsize / 2, ypos + ysize / 2, zpos + zsize / 2]))
    # bottom 4 points
    points.append(np.matrix([xpos - xsize / 2, ypos - ysize / 2, zpos - zsize / 2]))
    points.append(np.matrix([xpos + xsize / 2, ypos - ysize / 2, zpos - zsize / 2]))
    points.append(np.matrix([xpos + xsize / 2, ypos + ysize / 2, zpos - zsize / 2]))
    points.append(np.matrix([xpos - xsize / 2, ypos + ysize / 2, zpos - zsize / 2]))

    return points

def scale_points(box: Box, scale: list[float]):
    '''
    This function scales the given box by the given amount

    Args:
        box (Box): the box object to be scaled
        scale (float): the amount to scale the box by

    Returns:
        None
    '''
    box.size[0] += scale[0]
    box.size[1] += scale[1]
    box.size[2] += scale[2]
    box.center[1] -= scale[1]/2

def create_line(i: int, j: int, points: list[[]]) -> DesignerObject:
    '''
    This function draws a line in the viewport, making up one edge of a box, based on the list of 2d coordinates and
    2 indexes given

    Args:
        i (int): the index in the list of the first point of the line
        j (int): the index in the list of the second point of the line
        points (list[[]]): the list of 2d coordinates representing a projected cube to be used for drawing lines

    Returns:
        DesignerObject: The line object generated from the list and indexes
    '''
    # Returns a line connecting points at indexes i and j in list points
    return line("black", points[i][0], points[i][1], points[j][0], points[j][1])

def create_face(color: str, i: int, j: int, k: int, l: int, points: list[[]]) -> DesignerObject:
    '''
    This function draws a shape in the viewport, making up one face of a box, based on the list of 2d coordinates
    and 2 indexes given

    Args:
        i (int): the index in the list of the first vertex of the shape
        j (int): the index in the list of the second vertex of the shape
        k (int): the index in the list of the third vertex of the shape
        l (int): the index in the list of the fourth vertex of the shape
        points (list[[]]): the list of 2d coordinates representing a projected cube to be used for drawing shapes

    Returns:
        DesignerObject: The shape object generated from the list and indexes
    '''
    # Returns a shape of chosen color connecting points at indexes i, j, k, and l in list points
    return shape(color, [points[i][0], points[i][1], points[j][0], points[j][1], points[k][0], points[k][1],
                         points[l][0], points[l][1]], absolute=True, anchor='topleft')


def create_box(size: list[float], position: list[float], type: str) -> Box:
    '''
    This function generates a box object of the given size, position, and type

    Args:
        size (list[float]): a list containing the x, y, and z sizes of the box
        position (list[float]): a list containing the x, y, and z positions of the box
        type (str): can be either "base", "white", "red", "blue", or "green", which correspond to the color and
        behavior of the box

    Returns:
        Box: the box object generated from the inputs
    '''
    # Returns a box of given type, size, and center position

    projected_points = []
    vertices = []
    lines = []
    faces = []

    if type == "base":
        type = "white"

    points = generate_points(size, position)

    for point in points:
        # @ is the matrix multiplication operator
        # Use transpose to change point from 1x3 to 3x1 matrix to make multiplication with 2d matrix compatible
        projected2d = PROJECTION_MATRIX @ point.transpose()

        # Set x and y to projected position
        x = projected2d[0, 0] * SCALE + CENTER[0]
        y = projected2d[1, 0] * SCALE + CENTER[1]

        # Add 8 circles representing the vertices
        vertices.append(circle("black", 5, x, y))

        # Add the coordinates of the projected position to projected_points
        projected_points.append([x, y])

    # Add 12 lines outlining cube to list lines
    for p in range(4):
        lines.append(create_line(p, (p + 1) % 4, projected_points))
        lines.append(create_line(p + 4, (p + 1) % 4 + 4, projected_points))
        lines.append(create_line(p, p + 4, projected_points))

    faces.append(create_face(type, 0, 1, 2, 3, projected_points))
    faces.append(create_face(type, 4, 5, 6, 7, projected_points))
    for p in range(4):
        faces.append(create_face(type, p, (p + 1) % 4, (p + 1) % 4 + 4, p + 4, projected_points))

    return Box(type, size, position, points, projected_points, vertices, lines, faces, False,
               [0.0, 0.0, 0.0])

def destroy_box(box: Box):
    '''
    This function destroys a box's rendered DesignerObjects, but not its data. This allows all the
    DesignerObjects to be regenerated based on updated data

    Args:
        box (Box): the box to be destroyed

    Returns:
        None
    '''
    for vertex in box.vertices:
        destroy(vertex)
    for line in box.lines:
        destroy(line)
    for face in box.faces:
        destroy(face)

def draw_boxes(world: World):
    '''
        This function is run when updating and updates every box in the world. This includes updating size, position,
        rotation, and projection of all boxes.

        Args:
            world (World): the current world data

        Returns:
            None
        '''
    rotation_x_matrix = np.matrix([
        [1, 0, 0],
        [0, m.cos(world.angle[0]), -m.sin(world.angle[0])],
        [0, m.sin(world.angle[0]), m.cos(world.angle[0])]
    ])

    rotation_y_matrix = np.matrix([
        [m.cos(world.angle[1]), 0, m.sin(world.angle[1])],
        [0, 1, 0],
        [-m.sin(world.angle[1]), 0, m.cos(world.angle[1])]
    ])

    rotation_z_matrix = np.matrix([
        [m.cos(world.angle[2]), -m.sin(world.angle[2]), 0],
        [m.sin(world.angle[2]), m.cos(world.angle[2]), 0],
        [0, 0, 1]
    ])

    for box in world.box_render_order:
        # Update each box based on box_render_order

        destroy_box(box)

        box.points.clear()
        box.points = generate_points(box.size, box.center)

        # Calculating rotation and projection
        for index, point in enumerate(box.points):
            # @ is the matrix multiplication operator
            # Use transpose to change point from 1x3 to 3x1 matrix to make multiplication with 2d matrix compatible

            # For each 3d coordinate, multiply by rotation_z to rotate points about the z axis
            rotated2d = rotation_x_matrix @ point.transpose()
            rotated2d = rotation_y_matrix @ rotated2d
            rotated2d = rotation_z_matrix @ rotated2d
            # For each 3d coordinate, multiply by projection_matrix to convert to 2d coordinate
            projected2d = PROJECTION_MATRIX @ rotated2d

            # Set projected x and y values for each coordinate
            x = projected2d[0, 0] * SCALE + CENTER[0]
            y = projected2d[1, 0] * SCALE + CENTER[1]

            # Add x and y values to list of projected points
            box.projected_points[index] = [x, y]

            # Move corresponding vertices to newly calculated positions
            box.vertices[index].x = x
            box.vertices[index].y = y


        # Reloading box geometry
        # Generates 6 new faces
        box.faces[0] = create_face(box.color, 0, 1, 2, 3, box.projected_points)
        box.faces[1] = create_face(box.color, 4, 5, 6, 7, box.projected_points)
        for p in range(4):
            box.faces[p + 2] = create_face(box.color, p, (p + 1) % 4, (p + 1) % 4 + 4, p + 4, box.projected_points)\

        # Generates 12 new lines
        for p in range(4):
            box.lines[p] = create_line(p, (p + 1) % 4, box.projected_points)
            box.lines[p + 4] = create_line(p + 4, (p + 1) % 4 + 4, box.projected_points)
            box.lines[p + 8] = create_line(p, p + 4, box.projected_points)

        # Generates 8 new vertices
        for index, projected_point in enumerate(box.projected_points):
            box.vertices[index] = circle("black", 5, projected_point[0], projected_point[1])

def main(world: World):

    calculate_render_order(world)

    draw_boxes(world)

    # Rotating boxes with mouse pan
    if world.is_panning:
        pan_world(world)

    if world.is_scaling:
        directions = [True, True, True]
        directions[0] = (check_box_collision(world, world.scaled_up_red_box, 0, 1) and
                         check_box_collision(world, world.scaled_up_red_box, 0, -1))
        directions[2] = (check_box_collision(world, world.scaled_up_red_box, 2, 1) and
                         check_box_collision(world, world.scaled_up_red_box, 2, -1))

        scale_red_box(world, directions)

        move_blue_box(world, world.scaled_up_red_box)




def calculate_render_order(world: World):
    '''
    This function orders all boxes in the world in a list based on their position relative to the camera, assuring they
    are rendered in the correct order

    Args:
        world (World): the current world data

    Returns:
        None
    '''
    # Clear render order so it can be recalculated
    world.box_render_order.clear()

    for type in world.boxes:
        # Run through all 4 box types

        for box in type:
            # This loop adds all boxes to a new list insertion sorted from furthest to closest to the camera,
            # therefore preventing layering issues upon rendering

            i = 0

            # When y rotation is between 45 degrees and 135 degrees, render from smallest x to largest x
            if (m.pi * 2 / 8) <= world.angle[1] % (m.pi * 2) < (m.pi * 2 / 8) * 3:
                for render_box in world.box_render_order:
                    if box.center[0] > render_box.center[0]:
                        i += 1
                    # If 2 boxes have the same x, check if rotation is greater than or less than 90 degrees and render
                    # based on z value
                    elif box.center[0] == render_box.center[0]:
                        if world.angle[1] % (m.pi * 2) > (m.pi * 2 / 8) * 2:
                            if box.center[2] > render_box.center[2]:
                                i += 1
                        else:
                            if box.center[2] < render_box.center[2]:
                                i += 1

            # When y rotation is between 135 degrees and 225 degrees, render from smallest z to largest z
            if (m.pi * 2 / 8) * 3 <= world.angle[1] % (m.pi * 2) < (m.pi * 2 / 8) * 5:
                for render_box in world.box_render_order:
                    if box.center[2] > render_box.center[2]:
                        i += 1
                    # If 2 boxes have the same z, check if rotation is greater than or less than 180 degrees and render
                    # based on x value
                    elif box.center[2] == render_box.center[2]:
                        if world.angle[1] % (m.pi * 2) > (m.pi * 2 / 8) * 4:
                            if box.center[0] < render_box.center[0]:
                                i += 1
                        else:
                            if box.center[0] > render_box.center[0]:
                                i += 1

            # When y rotation is between 225 degrees and 315 degrees, render from largest x to smallest x
            if (m.pi * 2 / 8) * 5 <= world.angle[1] % (m.pi * 2) < (m.pi * 2 / 8) * 7:
                for render_box in world.box_render_order:
                    if box.center[0] < render_box.center[0]:
                        i += 1
                    # If 2 boxes have the same x, check if rotation is greater than or less than 270 degrees and render
                    # based on z value
                    elif box.center[0] == render_box.center[0]:
                        if world.angle[1] % (m.pi * 2) > (m.pi * 2 / 8) * 6:
                            if box.center[2] < render_box.center[2]:
                                i += 1
                        else:
                            if box.center[2] > render_box.center[2]:
                                i += 1

            # When y rotation is greater than 315 degrees or fewer than 45 degrees, render from largest z to smallest z
            if (m.pi * 2 / 8) * 7 <= world.angle[1] % (m.pi * 2) or world.angle[1] % (m.pi * 2) < (m.pi * 2 / 8):
                for render_box in world.box_render_order:
                    if box.center[2] < render_box.center[2]:
                        i += 1
                    # If 2 boxes have the same z, check if rotation is less than 45 degrees or greater than 315 degrees
                    # and render based on x value
                    elif box.center[2] == render_box.center[2]:
                        if world.angle[1] % (m.pi * 2) < (m.pi / 2):
                            if box.center[0] > render_box.center[0]:
                                i += 1
                        else:
                            if box.center[0] < render_box.center[0]:
                                i += 1

            world.box_render_order.insert(i, box)

    # Rendering level base before or after cubes based on x rotation
    if world.angle[0] % (m.pi * 2) > m.pi and (
            world.angle[1] % (m.pi * 2) <= (m.pi / 2) or world.angle[1] % (m.pi * 2) > (m.pi * 3 / 2)):
        world.box_render_order.append(world.base)
    elif world.angle[0] % (m.pi * 2) < m.pi and ((m.pi / 2) < world.angle[1] % (m.pi * 2) < (m.pi * 3 / 2)):
        world.box_render_order.append(world.base)
    else:
        world.box_render_order.insert(0, world.base)


def red_box_interaction(world: World):

    # Creates a list containing all boxes colliding with the mouse upon clicking
    boxes_clicked = []
    for type in world.boxes:
        for box in type:
            for face in box.faces:
                if colliding_with_mouse(face):
                    boxes_clicked.append(box)

    # Checks if any boxes were clicked as a safeguard
    if boxes_clicked:
        # Calculates which of all clicked boxes is the closest to the camera using world.box_render_order
        closest_clicked = boxes_clicked[0]
        for box in world.box_render_order:
            for box_clicked in boxes_clicked:
                if box == box_clicked:
                    closest_clicked = box_clicked

        # Checks if the closest clicked box is red
        if closest_clicked.color == "red" and not world.is_scaling:
            world.is_clicking_interactable = True
            if closest_clicked.size[1] == 1.0 and closest_clicked != world.scaled_up_red_box:
                world.previously_scaled_up_red_box = world.scaled_up_red_box
                world.scaled_up_red_box = closest_clicked
                world.is_scaling = True
            else:
                world.is_clicking_interactable = False

    else:
        world.is_clicking_interactable = False

    boxes_clicked.clear()

def scale_red_box(world: World, directions: list[bool]):

    scale_speed = [0,0,0]
    if directions[0]:
        scale_speed[0] = SCALE_SPEED
    if directions[1]:
        scale_speed[1] = SCALE_SPEED
    if directions[2]:
        scale_speed[2] = SCALE_SPEED


    # Scales up red box when it is clicked and not already scaled
    if world.scaled_up_red_box:
        if world.scaled_up_red_box.size[1] < SCALE_MAX:

            scale_points(world.scaled_up_red_box, scale_speed)

            # Checks if there is a red box currently scaled up and scales it down
            if world.previously_scaled_up_red_box:
                scale_down_speed = [0,0,0]
                if world.previously_scaled_up_red_box.size[0] > 1.0:
                    scale_down_speed[0] = -SCALE_SPEED
                if world.previously_scaled_up_red_box.size[1] > 1.0:
                    scale_down_speed[1] = -SCALE_SPEED
                if world.previously_scaled_up_red_box.size[2] > 1.0:
                    scale_down_speed[2] = -SCALE_SPEED
                scale_points(world.previously_scaled_up_red_box, scale_down_speed)
        else:
            world.is_scaling = False

def move_blue_box(world: World, pushing_box: Box):

    for blue_box in world.boxes[2]: # 2 is blue boxes
        if not blue_box.is_moving:
            if pushing_box.color == "red":

                if pushing_box.center[0] == blue_box.center[0] and pushing_box.size[2] > 1.0:
                    if pushing_box.center[2] == blue_box.center[2] - 1:
                        blue_box.is_moving = True
                        blue_box.movement[2] = SCALE_SPEED/2
                    elif pushing_box.center[2] == blue_box.center[2] + 1:
                        blue_box.is_moving = True
                        blue_box.movement[2] = -SCALE_SPEED/2

                elif pushing_box.center[2] == blue_box.center[2] and pushing_box.size[0] > 1.0:
                    if pushing_box.center[0] == blue_box.center[0] - 1:
                        blue_box.is_moving = True
                        blue_box.movement[0] = SCALE_SPEED/2
                    elif pushing_box.center[0] == blue_box.center[0] + 1:
                        blue_box.is_moving = True
                        blue_box.movement[0] = -SCALE_SPEED/2

            elif pushing_box.color == "blue":
                if round(pushing_box.center[0]) == blue_box.center[0]:
                    if (round(pushing_box.center[2]) == blue_box.center[2] - 1 or
                            round(pushing_box.center[2]) == blue_box.center[2] + 1):
                        blue_box.is_moving = True
                        blue_box.movement[2] = pushing_box.movement[2]
                if round(pushing_box.center[2]) == blue_box.center[2]:
                    if (round(pushing_box.center[0]) == blue_box.center[0] - 1 or
                            round(pushing_box.center[0]) == blue_box.center[0] + 1):
                        blue_box.is_moving = True
                        blue_box.movement[0] = pushing_box.movement[0]

            if blue_box.is_moving:
                move_blue_box(world, blue_box)

        else:
            blue_box.center[0] += blue_box.movement[0]
            blue_box.center[2] += blue_box.movement[2]
            if pushing_box.size[1] >= SCALE_MAX or (pushing_box.color == "blue" and pushing_box.is_moving == False):
                blue_box.is_moving = False
                blue_box.movement = [0, 0, 0]
                blue_box.center[0] = round(blue_box.center[0])
                blue_box.center[2] = round(blue_box.center[2])

def check_box_collision(world: World, checked_box: Box, axis: int, direction: int) -> bool:
    # Run through all boxes in the world and filter out any that aren't white or blue
    other_axis = 0
    if axis == 0:
        other_axis = 2

    for index, type in enumerate(world.boxes):
        if index == 1 or index == 2 or index == 0: # 1 is white, 2 is blue, 0 is red
            for box in type:
                if (checked_box.center[axis] == box.center[axis] + direction and
                        checked_box.center[other_axis] == box.center[other_axis]):
                    #Check if a blue, red,  or white box is directly next to the box we are checking along the given
                    #axis and direction, which is either 1 or -1
                    if box.color == "white" or box.color == "red":
                        # If the neighboring box is white or red, return false
                        return False
                    else:
                        # If the neighboring box is blue, check if it has a white box in the next space over
                        return check_box_collision(world, box, axis, direction)
    return True




def pan_start(world: World, x, y):
    if not world.is_clicking_interactable:
        world.pan_pos = [x, y]
        world.is_panning = True

def pan_world(world: World):
    world.angle[1] -= (get_mouse_x() - world.pan_pos[0]) / 500

    if world.angle[1] % (m.pi * 2) < (m.pi / 2) or world.angle[1] % (m.pi * 2) >= (m.pi * 3 / 2):
        world.angle[0] += (get_mouse_y() - world.pan_pos[1]) / 500
    elif world.angle[1] % (m.pi * 2) >= (m.pi / 2) and world.angle[1] % (m.pi * 2) < (m.pi * 3 / 2):
        world.angle[0] -= (get_mouse_y() - world.pan_pos[1]) / 500

    world.pan_pos[0] = get_mouse_x()
    world.pan_pos[1] = get_mouse_y()

def pan_end(world: World):
    world.is_panning = False


def detect_win(world: World) -> bool:
    green_boxes_filled = []
    for green_box in world.boxes[3]: # 3 is green boxes
        for blue_box in world.boxes[2]: # 2 is blue boxes
            if blue_box.center == green_box.center:
                green_boxes_filled.append(True)
                blue_box.color = "purple"
    return len(green_boxes_filled) == len(world.boxes[3])

def end_level(world: World):
    global level_number
    level_number += 1
    for box in world.box_render_order:
        destroy_box(box)
    start()


def create_level(level: list[list[str]], base_x, base_z) -> World:
    #   = empty
    # r = red
    # w = white
    # b = blue
    # g = green
    base = create_box([base_x, 1, base_z], [0,1,0], "base")
    red = []
    white = []
    blue = []
    green = []
    for i, row in enumerate(reversed(level)):
        for j, character in enumerate(row):
            if character == "r":
                red.append(create_box([1,1,1], [j-m.floor(base_x/2), 0, i-m.floor(base_z/2)],
                                      "red"))
            elif character == "w":
                white.append(create_box([1, 1, 1], [j-m.floor(base_x/2), 0, i-m.floor(base_z/2)],
                                        "white"))
            elif character == "b":
                blue.append(create_box([1, 1, 1], [j-m.floor(base_x/2), 0, i-m.floor(base_z/2)],
                                       "blue"))
            elif character == "g":
                green.append(create_box([1, 1, 1], [j-m.floor(base_x/2), 0, i-m.floor(base_z/2)],
                                        "green"))
    return World(base, [red, white, blue, green], [], [0.3, 0.3, 0.0], [0, 0], False, False, None, None, False)


def create_world() -> World:
    set_window_color("black")

    return create_level(change_level(level_number), 9, 9)



when('starting', create_world)

when('clicking', red_box_interaction)

when('input.mouse.down', pan_start)
when('input.mouse.up', pan_end)

when(detect_win, end_level)

when('updating', main)
start()