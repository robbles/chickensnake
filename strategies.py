from flask import current_app as app
import random
import data
import log


def choose_strategy(name, turn, board, snakes, food):
    return RandomStrategy(name, turn, board, snakes, food)


class BaseStrategy(object):
    def __init__(self, name, turn, board, snakes, food):
        self.name = name
        self.turn = turn
        self.board = board
        self.snakes = snakes
        self.food = food

        self.me = data.get_snake(snakes, name)
        self.head = self.me['coords'][0]
        self.health = 100 - (turn - self.me.get('last_eaten', 0))

        self.log('Snake: %s', self.me)
        self.log('Current head position: %s', self.head)
        self.log('Health: %d', self.health)

    def log(self, msg, *args):
        name = self.__class__.__name__
        app.logger.debug(name + ': ' + msg, *args)

    def get_action(self):
        """ return (direction, taunt | None) """
        return data.UP, None


class RandomStrategy(BaseStrategy):
    def get_action(self):
        safe = data.safe_directions(self.board, self.head)

        if not safe:
            # we're fucked
            return data.UP, 'goodbye, cruel world'

        direction, contents = random.choice(safe)
        self.log('choosing %s randomly', direction)

        return direction, 'mmmmm' if contents == data.FOOD else None
