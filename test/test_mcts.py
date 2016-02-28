import unittest

from mock import patch

from test.games import (
    GameWithOneMove, GameWithTwoMoves, SimpleDiceRollingGame, TicTacToeGame,
    GameWithManyMovesOnlyOneDetermined
)
from mittmcts import MCTS, Draw


class TestMCTS(unittest.TestCase):
    def test_game_with_one_move(self):
        result = MCTS(GameWithOneMove).get_simulation_result(100)
        self.assertEqual(result.move, 'win')
        self.assertEqual(result.root.children[0].wins_by_player[1], 100)
        self.assertEqual(result.max_depth, 1)

    def test_game_with_two_possible_moves(self):
        result = MCTS(GameWithTwoMoves).get_simulation_result(100)
        self.assertEqual(result.root.children[0].move, 0)
        self.assertEqual(result.root.children[0].wins_by_player[1], 0)
        self.assertIsNone(result.root.children[0].winner)
        self.assertEqual(result.root.children[0].children[0].winner, 2)
        self.assertEqual(result.root.children[0].children[0].wins_by_player,
                         {2: result.root.children[0].children[0].visits})
        self.assertEqual(result.root.children[1].move, 1)
        self.assertEqual(result.root.children[1].winner, 1)
        self.assertEqual(result.root.children[1].wins_by_player,
                         {1: result.root.children[1].visits})
        self.assertEqual(result.move, 1)
        self.assertEqual(result.max_depth, 2)
        self.assertEqual(result.avg_depth, 1.06)

    def test_random_moves_selected_randomly(self):
        with patch('mittmcts.choice') as mock_choice:
            # always choose the first item in random choices
            # (lowest die rolls in our silly game)
            mock_choice.side_effect = lambda items: items[0]
            result = MCTS(SimpleDiceRollingGame).get_simulation_result(100)
            # because the player chooes to roll no dice it always loses
            self.assertEqual(result.root.children[0].wins_by_player[1], 0)
            self.assertEqual(result.root.children[1].wins_by_player[1], 0)
            self.assertEqual(result.root.children[2].wins_by_player[1], 0)
            self.assertEqual(result.root.misc_by_player[1]['min_score'], 0)
            self.assertEqual(result.root.misc_by_player[1]['max_score'], 2)
            self.assertEqual(result.root.children[1]
                             .misc_by_player[1]['min_score'],
                             1)
            self.assertEqual(result.root.children[1]
                             .misc_by_player[1]['max_score'],
                             1)
            self.assertEqual(result.root.children[2]
                             .misc_by_player[1]['min_score'],
                             2)
            self.assertEqual(result.root.children[2]
                             .misc_by_player[1]['max_score'],
                             2)
            self.assertEqual(result.root.wins_by_player[1], 0)

        with patch('mittmcts.choice') as mock_choice:
            mock_choice.side_effect = lambda items: items[-1]
            result = MCTS(SimpleDiceRollingGame).get_simulation_result(100)
            # 100 simulations should be enough time for UCB1 to converge on
            # the always winning choice given our loaded dice
            self.assertEqual(result.move, 2)
            # because the player chooses the highest die roll the player wins
            # every time it rolls two dice
            self.assertEqual(result.root.children[2].wins_by_player[1],
                             result.root.children[2].visits)
            self.assertEqual(result.root.children[2]
                             .misc_by_player[1]['min_score'],
                             12)
            self.assertEqual(result.root.children[2]
                             .misc_by_player[1]['max_score'],
                             12)
            self.assertEqual(result.root.children[2]
                             .misc_by_player[1]['avg_score'],
                             12)

    def test_selects_winning_tictactoe_move(self):
        ___ = None
        one_move_from_winning = TicTacToeGame.State(board=['O', 'O', ___,
                                                           'X', ___, 'X',
                                                           ___, 'X', ___],
                                                    current_player='O',
                                                    winner=None)
        result = (MCTS(TicTacToeGame, one_move_from_winning)
                  .get_simulation_result(100))
        self.assertEqual(result.move, 2)
        one_move_from_winning = TicTacToeGame.State(board=['O', ___, ___,
                                                           'O', 'X', 'X',
                                                           ___, 'X', ___],
                                                    current_player='O',
                                                    winner=None)
        result = (MCTS(TicTacToeGame, one_move_from_winning)
                  .get_simulation_result(100))
        self.assertEqual(result.move, 6)

    def test_tictactoe_tie(self):
        ___ = None
        one_move_from_winning = TicTacToeGame.State(board=['O', 'X', ___,
                                                           'X', 'O', 'O',
                                                           'O', 'X', 'X'],
                                                    current_player='X',
                                                    winner=None)
        result = (MCTS(TicTacToeGame, one_move_from_winning)
                  .get_simulation_result(100))
        self.assertEqual(result.move, 2)
        self.assertEqual(result.root.children[0].winner, Draw)

    def test_only_determined_moves_are_followed(self):
        result = (MCTS(GameWithManyMovesOnlyOneDetermined)
                  .get_simulation_result(100))
        self.assertEqual(result.root.children[0].move, 1)
        self.assertEqual(result.root.children[0].visits, 100)
