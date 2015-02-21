#!/usr/bin/env python

from flask import Flask, g, request, jsonify

import strategies
import data
import log

SNAKE_NAME = 'Sample Snake'

app = Flask(__name__)
app.logger.handlers[0].setFormatter(log.LogFormatter())

@app.before_request
def debug_request():
    g.data = request.get_json(force=True)

@app.after_request
def debug_response(response):
    app.logger.debug('\nRESPONSE: %s', response.data)
    return response


@app.route('/')
def index():
    return "nothing to see here, move along"


@app.route('/start', methods=['POST'])
def start():
    app.logger.debug('\nSTART: %s', g.data)

    return jsonify({
        'name': SNAKE_NAME,
        'color': '#ffffff',
        'head_url': 'https://www.pretio.in/static/img/favicon.ico',
        'taunt': 'buk buk buk buk'
    })


@app.route('/move', methods=['POST'])
def move():
    name = 'Sample Snake'
    turn, board, snakes, food = g.data['turn'], g.data['board'], g.data['snakes'], g.data['food']
    width, height = data.dimensions(board)

    app.logger.debug('\nTURN: %s\nBOARD: %dX%d\nSNAKES: %s\nFOOD: %s\n',
        turn, width, height, snakes, food)

    strategy = strategies.choose_strategy(name, turn, board, snakes, food)
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
    app.run(debug=True)
