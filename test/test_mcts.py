from collections import namedtuple
from copy import deepcopy
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
            return []
        else:
            return ['win']

    @classmethod
    def apply_move(cls, state, move):
        if move != 'win':
            raise ValueError('Invalid move')
        new_state = deepcopy(state)
        new_state.winner = state.current_player
        return new_state

    @classmethod
    def get_winner(cls, state):
        return state.winner


class GameWithTwoMoves(object):
    State = namedtuple('GameWithOneMoveState',
                       'board, winner, current_player')

    @classmethod
    def initial_state(cls):
        return cls.State(board=[0, 0], winner=None, current_player=1)

    @classmethod
    def get_moves(cls, state):
        return [position for position, player in enumerate(state.board)
                if player == 0]

    @classmethod
    def apply_move(cls, state, move):
        if state.board[move] != 0:
            raise ValueError('Invalid move')
        new_state = deepcopy(state)
        if move == 0:
            new_state._replace(winner=state.current_player)
        new_state.current_player = state.current_player + 1
        return new_state

    @classmethod
    def get_winner(cls, state):
        return state.winner


class TestMCTS(unittest.TestCase):
    def test_game_with_one_move(self):
        move, _ = MCTS(GameWithOneMove).get_move_and_root()
        self.assertEqual(move, 'win')

        mcts = MCTS(GameWithOneMove,
                    initial_state=GameWithOneMove.State(winner=1,
                                                        current_player=1))
        self.assertIsNone(mcts.get_move_and_root().move)

    def test_game_with_two_possible_moves(self):
        move, _ = MCTS(GameWithTwoMoves).get_move_and_root()
        self.assertEqual(move, 0)
