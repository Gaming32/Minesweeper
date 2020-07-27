import configparser
from math import ceil
import os
import math

import pygame

from minesweeper import EMPTY_SLOT, FLAG_SLOT, Minesweeper, MINE_BIT


FILE_ROOT = os.path.dirname(__file__)


def get_file(fname):
    if os.path.exists(fname):
        return fname
    else:
        return os.path.join(FILE_ROOT, fname)


def load_config():
    config = configparser.ConfigParser()
    config.read(get_file('msgui.ini'))
    return config


def hex_to_color(s):
    if len(s) < 3:
        s = s * 6
    elif len(s) < 6:
        s = s[0] * 2 + s[1] * 2 + s[2] * 2
    number = int(s, 16)
    r = number >> 16
    number -= r << 16
    g = number >> 8
    number -= g << 8
    b = number
    return r, g, b


def image_color_not_dead(item, colors, font, flag_image, cell_size, cell_border):
    if item == EMPTY_SLOT:
        color = colors['normal']
        image = None
    elif item == FLAG_SLOT:
        color = colors['selected']
        image = flag_image
    elif item == 0:
        color = colors['selected']
        image = None
    else:
        color = colors['selected']
        text = str(item)
        text_size = font.size(text)
        actual_size = cell_size - cell_border * 2
        image = pygame.Surface((actual_size, actual_size))
        image.fill(color)
        image.blit(font.render(text, True, colors['number']), pygame.Rect(
            (
                actual_size / 2 - text_size[0] / 2,
                actual_size / 2 - text_size[1] / 2,
            ),
            text_size,
        ))

    return color, image


def render(surface, render_matrix, board_matrix, cell_size, cell_border, flag_image, bomb_image, colors, font, state):
    for (ri, row) in enumerate(render_matrix):
        for (ci, item) in enumerate(row):

            location = pygame.Rect(
                ci * cell_size + cell_border,
                ri * cell_size + cell_border,
                cell_size - cell_border * 2,
                cell_size - cell_border * 2,
            )

            if state != 1:
                color, image = image_color_not_dead(item, colors, font, flag_image, cell_size, cell_border)
            else:
                internal_item = board_matrix[ri, ci]
                if internal_item & MINE_BIT:
                    color = colors['bomb']
                    image = bomb_image
                else:
                    color, image = image_color_not_dead(item, colors, font, flag_image, cell_size, cell_border)
                
            surface.fill(color, location)
            if image is not None:
                surface.blit(image, location)


def main():
    config = load_config()
    board_width = config.getint('board', 'width')
    board_height = config.getint('board', 'height')
    bomb_count = config.getint('board', 'bombs')
    cell_size = config.getint('view', 'cell-size')
    cell_border = config.getint('view', 'cell-border')
    zoom_size = config.getint('zoom', 'size')
    zoom_scale = config.getint('zoom', 'scale')
    zoomed_cell_size = cell_size * zoom_scale
    colors = {name: hex_to_color(value) for (name, value) in config['colors'].items()}
    rawfontname = config.get('view', 'font')
    fontname = get_file(rawfontname)
    fontsize = config.getint('view', 'font-size')

    pygame.init()
    render_size = (board_width * cell_size, board_height * cell_size)
    render_surface = pygame.Surface(render_size)
    screen = pygame.display.set_mode((render_size[0], render_size[1] + cell_size))

    if os.path.exists(fontname):
        font = pygame.font.Font(fontname, fontsize)
        zoom_font = pygame.font.Font(fontname, fontsize * zoom_scale)
    else:
        font = pygame.font.SysFont(rawfontname, fontsize)
        zoom_font = pygame.font.SysFont(rawfontname, fontsize * zoom_scale)

    board = Minesweeper(board_height, board_width, bomb_count)

    real_cell_size = cell_size - cell_border

    filename = get_file(config.get('images', 'bomb'))
    bomb_image = pygame.image.load(filename).convert_alpha()
    scaled_bomb_image = pygame.transform.scale(bomb_image, (real_cell_size, real_cell_size))
    bomb_image = pygame.transform.scale(bomb_image, (zoom_size, zoom_size))

    filename = get_file(config.get('images', 'flag'))
    flag_image = pygame.image.load(filename).convert_alpha()
    scaled_flag_image = pygame.transform.scale(flag_image, (real_cell_size, real_cell_size))
    flag_image = pygame.transform.scale(flag_image, (zoom_size, zoom_size))

    filename = get_file(config.get('images', 'faces'))
    faces_image = pygame.image.load(filename).convert_alpha()
    faces_image = pygame.transform.scale(faces_image, (cell_size, cell_size * 5))
    faces = []
    for y in range(0, faces_image.get_size()[1], cell_size):
        faces.append(pygame.Surface((cell_size, cell_size)))
        faces[-1].blit(faces_image, (0, 0), (0, y, cell_size, cell_size))
    del faces_image
    face = 4

    # from msterm import render as render_term
    # render_term(board)

    zoom_size_diff = zoom_size - zoomed_cell_size
    zoom = zoom_size_diff > 0
    zoom_cell_size = zoom_size // zoom_scale

    state = 0

    clock = pygame.time.Clock()
    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
                board = Minesweeper(board_height, board_width, bomb_count)
                state = 0
                face = 4
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[1] < cell_size:
                    if event.button == 1:
                        if event.pos[0] < cell_size:
                            face = 0
                elif state == 1:
                    face = 2
                elif state == 2:
                    face = 1
                else:
                    face = 3
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.pos[1] < cell_size:
                    if event.button == 1:
                        if event.pos[0] < cell_size:
                            board = Minesweeper(board_height, board_width, bomb_count)
                            state = 0
                            face = 4
                elif not state:
                    face = 4
                    cell = (event.pos[1] // cell_size - 1, event.pos[0] // cell_size)
                    print('you', event.button, 'clicked', cell)
                    if event.button == 1:
                        count = board.recursive_reveal(*cell)
                        if count == -1:
                            print('Game Over!')
                            state = 1
                            face = 2
                    elif event.button == 3:
                        board.toggle_flag(*cell)
                        if board.has_won():
                            print('You Won!')
                            state = 2
                            face = 1
                            board.reveal_all()

        screen.fill(colors['clear'])

        screen.blit(faces[face], (0, 0))
        render(
            render_surface,
            board.render_matrix,
            board.board_matrix,
            cell_size,
            cell_border,
            scaled_flag_image,
            scaled_bomb_image,
            colors,
            font,
            state,
        )
        screen.blit(render_surface, (0, cell_size))

        if not state and zoom:
            try:
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[1] >= zoomed_cell_size:
                    location = (mouse_pos[0] - zoomed_cell_size // 2, mouse_pos[1] - zoomed_cell_size // 2)
                    edge_location = (location[0] + zoom_size // 2, location[1] + zoom_size // 2)
                    if location >= (0, 0) and edge_location <= screen.get_size():
                        cell = (mouse_pos[1] // cell_size - 1, mouse_pos[0] // cell_size)
                        zoom_rect = (
                            math.floor(cell[0] - zoom_scale / 2),
                            math.floor(cell[1] - zoom_scale / 2),
                            math.ceil(cell[0] + zoom_scale / 2),
                            math.ceil(cell[1] + zoom_scale / 2),
                        )
                        zoomed_cells = board.render_matrix[
                            zoom_rect[0] : zoom_rect[2] + 1,
                            zoom_rect[1] : zoom_rect[3] + 1
                        ]
                        zoomed_board_cells = board.board_matrix[
                            zoom_rect[0] : zoom_rect[2] + 1,
                            zoom_rect[1] : zoom_rect[3] + 1
                        ]
                        # print(zoomed_cells)
                        # surface = screen.copy().subsurface(pygame.Rect(location, (zoomed_cell_size, zoomed_cell_size)))
                        zoom_scale_diff = (zoom_size // zoom_scale // cell_size)
                        surface = pygame.Surface((render_size[0] * zoom_scale_diff, render_size[1] * zoom_scale_diff))
                        render(
                            surface,
                            board.render_matrix,
                            board.board_matrix,
                            zoom_cell_size,
                            cell_border * zoom_scale,
                            flag_image,
                            bomb_image,
                            colors,
                            zoom_font,
                            state,
                        )
                        draw_location = (location[0] - zoom_size // 4, location[1] - zoom_size // 4)
                        zoom_offset = zoom_scale * cell_size
                        # print((
                        #     mouse_pos[0] * zoom_scale,
                        #     mouse_pos[1] * zoom_scale,
                        #     zoom_size,
                        #     zoom_size,
                        # ), '           ', end='\r')
                        # print(len(zoomed_cells), '        ', end='\r')
                        screen.blit(surface, draw_location, (
                            mouse_pos[0] * zoom_scale_diff - zoom_offset,
                            mouse_pos[1] * zoom_scale_diff - 2 * zoom_offset,
                            zoom_size,
                            zoom_size,
                        ))
            except Exception:
                raise
        pygame.display.update()


if __name__ == '__main__':
    main()
