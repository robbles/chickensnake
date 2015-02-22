from flask import current_app as app, url_for
import random
import data


def choose_strategy(turn, board, snakes, food):
    me = get_snake(snakes)
    head = me['coords'][0]
    health = 100 - (turn - me.get('last_eaten', 0))

    app.logger.debug('Snake: %s', me)
    app.logger.debug('Current head position: %s', head)
    app.logger.debug('Health: %d', health)

    return RandomStrategy(turn, head, health, board, snakes, food)

def get_snake(snakes):
    url = url_for('base', _external=True).rstrip('/')
    app.logger.debug('Snake URL should be %s', url)

    for snake in snakes:
        if snake['url'].rstrip('/') == url:
            return snake


class BaseStrategy(object):
    def __init__(self, turn, position, health, board, snakes, food):
        self.turn = turn
        self.position = position
        self.health = health
        self.board = board
        self.snakes = snakes
        self.food = food

    def log(self, msg, *args):
        name = self.__class__.__name__
        app.logger.debug(name + ': ' + msg, *args)

    def get_action(self):
        """ return (direction, taunt | None) """
        return data.UP, None


class RandomStrategy(BaseStrategy):
    def get_action(self):
        safe = data.safe_directions(self.board, self.position)

        if not safe:
            # we're fucked
            return data.UP, 'goodbye, cruel world'

        direction, contents = random.choice(safe)
        self.log('choosing %s randomly', direction)

        return direction, 'mmmmm' if contents == data.FOOD else None
