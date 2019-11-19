import pytest

from app import app
import data


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def turn_data():
    return {
        "game": {"id": "game-id-string"},
        "turn": 4,
        "board": {
            "height": 15,
            "width": 15,
            "food": [{"x": 1, "y": 3}],
            "snakes": [
                {
                    "id": "snake-id-string",
                    "name": "Sneky Snek",
                    "health": 90,
                    "body": [{"x": 1, "y": 3}],
                }
            ],
        },
        "you": {
            "id": "snake-id-string",
            "name": "Sneky Snek",
            "health": 90,
            "body": [{"x": 1, "y": 3}],
        },
    }


def test_start(client, turn_data):
    res = client.post("/start", json=turn_data,)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/json"
    json_data = res.get_json()
    assert json_data["color"]
    assert json_data["headType"]
    assert json_data["tailType"]


def test_end(client, turn_data):
    res = client.post("/end", json=turn_data,)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/json"


def test_move(client, turn_data):
    res = client.post("/move", json=turn_data,)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/json"
    json_data = res.get_json()
    assert json_data["move"] in [data.UP, data.DOWN, data.LEFT, data.RIGHT]
