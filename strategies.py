import os
import random
import logging

import data
import logs

OPTIONS = {
    "FORCE_STRATEGY": os.getenv("FORCE_STRATEGY", False),
}

logger = logging.getLogger(__name__)


def choose_strategy(turn_context: data.TurnContext, options=OPTIONS):
    logger.debug("Snake: %s", turn_context.my_snake)
    logger.debug("Current head position: %s", turn_context.position)
    logger.debug("Health: %d", turn_context.health)

    if options["FORCE_STRATEGY"]:
        force_strategy = options["FORCE_STRATEGY"]
        strategy = {
            "RANDOM": RandomStrategy,
            "FOOD": PreferFoodStrategy,
            "NOFOOD": AvoidFoodStrategy,
        }.get(force_strategy, RandomStrategy)

    elif turn_context.health > 40 and not data.has_eaten(turn_context.my_snake):
        # stay in the corner if we have food and haven't eaten
        strategy = CornerStrategy
    else:
        if turn_context.health > 40:
            # don't collect food unless you absolutely have to
            strategy = AvoidFoodStrategy
        else:
            # prefer food when low on health
            strategy = PreferFoodStrategy

    return strategy(turn_context)


class BaseStrategy(object):
    def __init__(self, turn_context):
        self.ctx = turn_context

    def log(self, msg, *args):
        name = self.__class__.__name__
        logger.debug(name + ": " + msg, *args)

    def get_action(self) -> str:
        return data.UP

    def safe_directions(self, allowed_tiles=[data.EMPTY, data.FOOD]):
        good = []
        for d in data.DIRECTIONS:
            safe, contents = self.check_square(d, allowed_tiles)
            if safe:
                good.append((d, contents))

        return good

    def check_square(self, direction, allowed_tiles=[data.EMPTY, data.FOOD]):
        x, y = self.ctx.position
        ncols, nrows = self.ctx.width, self.ctx.height

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
        contents = self.ctx.grid[x][y]

        if contents not in allowed_tiles:
            safe = False

        for other_snake in self.ctx.snakes:
            other_snake_head = other_snake[0]
            if data.adjacent(other_snake_head, (x, y)):
                safe = False
                contents = data.COLLISION
                self.log("Avoiding collision!")

        self.log(
            "%s, contains %s",
            logs.green("safe") if safe else logs.red("unsafe"),
            contents,
        )

        return safe, contents


class RandomStrategy(BaseStrategy):
    def get_action(self):
        safe = self.safe_directions()

        if not safe:
            return data.UP

        direction, contents = random.choice(safe)
        self.log("choosing %s randomly", direction)

        return direction


class PreferFoodStrategy(BaseStrategy):
    def get_action(self):
        safe = self.safe_directions()

        if not safe:
            return data.UP

        for direction, contents in safe:
            if contents == data.FOOD:
                return direction

        direction, contents = random.choice(safe)

        return direction


class AvoidFoodStrategy(BaseStrategy):
    def get_action(self):
        safe = self.safe_directions()

        if not safe:
            return data.UP

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
            return data.UP

        ncols, nrows = self.ctx.width, self.ctx.height

        corners = ((0, 0), (ncols - 1, 0), (0, nrows - 1), (ncols - 1, nrows - 1))

        closest_corner = sorted(
            corners, key=lambda corner: data.manhattan_dist(self.ctx.position, corner)
        )[0]

        position = self.ctx.position
        x, y = position
        cx, cy = closest_corner

        if data.adjacent(position, closest_corner):
            self.log("ADJACENT TO CORNER: %s", safe_dirs)

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
        self.log("MOVING RANDOMLY")
        direction, contents = random.choice(safe)

        return direction
