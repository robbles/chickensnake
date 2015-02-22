from flask import current_app as app

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

HEAD = 'head'
FOOD = 'food'
BODY = 'body'
EMPTY = 'empty'
BOUNDARY = 'boundary'
COLLISION = 'collision'

def dimensions(board):
    ncols = len(board)
    nrows = len(board[0])
    return ncols, nrows

def adjacent(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1

def manhattan_dist(pos1, pos2):
    return (abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]))
