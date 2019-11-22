#!/usr/bin/env python

from flask import Flask, request, jsonify
import os

import strategies
import data
import logs
import logging

HEAD_TYPE = os.getenv("HEAD_TYPE", "safe")
TAIL_TYPE = os.getenv("TAIL_TYPE", "hook")
COLOR = os.getenv("COLOR", "#A0522D")

app = Flask(__name__)
app.logger.handlers[0].setFormatter(logs.LogFormatter())
app.logger.setLevel(os.getenv("LOG_LEVEL", logging.DEBUG))


@app.after_request
def debug_response(response):
    if response.content_type == "application/json":
        app.logger.debug("RESPONSE: %s", response.get_json())
    return response


@app.route("/")
def base():
    return "nothing to see here, move along"


@app.route("/start", methods=["POST"])
def start():
    request_data = request.get_json(force=True)
    app.logger.debug("START: %s", request_data)

    return jsonify({"color": COLOR, "headType": HEAD_TYPE, "tailType": TAIL_TYPE,})


@app.route("/move", methods=["POST"])
def move():
    request_data = request.get_json(force=True)
    app.logger.debug("MOVE: %s", request_data)
    turn_context = data.build_turn_context(request_data)

    app.logger.debug(f"turn = {turn_context.turn}")
    app.logger.debug(f"width = {turn_context.width}")
    app.logger.debug(f"height = {turn_context.height}")
    app.logger.debug(f"snakes = {turn_context.snakes}")
    app.logger.debug(f"foods = {turn_context.foods}")
    app.logger.debug(f"position = {turn_context.position}")

    strategy = strategies.choose_strategy(turn_context)
    direction = strategy.get_action()

    return jsonify({"move": direction,})


@app.route("/end", methods=["POST"])
def end():
    return jsonify({})


if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", 8000)))
