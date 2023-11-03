from designer import *
import numpy as np
import math as m
from dataclasses import dataclass

@dataclass
class Box:
    scale: int
    projected_points: list[list[int]]
    vertices: list[DesignerObject]
    lines: list[DesignerObject]
    faces: list[DesignerObject]


@dataclass
class World:
    level_base: Box
    boxes: list[Box]
    angle: list[float] # [x, y, z]
    click_pos: list[int]
    is_clicking: bool


CENTER = [get_width()/2, get_height()/2]

PROJECTION_MATRIX = np.matrix([
    [1, 0, 0],
    [0, 1, 0]
])

# ROTATION_X_MATRIX = np.matrix([
#     [1, 0, 0],
#     [0, m.cos(world.angle[0]), -m.sin(world.angle[0])],
#     [0, m.sin(world.angle[0]), m.cos(world.angle[0])]
# ])
#
# ROTATION_Y_MATRIX = np.matrix([
#     [m.cos(world.angle[1]), 0, m.sin(world.angle[1])],
#     [0, 1, 0],
#     [-m.sin(world.angle[1]), 0, m.cos(world.angle[1])]
# ])
#
# ROTATION_Z_MATRIX = np.matrix([
#     [m.cos(world.angle[2]), -m.sin(world.angle[2]), 0],
#     [m.sin(world.angle[2]), m.cos(world.angle[2]), 0],
#     [0, 0, 1]
# ])


def generate_points(size: list[int], position: list[int]) -> list[[]]:
    # Returns a list of points representing a box based on the given xyz size and xyz position
    points = []
    xpos = position[0]
    ypos = position[1]
    zpos = position[2]
    xsize = size[0]
    ysize = size[1]
    zsize = size[2]
    #top 4
    points.append(np.matrix([xpos - xsize / 2, ypos - ysize / 2, zpos + zsize / 2]))
    points.append(np.matrix([xpos + xsize / 2, ypos - ysize / 2, zpos + zsize / 2]))
    points.append(np.matrix([xpos + xsize / 2, ypos + ysize / 2, zpos + zsize / 2]))
    points.append(np.matrix([xpos - xsize / 2, ypos + ysize / 2, zpos + zsize / 2]))
    # bottom 4
    points.append(np.matrix([xpos - xsize / 2, ypos - ysize / 2, zpos - zsize / 2]))
    points.append(np.matrix([xpos + xsize / 2, ypos - ysize / 2, zpos - zsize / 2]))
    points.append(np.matrix([xpos + xsize / 2, ypos + ysize / 2, zpos - zsize / 2]))
    points.append(np.matrix([xpos - xsize / 2, ypos + ysize / 2, zpos - zsize / 2]))

    return points

def create_line(i: int, j: int, points) -> DesignerObject:
    # Returns a line connecting points at indexes i and j in list points
    return line("black", points[i][0], points[i][1], points[j][0], points[j][1])

def create_face(color: str, i: int, j: int, k: int, l: int, points) -> DesignerObject:
    # Returns a shape of chosen color connecting points at indexes i, j, k, and l in list points
    return shape(color, [points[i][0], points[i][1], points[j][0], points[j][1], points[k][0], points[k][1], points[l][0], points[l][1]], absolute=True, anchor='topleft')


def create_box(size: list[int], position: list[int], type: str) -> Box:
    # Returns a box of given type, size, and center posistion

    starting_scale = 100.0
    projected_points = []
    vertices = []
    lines = []
    faces = []

    points = generate_points(size, position)

    for point in points:
        # @ is the matrix multiplication operator
        # Use transpose to change point from 1x3 to 3x1 matrix to make multiplication with 2d matrix compatible
        projected2d = PROJECTION_MATRIX @ point.transpose()

        # Set x and y to projected position
        x = projected2d[0, 0] * starting_scale + CENTER[0]
        y = projected2d[1, 0] * starting_scale + CENTER[1]

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

    return Box(starting_scale, projected_points, vertices, lines, faces)



def create_World() -> World:
    base = create_box([4,2,4], [0,0,0], "white")
    box = create_box([2, 2, 2], [2, 2, 2], "red")
    return(base, [box], [0.0, 0.0, 0.0], [0, 0], False)


when('starting', create_World)
start()