from minesweeper import Minesweeper, EMPTY_SLOT, FLAG_SLOT
import pygame


def main():
    pygame.init()
    display = pygame.display.set_mode((640, 640))
    board = Minesweeper()


if __name__ == '__main__':
    main()
