from collections import namedtuple

from six.moves import range
from mittmcts import Draw


bitboard_lookup = [
    [5, 12, 19, 26, 33, 40, 47],
    [4, 11, 18, 25, 32, 39, 46],
    [3, 10, 17, 24, 31, 38, 45],
    [2, 9, 16, 23, 30, 37, 44],
    [1, 8, 15, 22, 29, 36, 43],
    [0, 7, 14, 21, 28, 35, 42],
]


def empty_board():
    return [[None] * 7 for _ in range(6)]


def check_win(bitboard):
    # https://github.com/tonyho/ARM_BenchMark/blob/master/fhourstones/Game.c
    HEIGHT = 6
    H1 = HEIGHT + 1
    H2 = HEIGHT + 2
    diag1 = bitboard & (bitboard >> HEIGHT)
    hori = bitboard & (bitboard >> H1)
    diag2 = bitboard & (bitboard >> H2)
    vert = bitboard & (bitboard >> 1)
    return ((diag1 & (diag1 >> 2 * HEIGHT)) |
            (hori & (hori >> 2 * H1)) |
            (diag2 & (diag2 >> 2 * H2)) |
            (vert & (vert >> 2)))


def check_top_row(board):
    return [column for column, piece
            in enumerate(board[0])
            if piece is None]


def get_bitboards(board):
    bitboards = [0, 0]
    for player in range(2):
        for row in range(5, -1, -1):
            for column in range(7):
                if board[row][column] == player:
                    bitboards[player] ^= 1 << bitboard_lookup[row][column]
    return bitboards


def find_row_for_column(board, column):
    for row, pieces in enumerate(reversed(board)):
        if pieces[column] is None:
            return 5 - row
    raise Exception('No empty spot in that column')


class ConnectFourGame(object):
    """A simple connection game"""
    State = namedtuple('ConnectFourState',
                       ['board',
                        'bitboards',
                        'winner',
                        'current_player'])

    @classmethod
    def initial_state(cls):
        return cls.State(board=empty_board(),
                         bitboards=[0, 0],
                         winner=None,
                         current_player=0)

    @classmethod
    def apply_move(cls, state, column):
        bitboards = state.bitboards[:]
        board = [row[:] for row in state.board]
        winner = None

        row = find_row_for_column(board, column)

        board[row][column] = state.current_player
        bitboards[state.current_player] ^= 1 << bitboard_lookup[row][column]

        for player, bitboard in enumerate(bitboards):
            if check_win(bitboard):
                winner = player

        if not check_top_row(board) and not winner:
            winner = Draw

        current_player = (state.current_player + 1) % 2

        return cls.State(board=board,
                         bitboards=bitboards,
                         winner=winner,
                         current_player=current_player)

    @staticmethod
    def get_moves(state):
        return False, check_top_row(state.board)

    @staticmethod
    def get_winner(state):
        return state.winner

    @staticmethod
    def current_player(state):
        return state.current_player
