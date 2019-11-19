import pytest

from data import build_grid, build_turn_context, TurnContext
from data import EMPTY, FOOD, HEAD, BODY


@pytest.fixture
def sample_snake():
    return {
        "id": "snake-id-string",
        "name": "Sneky Snek",
        "health": 41,
        "body": [{"x": 1, "y": 2,}, {"x": 2, "y": 2,}, {"x": 2, "y": 3,}],
    }


@pytest.fixture
def sample_request_body():
    return {
        "game": {"id": "game-id-string"},
        "turn": 4,
        "board": {
            "height": 15,
            "width": 16,
            "food": [{"x": 6, "y": 8,}],
            "snakes": [
                {
                    "id": "snake-1",
                    "name": "Other Snek",
                    "health": 70,
                    "body": [{"x": 5, "y": 2}, {"x": 6, "y": 2}],
                },
                {
                    "id": "snake-2",
                    "name": "Sneky Snek",
                    "health": 90,
                    "body": [{"x": 1, "y": 3}],
                },
            ],
        },
        "you": {
            "id": "snake-2",
            "name": "Sneky Snek",
            "health": 90,
            "body": [{"x": 1, "y": 3}],
        },
    }


def test_build_grid_empty():
    result = build_grid(width=3, height=4, snakes=[], foods=[])
    assert result == [[EMPTY] * 4] * 3


def test_build_grid_foods():
    result = build_grid(
        width=3, height=4, snakes=[], foods=[{"x": 1, "y": 2}, {"x": 2, "y": 0}]
    )
    assert result == [
        [EMPTY] * 4,
        [EMPTY, EMPTY, FOOD, EMPTY],
        [FOOD, EMPTY, EMPTY, EMPTY],
    ]


def test_build_grid_snakes(sample_snake):
    result = build_grid(width=3, height=4, snakes=[sample_snake], foods=[])
    assert result == [
        [EMPTY] * 4,
        [EMPTY, EMPTY, HEAD, EMPTY],
        [EMPTY, EMPTY, BODY, BODY],
    ]


def test_build_turn_context(sample_request_body):
    ctx = build_turn_context(sample_request_body)
    assert isinstance(ctx, TurnContext)
    assert ctx.turn == 4
    assert ctx.position == (1, 3)
    assert ctx.health == 90
    assert ctx.width == 16
    assert ctx.height == 15
    assert isinstance(ctx.grid, list)
    assert ctx.snakes == [[(5, 2), (6, 2)]]
    assert ctx.foods == [(6, 8)]
