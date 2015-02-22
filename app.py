#!/usr/bin/env python

from flask import Flask, g, request, jsonify, url_for
import os
import random

import strategies
import data
import log

SNAKE_NAME = os.getenv('SNAKE_NAME', 'Sample Snake ' + str(random.random()))
SNAKE_HEAD = 'chicken.jpg'

app = Flask(__name__)
app.logger.handlers[0].setFormatter(log.LogFormatter())

@app.after_request
def debug_response(response):
    if response.content_type == 'application/json':
        app.logger.debug('\nRESPONSE: %s', response.data)
    return response


@app.route('/')
def base():
    return "nothing to see here, move along"


@app.route('/start', methods=['POST'])
def start():
    g.data = request.get_json(force=True)
    app.logger.debug('\nSTART: %s', g.data)

    return jsonify({
        'name': SNAKE_NAME,
        'color': '#ffffff',
        'head_url': url_for('static', filename=SNAKE_HEAD, _external=True),
        'taunt': 'buk buk buk buk'
    })


@app.route('/move', methods=['POST'])
def move():
    g.data = request.get_json(force=True)
    turn, board, snakes, food = g.data['turn'], g.data['board'], g.data['snakes'], g.data['food']
    width, height = data.dimensions(board)

    app.logger.debug('\nTURN: %s\nBOARD: %dX%d\nSNAKES: %s\nFOOD: %s\n',
        turn, width, height, snakes, food)

    strategy = strategies.choose_strategy(turn, board, snakes, food)
    direction, taunt = strategy.get_action()

    # move, taunt
    return jsonify({
        'move': direction,
        'taunt': taunt,
    })


@app.route('/end', methods=['POST'])
def end():
    return jsonify({})


if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv('PORT', 5000)))
