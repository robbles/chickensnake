from flask import current_app as app
import log

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

def safe_directions(board, pos, allowed_tiles=[EMPTY, FOOD]):
    good = []
    for d in DIRECTIONS:
        safe, contents = check_square(board, pos, d, allowed_tiles)
        if safe:
            good.append((d, contents))

    return good

def check_square(board, pos, direction, allowed_tiles=[EMPTY, FOOD]):
    x = pos[0]
    y = pos[1]
    ncols, nrows = dimensions(board)

    if direction == UP:
        y -= 1
    elif direction == DOWN:
        y += 1
    elif direction == LEFT:
        x -= 1
    else:
        x += 1

    app.logger.debug('Checking for move %s from %s to %s',
        direction, pos, (x, y))

    safe, contents = True, EMPTY

    # check the boundaries
    if (x >= ncols or x < 0) or (y >= nrows or y < 0):
        # out of boundaries
        safe, contents = False, BOUNDARY
    else:
        # check for invalid tile according to allowed_tiles
        tile = board[x][y]
        contents = tile['state']
        if contents not in allowed_tiles:
            safe = False

    app.logger.debug('%s, contains %s',
        log.green('safe') if safe else log.red('unsafe'), contents)

    return safe, contents

def dimensions(board):
    ncols = len(board)
    nrows = len(board[0])
    return ncols, nrows

def adjacent(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1

def manhattan_dist(pos1, pos2):
    return (abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]))
