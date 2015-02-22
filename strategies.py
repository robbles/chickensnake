from flask import current_app as app, url_for
import random
import data
import log


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
        self.snakes = [
            s for s in snakes if s['coords'][0] != self.position
        ]
        self.food = food

    def log(self, msg, *args):
        name = self.__class__.__name__
        app.logger.debug(name + ': ' + msg, *args)

    def get_action(self):
        """ return (direction, taunt | None) """
        return data.UP, None

    def safe_directions(self, allowed_tiles=[data.EMPTY, data.FOOD]):
        good = []
        for d in data.DIRECTIONS:
            safe, contents = self.check_square(d, allowed_tiles)
            if safe:
                good.append((d, contents))

        return good

    def check_square(self, direction, allowed_tiles=[data.EMPTY, data.FOOD]):
        pos = self.position
        x = pos[0]
        y = pos[1]
        ncols, nrows = data.dimensions(self.board)

        if direction == data.UP:
            y -= 1
        elif direction == data.DOWN:
            y += 1
        elif direction == data.LEFT:
            x -= 1
        else:
            x += 1

        safe, contents = True, data.EMPTY

        # check the boundaries
        if (x >= ncols or x < 0) or (y >= nrows or y < 0):
            # out of boundaries
            return False, data.BOUNDARY

        # check for invalid tile according to allowed_tiles
        tile = self.board[x][y]
        contents = tile['state']

        if contents not in allowed_tiles:
            safe = False

        for other_snake in self.snakes:
            other_snake_pos = other_snake['coords'][0]
            if data.adjacent(other_snake_pos, (x, y)):
                safe = False
                contents = data.COLLISION
                self.log('Avoiding collision!')

        self.log('%s, contains %s',
            log.green('safe') if safe else log.red('unsafe'), contents)

        return safe, contents



class RandomStrategy(BaseStrategy):
    def get_action(self):
        safe = self.safe_directions()

        if not safe:
            # we're fucked
            return data.UP, 'goodbye, cruel world'

        direction, contents = random.choice(safe)
        self.log('choosing %s randomly', direction)

        return direction, 'mmmmm' if contents == data.FOOD else None
