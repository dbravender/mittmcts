import unittest

from mittmcts import MCTS

from test.connect4 import (
    get_bitboards, find_row_for_column, empty_board, ConnectFourGame
)


class TestConnectFour(unittest.TestCase):
    def test_empty_board(self):
        _ = None
        self.assertEqual(empty_board(),
                         [[_, _, _, _, _, _, _],
                          [_, _, _, _, _, _, _],
                          [_, _, _, _, _, _, _],
                          [_, _, _, _, _, _, _],
                          [_, _, _, _, _, _, _],
                          [_, _, _, _, _, _, _]])

    def test_find_row_for_column(self):
        _ = None
        board = [[0, 0, _, _, _, 1, 1],
                 [1, 0, _, _, _, 0, 0],
                 [0, 1, 0, _, _, 1, 1],
                 [1, 0, 1, _, _, 0, 0],
                 [0, 1, 0, _, _, 1, 1],
                 [1, 0, 1, _, 1, 0, 0]]
        self.assertEqual(find_row_for_column(board, 2), 1)
        with self.assertRaises(Exception):
            find_row_for_column(board, 0)
        self.assertEqual(find_row_for_column(board, 3), 5)
        self.assertEqual(find_row_for_column(board, 4), 4)
        with self.assertRaises(Exception):
            find_row_for_column(board, 5)

    def test_apply_move(self):
        _ = None
        board = [[_, _, _, _, _, _, _],
                 [_, _, _, _, _, _, _],
                 [_, _, _, _, _, _, _],
                 [_, _, _, _, _, _, _],
                 [_, _, _, _, _, _, _],
                 [_, _, _, _, 0, 0, 0]]
        initial_state = ConnectFourGame.initial_state()
        initial_state = initial_state._replace(board=board,
                                               bitboards=get_bitboards(board))
        state = ConnectFourGame.apply_move(initial_state, 6)
        self.assertIsNone(state.winner)
        self.assertEqual(state.board,
                         [[_, _, _, _, _, _, _],
                          [_, _, _, _, _, _, _],
                          [_, _, _, _, _, _, _],
                          [_, _, _, _, _, _, _],
                          [_, _, _, _, _, _, 0],
                          [_, _, _, _, 0, 0, 0]])
        state = ConnectFourGame.apply_move(initial_state, 3)
        self.assertEqual(state.board,
                         [[_, _, _, _, _, _, _],
                          [_, _, _, _, _, _, _],
                          [_, _, _, _, _, _, _],
                          [_, _, _, _, _, _, _],
                          [_, _, _, _, _, _, _],
                          [_, _, _, 0, 0, 0, 0]])
        self.assertEqual(state.winner, 0)

        _ = None
        board = [[_, _, _, _, _, _, _],
                 [_, _, _, _, _, _, _],
                 [_, _, _, _, _, _, _],
                 [_, _, _, _, _, 1, 0],
                 [_, _, _, _, 1, 0, 1],
                 [_, _, _, 1, 0, 0, 0]]
        state = ConnectFourGame.initial_state()
        state = state._replace(board=board,
                               bitboards=get_bitboards(board),
                               current_player=1)
        state = ConnectFourGame.apply_move(state, 6)
        self.assertEqual(state.winner, 1)

    def test_with_mcts(self):
        _ = None
        board = [[_, _, _, _, _, _, _],
                 [_, _, _, _, _, _, _],
                 [_, _, _, _, _, _, _],
                 [_, _, _, _, _, _, _],
                 [_, _, 1, 1, 1, _, _],
                 [_, _, 0, 0, 0, _, _]]
        state = ConnectFourGame.State(
            board=board,
            current_player=0,
            bitboards=get_bitboards(board),
            winner=None)
        result = (MCTS(ConnectFourGame, state)
                  .get_simulation_result(100))
        self.assertIn(result.move, [1, 5])
