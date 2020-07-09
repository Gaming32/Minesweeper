from minesweeper import EMPTY_SLOT, FLAG_BIT, FLAG_SLOT, MINE_BIT, Minesweeper


def render(board):
    value = '   ' + ''.join(' ' + str(v) + ' ' for v in range(board.render_matrix.shape[0])) + '\n'
    for (ri, row) in enumerate(board.board_matrix):
        value += chr(65 + ri) + ' ['
        for item in row:
            value += ' '
            if item & MINE_BIT:
                value += '!'
            elif item & FLAG_BIT:
                value += 'P'
            # if item == EMPTY_SLOT:
            #     value += ' '
            # elif item == FLAG_SLOT:
            #     value += 'P'
            else:
                value += str(item)
            value += ' '
        value += ']\n'
    print(value, end='')


def main():
    board = Minesweeper()
    render(board)


if __name__ == '__main__':
    main()
