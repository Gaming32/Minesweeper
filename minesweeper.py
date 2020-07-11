import math
import random

import numpy as np

MINE_BIT = 0b01
FLAG_BIT = 0b10

EMPTY_SLOT = 0xFF
FLAG_SLOT = 0xFE

SURROUNDING = [
    (1, 0),
    (1, 1),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (-1, -1),
    (0, -1),
    (1, -1),
]


class Minesweeper:
    def __init__(self, *shape, seed=None):
        if len(shape) < 1:
            shape = (10, 10)
            bomb_count = 7
        else:
            shape, bomb_count = shape[:-1], shape[-1]
        if math.prod(shape) < bomb_count:
            raise ValueError('cannot be more bombs than spaces on the board')
        self.board_matrix = np.zeros(shape, 'uint16')
        self.render_matrix = np.full(shape, EMPTY_SLOT, 'uint8')
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

    def add_flag(self, *pos):
        self.board_matrix[pos] |= FLAG_BIT
        self.render_matrix[pos] = FLAG_SLOT

    def remove_flag(self, *pos):
        self.board_matrix[pos] ^= FLAG_BIT
        self.render_matrix[pos] = EMPTY_SLOT

    def is_flagged(self, *pos):
        return FLAG_BIT & self.board_matrix[pos]

    def toggle_flag(self, *pos):
        if self.is_flagged(*pos):
            self.remove_flag(*pos)
        else:
            self.add_flag(*pos)

    def _reveal(self, pos):
        cell = self.board_matrix[pos]
        if cell & FLAG_BIT:
            return -2
        elif cell & MINE_BIT:
            return -1
        else:
            count = 0
            shape = self.board_matrix.shape
            for direction in SURROUNDING:
                # newpos = (pos[0] + direction[0], pos[1] + direction[1])
                newpos = tuple(map(sum, ((pos[x], direction[x]) for x in range(len(direction)))))
                if all(map((lambda x: x[1] >= 0 and x[1] < shape[x[0]]), enumerate(newpos))):
                    count += self.board_matrix[newpos] & MINE_BIT
            return count

    def reveal(self, *pos):
        count = self._reveal(pos)
        if count >= 0:
            self.render_matrix[pos] = count
        return count

    def recursive_reveal(self, *pos):
        reached = set()
        to_search = {pos}
        retcount = None
        shape = self.board_matrix.shape
        while to_search:
            for subpos in to_search.copy():
                to_search.remove(subpos)
                if subpos in reached:
                    continue
                reached.add(subpos)
                count = self.reveal(*subpos)
                retcount = count if retcount is None else retcount
                if count == 0:
                    for direction in SURROUNDING:
                        # newpos = (pos[0] + direction[0], pos[1] + direction[1])
                        newpos = tuple(map(sum, ((subpos[x], direction[x]) for x in range(len(direction)))))
                        if newpos not in reached \
                                and all(map((lambda x: x[1] >= 0 and x[1] < shape[x[0]]), enumerate(newpos))):
                            to_search.add(newpos)
        return retcount

    def has_won(self):
        return all((bool(cell & FLAG_BIT) == bool(cell & MINE_BIT)) for cell in np.nditer(self.board_matrix))

    def reveal_all(self):
        for (pos, cell) in np.ndenumerate(self.board_matrix):
            if not cell & FLAG_BIT and not cell & MINE_BIT:
                self.reveal(*pos)
