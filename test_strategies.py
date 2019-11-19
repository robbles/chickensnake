import pytest

from tests import clone
from data import TurnContext
from data import UP, DOWN, LEFT, RIGHT
from strategies import (
    choose_strategy,
    RandomStrategy,
    CornerStrategy,
    PreferFoodStrategy,
    AvoidFoodStrategy,
)


@pytest.fixture
def sample_snake():
    return {
        "id": "snake-id-string",
        "name": "Sneky Snek",
        "health": 41,
        "body": [{"x": 1, "y": 3,}],
    }


@pytest.fixture
def directions():
    return [UP, DOWN, LEFT, RIGHT]


def test_choose_strategy_force_strategy(sample_snake):
    result = choose_strategy(
        TurnContext(0, 0, 0, [], sample_snake, [sample_snake], []),
        {"FORCE_STRATEGY": "RANDOM"},
    )
    assert isinstance(result, RandomStrategy)


def test_choose_strategy_corner_strategy(sample_snake):
    result = choose_strategy(TurnContext(0, 0, 0, [], sample_snake, [sample_snake], []))
    assert isinstance(result, CornerStrategy)


def test_choose_strategy_prefer_food_strategy(sample_snake):
    snake = clone(sample_snake, health=40)
    result = choose_strategy(TurnContext(0, 0, 0, [], snake, [snake], []))
    assert isinstance(result, PreferFoodStrategy)


def test_choose_strategy_avoid_food_strategy(sample_snake):
    snake = clone(sample_snake, health=41, body=sample_snake["body"] * 4)
    result = choose_strategy(TurnContext(0, 0, 0, [], snake, [snake], []))
    assert isinstance(result, AvoidFoodStrategy)


def test_corner_strategy(sample_snake, directions):
    strategy = CornerStrategy(
        TurnContext(0, 0, 0, [], sample_snake, [sample_snake], [])
    )
    direction = strategy.get_action()
    assert isinstance(direction, str)
    assert direction in directions


def test_prefer_food_strategy(sample_snake, directions):
    snake = clone(sample_snake, health=40)
    strategy = PreferFoodStrategy(TurnContext(0, 0, 0, [], snake, [snake], []))
    direction = strategy.get_action()
    assert isinstance(direction, str)
    assert direction in directions


def test_avoid_food_strategy(sample_snake, directions):
    snake = clone(sample_snake, health=41, body=sample_snake["body"] * 4)
    strategy = AvoidFoodStrategy(TurnContext(0, 0, 0, [], snake, [snake], []))
    direction = strategy.get_action()
    assert isinstance(direction, str)
    assert direction in directions
