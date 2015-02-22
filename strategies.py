from flask import current_app as app
import random
import data
import log
import taunts


def choose_strategy(turn, board, snakes, food):
    me = data.get_snake(snakes)
    head = me['coords'][0]
    health = 100 - (turn - me.get('last_eaten', 0))

    app.logger.debug('Snake: %s', me)
    app.logger.debug('Current head position: %s', head)
    app.logger.debug('Health: %d', health)

    if health > 40 and me.get('food_eaten', 0) == 0:
        # stay in the corner if we have food and haven't eaten
        strategy = CornerStrategy
    else:
        if health > 40:
            # don't collect food unless you absolutely have to
            strategy = AvoidFoodStrategy
        else:
            # prefer food when low on health
            strategy = PreferFoodStrategy

    return strategy(turn, head, health, board, snakes, food)


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

    def get_taunt(self):
        for snake in self.snakes:
            pos = snake['coords'][0]
            if pos == self.position:
                continue
            taunt = snake['taunt']
            if taunt in taunts.TAUNTS:
                return taunts.TAUNTS[taunt]

        if random.randint(0, 15) == 0:
            return random.choice(taunts.TAUNTS.keys())

        return None


class RandomStrategy(BaseStrategy):
    def get_action(self):
        safe = self.safe_directions()

        if not safe:
            # we're fucked
            return data.UP, 'goodbye, cruel world'

        direction, contents = random.choice(safe)
        self.log('choosing %s randomly', direction)

        return direction


class PreferFoodStrategy(BaseStrategy):
    def get_action(self):
        safe = self.safe_directions()

        if not safe:
            return data.UP, 'goodbye, cruel world'

        for direction, contents in safe:
            if contents == data.FOOD:
                return direction

        direction, contents = random.choice(safe)

        return direction


class AvoidFoodStrategy(BaseStrategy):
    def get_action(self):
        safe = self.safe_directions()

        if not safe:
            return data.UP, 'goodbye, cruel world'

        random.shuffle(safe)

        for direction, contents in safe:
            if contents != data.FOOD:
                return direction

        # only food??
        direction, contents = random.choice(safe)

        return direction


class CornerStrategy(BaseStrategy):
    def get_action(self):
        safe = self.safe_directions()
        safe_dirs = [direction for direction, contents in safe]

        if not safe:
            return data.UP, 'goodbye, cruel world'

        ncols, nrows = data.dimensions(self.board)
        corners = (
            (0, 0), (ncols - 1, 0), (0, nrows - 1), (ncols - 1, nrows - 1)
        )

        closest_corner = sorted(corners, key=lambda corner:
            data.manhattan_dist(self.position, corner)
        )[0]

        x, y = self.position
        cx, cy = closest_corner

        if data.adjacent(self.position, closest_corner):
            self.log('ADJACENT TO CORNER: %s', safe_dirs)

            # stay in corner, gross logic
            if closest_corner == corners[0]:
                if x > cx and data.DOWN in safe_dirs:
                    return data.DOWN
                if y > cy and data.RIGHT in safe_dirs:
                    return data.RIGHT
            if closest_corner == corners[1]:
                if x < cx and data.DOWN in safe_dirs:
                    return data.DOWN
                if y > cy and data.LEFT in safe_dirs:
                    return data.LEFT
            if closest_corner == corners[2]:
                if x > cx and data.UP in safe_dirs:
                    return data.UP
                if y < cy and data.RIGHT in safe_dirs:
                    return data.RIGHT
            if closest_corner == corners[3]:
                if x < cx and data.UP in safe_dirs:
                    return data.UP
                if y < cy and data.LEFT in safe_dirs:
                    return data.LEFT

        # move towards corner
        for direction, contents in safe:
            if direction == data.LEFT and cx < x:
                return direction
            if direction == data.RIGHT and cx > x:
                return direction
            if direction == data.UP and cy < y:
                return direction
            if direction == data.DOWN and cy > y:
                return direction

        # no idea, fuck it
        self.log('MOVING RANDOMLY')
        direction, contents = random.choice(safe)

        return direction
