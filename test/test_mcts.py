from collections import namedtuple
from copy import copy
import unittest

from mcts import MCTS


class GameWithOneMove(object):
    State = namedtuple('GameWithOneMoveState',
                       'winner, current_player')

    @classmethod
    def initial_state(cls):
        return cls.State(winner=None, current_player=1)

    @classmethod
    def get_moves(cls, state):
        if state.winner:
            return (False, [])
        else:
            return (False, ['win'])

    @classmethod
    def apply_move(cls, state, move):
        if move != 'win':
            raise ValueError('Invalid move')
        new_state = state._replace(winner=state.current_player)
        return new_state

    @classmethod
    def get_winner(cls, state):
        return state.winner

    @classmethod
    def current_player(cls, state):
        return state.current_player


class GameWithTwoMoves(object):
    State = namedtuple('GameWithOneMoveState',
                       'board, winner, current_player')

    @classmethod
    def initial_state(cls):
        return cls.State(board=[0, 0], winner=None, current_player=1)

    @classmethod
    def get_moves(cls, state):
        return (False, [position for position, player in enumerate(state.board)
                        if player == 0])

    @classmethod
    def apply_move(cls, state, move):
        if state.board[move] != 0:
            raise ValueError('Invalid move')
        new_board = copy(state.board)
        new_board[move] = state.current_player
        new_state = state._replace(current_player=state.current_player + 1,
                                   board=new_board)
        if move == 1:
            new_state = new_state._replace(winner=state.current_player)
        return new_state

    @classmethod
    def get_winner(cls, state):
        return state.winner

    @classmethod
    def current_player(cls, state):
        return state.current_player


class TestMCTS(unittest.TestCase):
    def test_game_with_one_move(self):
        move, root = MCTS(GameWithOneMove).get_move_and_root(100)
        self.assertEqual(move, 'win')
        self.assertEqual(root.children[0].wins_by_player[1], 100)

    def test_game_with_two_possible_moves(self):
        move, root = MCTS(GameWithTwoMoves).get_move_and_root(100)
        self.assertEqual(root.children[0].move, 0)
        self.assertEqual(root.children[0].wins_by_player[1], 0)
        self.assertIsNone(root.children[0].winner)
        self.assertEqual(root.children[0].children[0].winner, 2)
        self.assertEqual(root.children[0].children[0].wins_by_player,
                         {2: root.children[0].children[0].visits})
        self.assertEqual(root.children[1].move, 1)
        self.assertEqual(root.children[1].winner, 1)
        self.assertEqual(root.children[1].wins_by_player,
                         {1: root.children[1].visits})
        self.assertEqual(move, 1)
