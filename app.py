#!/usr/bin/env python

from flask import Flask, request, jsonify
import os

import strategies
import data
import logs

HEAD_TYPE = os.getenv("HEAD_TYPE", "safe")
TAIL_TYPE = os.getenv("TAIL_TYPE", "hook")

app = Flask(__name__)
app.logger.handlers[0].setFormatter(logs.LogFormatter())


@app.after_request
def debug_response(response):
    if response.content_type == "application/json":
        app.logger.debug("\nRESPONSE: %s", response.data)
    return response


@app.route("/")
def base():
    return "nothing to see here, move along"


@app.route("/start", methods=["POST"])
def start():
    request_data = request.get_json(force=True)
    app.logger.debug("\nSTART: %s", request_data)

    return jsonify({"color": "#ffffff", "headType": HEAD_TYPE, "tailType": TAIL_TYPE,})


@app.route("/move", methods=["POST"])
def move():
    request_data = request.get_json(force=True)
    turn_context = data.build_turn_context(request_data)

    app.logger.debug(
        "\nTURN: %s\nBOARD: %dX%d\nSNAKES: %s\nFOOD: %s\n",
        turn_context.turn,
        turn_context.width,
        turn_context.height,
        turn_context.snakes,
        turn_context.foods,
    )

    strategy = strategies.choose_strategy(turn_context)
    direction = strategy.get_action()

    # move, taunt
    return jsonify({"move": direction,})


@app.route("/end", methods=["POST"])
def end():
    return jsonify({})


if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))
