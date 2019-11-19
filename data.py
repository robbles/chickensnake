from typing import List

Grid = List[List[str]]

UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"

DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

HEAD = "head"
FOOD = "food"
BODY = "body"
EMPTY = "empty"
BOUNDARY = "boundary"
COLLISION = "collision"


class TurnContext(object):
    turn: int
    my_snake: dict
    position: tuple
    health: int
    width: int
    height: int
    grid: List[List[str]]
    snakes: list
    foods: list

    def __init__(
        self,
        turn: int,
        grid: Grid,
        width: int,
        height: int,
        my_snake: dict,
        snakes: List[dict],
        foods: List[dict],
    ):
        self.turn = turn
        self.my_snake = my_snake
        my_snake_head = my_snake["body"][0]
        self.position = (my_snake_head["x"], my_snake_head["y"])
        self.health = my_snake["health"]
        self.width = width
        self.height = height
        self.grid = grid
        self.snakes = [
            [(coord["x"], coord["y"]) for coord in snake["body"]]
            for snake in snakes
            if snake["id"] != my_snake["id"]
        ]
        self.foods = [(coord["x"], coord["y"]) for coord in foods]


def build_turn_context(request_data: dict) -> TurnContext:
    board = request_data["board"]

    width = board["width"]
    height = board["height"]
    grid = build_grid(width, height, board["snakes"], board["food"])

    return TurnContext(
        turn=request_data["turn"],
        grid=grid,
        width=board["width"],
        height=board["height"],
        my_snake=request_data["you"],
        snakes=board["snakes"],
        foods=board["food"],
    )


# TODO: switch to (row, column) since we're building this structure
# internally?
def build_grid(width: int, height: int, snakes: List[dict], foods: List[dict]) -> Grid:

    # Initialize grid to all empty
    grid = [[EMPTY for row in range(height)] for column in range(width)]

    # Place all food on grid
    for food in foods:
        x, y = food["x"], food["y"]
        grid[x][y] = FOOD

    # Place all snakes on grid
    for snake in snakes:
        body = snake["body"]
        head = body[0]
        grid[head["x"]][head["y"]] = HEAD
        for node in body[1:]:
            grid[node["x"]][node["y"]] = BODY

    return grid


def has_eaten(snake: dict):
    # Snake body expands up to 3 squares at the start, then stays at 3 until 1
    # turn after the first food is eaten.
    return len(snake["body"]) > 3


def adjacent(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1


def manhattan_dist(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
