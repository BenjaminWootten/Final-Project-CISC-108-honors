from designer import *
import numpy as np
import math as m
from dataclasses import dataclass

@dataclass
class Box:
    color: str
    scale: float
    size: list[float] # [x,y,z]
    center: list[float] # [x,y,z]
    points: list[list[float]] # [[x,y,z]]
    projected_points: list[list[float]] # [[x,y]]
    vertices: list[DesignerObject]
    lines: list[DesignerObject]
    faces: list[DesignerObject]


@dataclass
class World:
    base: Box
    boxes: list[list[Box]] # [[Red], [White], [Blue], [Green]]
    box_render_order: list[Box]
    angle: list[float] # [x, y, z]
    pan_pos: list[int]
    is_panning: bool
    is_clicking_interactable: bool
    is_scaling: bool
    scaled_up_red_box: Box
    previously_scaled_up_red_box: Box


CENTER = [get_width()/2, get_height()/2]
SCALE = 50.0

PROJECTION_MATRIX = np.matrix([
    [1, 0, 0],
    [0, 1, 0]
])


def generate_points(size: list[float], position: list[float]) -> list[[]]:
    # Returns a list of points representing a box based on the given xyz size and xyz position
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

def scale_points(box: Box, scale: float):
    box.size[0] += scale
    box.size[1] += scale
    box.size[2] += scale
    box.center[1] -= scale/2

def create_line(i: int, j: int, points) -> DesignerObject:
    # Returns a line connecting points at indexes i and j in list points
    return line("black", points[i][0], points[i][1], points[j][0], points[j][1])

def create_face(color: str, i: int, j: int, k: int, l: int, points) -> DesignerObject:
    # Returns a shape of chosen color connecting points at indexes i, j, k, and l in list points
    return shape(color, [points[i][0], points[i][1], points[j][0], points[j][1], points[k][0], points[k][1], points[l][0], points[l][1]], absolute=True, anchor='topleft')


def create_box(size: list[float], position: list[float], type: str) -> Box:
    # Returns a box of given type, size, and center position

    starting_scale = 1.0
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

    return Box(type, starting_scale, size, position, points, projected_points, vertices, lines, faces)

def destroy_box(box: Box):
    for vertex in box.vertices:
        destroy(vertex)
    for line in box.lines:
        destroy(line)
    for face in box.faces:
        destroy(face)

def update_boxes(world: World):

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

    # Clear render order so it can be recalculated
    world.box_render_order.clear()

    for type in world.boxes:
        # Run through all 4 box types

        for box in type:
            # This loop adds all boxes to a new list insertion sorted from furthest to closest to the camera,
            # therefore preventing layering issues upon rendering

            i = 0

            # When y rotation is between 45 degrees and 135 degrees, render from smallest x to largest x
            if (m.pi * 2 / 8) <= world.angle[1] % (m.pi*2) < (m.pi * 2 / 8) * 3:
                for render_box in world.box_render_order:
                    if box.center[0] > render_box.center[0]:
                        i += 1
                    # If 2 boxes have the same x, check if rotation is greater than or less than 90 degrees and render
                    # based on z value
                    elif box.center[0] == render_box.center[0]:
                        if world.angle[1] % (m.pi*2) > (m.pi * 2 / 8) * 2:
                            if box.center[2] > render_box.center[2]:
                                i += 1
                        else:
                            if box.center[2] < render_box.center[2]:
                                i += 1

            # When y rotation is between 135 degrees and 225 degrees, render from smallest z to largest z
            if (m.pi * 2 / 8) * 3 <= world.angle[1] % (m.pi*2) < (m.pi * 2 / 8) * 5:
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
            if (m.pi * 2 / 8) * 5 <= world.angle[1] % (m.pi*2) < (m.pi * 2 / 8) * 7:
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
            if (m.pi * 2 / 8) * 7 <= world.angle[1] % (m.pi*2) or world.angle[1] % (m.pi*2) < (m.pi * 2 / 8):
                for render_box in world.box_render_order:
                    if box.center[2] < render_box.center[2]:
                        i += 1
                    # If 2 boxes have the same z, check if rotation is less than 45 degrees or greater than 315 degrees
                    # and render based on x value
                    elif box.center[2] == render_box.center[2]:
                        if world.angle[1] % (m.pi * 2) < (m.pi/2):
                            if box.center[0] > render_box.center[0]:
                                i += 1
                        else:
                            if box.center[0] < render_box.center[0]:
                                i += 1


            world.box_render_order.insert(i, box)


    # Rendering level base before or after cubes based on x rotation
    if world.angle[0] % (m.pi*2) > m.pi and (world.angle[1] % (m.pi*2) <= (m.pi/2) or world.angle[1] % (m.pi*2) > (m.pi*3/2)):
        world.box_render_order.append(world.base)
    elif world.angle[0] % (m.pi*2) < m.pi and ((m.pi/2) < world.angle[1] % (m.pi*2) < (m.pi*3/2)):
        world.box_render_order.append(world.base)
    else:
        world.box_render_order.insert(0, world.base)



    for box in world.box_render_order:
        # Update each box based on box_render_order

        destroy_box(box)

        box.points.clear()
        box.points = generate_points(box.size, box.center)

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


    # Rotating boxes with mouse pan
    if world.is_panning:
        pan_world(world)


    scale_speed = 0.05
    scale_limit = 2

    # Scales up red box when it is clicked
    if world.scaled_up_red_box:
        if world.scaled_up_red_box.size[0] < scale_limit:
            scale_points(world.scaled_up_red_box, scale_speed)
            # Checks if there is a red box currently scaled up and scales it down
            if world.previously_scaled_up_red_box:
                scale_points(world.previously_scaled_up_red_box, -scale_speed)


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
        if closest_clicked.color == "red":
            world.is_clicking_interactable = True
            world.is_scaling = True
            if closest_clicked.scale == 1.0 and closest_clicked != world.scaled_up_red_box:
                world.previously_scaled_up_red_box = world.scaled_up_red_box
                world.scaled_up_red_box = closest_clicked

    else:
        world.is_clicking_interactable = False

    boxes_clicked.clear()

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


def create_World() -> World:
    red_boxes = [create_box([1,1,1], [0,0,0], "red"), create_box([1,1,1], [-2,0,0], "red")]
    white_boxes = [create_box([1, 1, 1], [0, 0, 2], "white")]
    blue_boxes = [create_box([1,1,1], [0, 0, -2], "blue")]
    green_boxes = [create_box([1,1,1], [2, 0, 0], "green")]
    base = create_box([8, 1, 8], [0, 1, 0], "white")


    set_window_color("black")

    return World(base, [red_boxes, white_boxes,blue_boxes,green_boxes], [], [0.3, 0.3, 0.0], [0, 0], False, False, False, None, None)


when('starting', create_World)

when('clicking', red_box_interaction)

when('input.mouse.down', pan_start)
when('input.mouse.up', pan_end)

when('updating', update_boxes)
start()