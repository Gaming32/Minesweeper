import numpy
import random
import math


MINE_BIT = 0b01
FLAG_BIT = 0b10

EMPTY_SLOT = 0xFF
FLAG_SLOT = 0xFE


class Minesweeper:
    def __init__(self, *shape, seed=None):
        if len(shape) < 1:
            shape = (10, 10)
            bomb_count = 7
        else:
            shape, bomb_count = shape[:-1], shape[-1]
        if math.prod(shape) < bomb_count:
            raise ValueError('cannot be more bombs than spaces on the board')
        self.board_matrix = numpy.zeros(shape, 'int16')
        self.render_matrix = numpy.ones(shape, 'int8') * EMPTY_SLOT
        randomizer = random.Random(seed)
        bombs = []
        while bomb_count:
            bomb = []
            for size in shape:
                bomb.append(randomizer.randrange(size))
            bomb = tuple(bomb)
            if bomb not in bombs:
                bombs.append(bomb)
                self.board_matrix[bomb] |= MINE_BIT
                bomb_count -= 1
