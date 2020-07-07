from minesweeper import Minesweeper, EMPTY_SLOT, FLAG_SLOT
import pygame


def main():
    pygame.init()
    display = pygame.display.set_mode((640, 640))
    board = Minesweeper()
    bomb_image = pygame.image.load('bomb.png').convert_alpha()
    flag_image = pygame.image.load('flag.png').convert_alpha()
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        pygame.display.update()


if __name__ == '__main__':
    main()
