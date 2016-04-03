from collections import namedtuple
from copy import copy

from six.moves import filter

from mittmcts import Draw


class GameWithOneMove(object):
    """An extremely silly game where you can only choose to win.
    MCTS should choose to win this game every time"""

    State = namedtuple('GameWithOneMoveState',
                       ['winner', 'current_player'])

    @staticmethod
    def initial_state():
        return GameWithOneMove.State(winner=None, current_player=1)

    @staticmethod
    def get_moves(state):
        if state.winner:
            return (False, [])
        else:
            return (False, ['win'])

    @staticmethod
    def apply_move(state, move):
        if move != 'win':
            raise ValueError('Invalid move')
        return GameWithOneMove.State(winner=state.current_player,
                                     current_player=1)

    @staticmethod
    def get_winner(state):
        return state.winner

    @staticmethod
    def current_player(state):
        return state.current_player


class GameWithTwoMoves(object):
    """A game with two players where the first player can choose to win or
    pass and then the next player has to choose to win if the first player
    passed"""

    State = namedtuple('GameWithOneMoveState',
                       ['board', 'winner', 'current_player'])

    @staticmethod
    def initial_state():
        return GameWithTwoMoves.State(board=[0, 0],
                                      winner=None,
                                      current_player=1)

    @staticmethod
    def get_moves(state):
        return (False, [position for position, player in enumerate(state.board)
                        if player == 0])

    @staticmethod
    def apply_move(state, move):
        winner = None
        new_board = copy(state.board)
        if state.board[move] != 0:
            raise ValueError('Invalid move')
        new_board[move] = state.current_player
        if move == 1:
            winner = state.current_player
        return GameWithTwoMoves.State(board=new_board,
                                      winner=winner,
                                      current_player=state.current_player + 1)

    @staticmethod
    def get_winner(state):
        return state.winner

    @staticmethod
    def current_player(state):
        return state.current_player


class SimpleDiceRollingGame(object):
    """A one-player game where the player chooses to roll 0, 1 or 2 dice and
    rolls them. The player wins if they roll a total greater than 6"""

    State = namedtuple('SimpleDiceRollingGameState',
                       'score, winner, round, dice_to_roll')
    die_roll_outcome = range(1, 7)

    @classmethod
    def initial_state(cls):
        return cls.State(score=0,
                         winner=None,
                         dice_to_roll=0,
                         round=0)

    @classmethod
    def get_moves(cls, state):
        if state.round == 2:
            return (False, [])

        if state.round == 0:
            return (False, [0, 1, 2])

        elif state.dice_to_roll == 0:
            return (True, [0])
        elif state.dice_to_roll == 1:
            return (True, cls.die_roll_outcome)
        elif state.dice_to_roll == 2:
            return (True, [x + y
                           for x in cls.die_roll_outcome
                           for y in cls.die_roll_outcome])

    @classmethod
    def apply_move(cls, state, move):
        dice_to_roll = 0
        score = 0
        winner = None

        if state.round == 0:
            dice_to_roll = move

        if state.round == 1:
            score = move
            if score > 6:
                winner = 1
            else:
                winner = 2

        return cls.State(dice_to_roll=dice_to_roll,
                         score=score,
                         winner=winner,
                         round=state.round + 1)

    @staticmethod
    def get_winner(state):
        return state.winner

    @staticmethod
    def update_misc(end_node, misc_by_player):
        if 'scores' not in misc_by_player[1]:
            misc_by_player[1] = {
                'scores': [],
                'avg_score': 0,
                'min_score': 0,
                'max_score': 0,
            }
        misc = misc_by_player[1]
        scores = misc['scores']
        scores.append(end_node.score)
        misc.update({'avg_score': float(sum(scores)) / len(scores),
                     'min_score': min(scores),
                     'max_score': max(scores)})

    @staticmethod
    def current_player(state):
        return 1


class TicTacToeGame(object):
    """Standard tic-tac-toe game"""

    State = namedtuple('TicTacToeState', 'board, current_player, winner')
    winning_scores = [7, 56, 448, 73, 146, 292, 273, 84]

    @classmethod
    def initial_state(cls):
        return cls.State(board=[None] * 9,
                         current_player='X',
                         winner=None)

    @classmethod
    def apply_move(cls, state, move):
        new_board = copy(state.board)
        if move not in range(9) or state.board[move]:
            raise ValueError('Illegal move')
        new_board[move] = state.current_player
        next_player = state.current_player == 'X' and 'O' or 'X'
        winner = None
        for player in ['X', 'O']:
            score = sum([2 ** i for i, spot in enumerate(new_board)
                        if spot == player])
            for winning_score in cls.winning_scores:
                if winning_score & score == winning_score:
                    winner = player
        if winner is None and len(list(filter(None, new_board))) == 9:
            winner = Draw
        return cls.State(board=new_board,
                         current_player=next_player,
                         winner=winner)

    @staticmethod
    def get_moves(state):
        if state.winner:
            return (False, [])
        return (False, [i for i, spot in enumerate(state.board)
                        if spot is None])

    @staticmethod
    def get_winner(state):
        return state.winner

    @staticmethod
    def current_player(state):
        return state.current_player

    @staticmethod
    def print_board(state):
        print(''.join([((x and str(x) or str(i)) +
                       ((i + 1) % 3 == 0 and '\n' or ' '))
                       for i, x in enumerate(state.board)]))


class GameWithManyMovesOnlyOneDetermined(GameWithTwoMoves):
    @classmethod
    def initial_state(cls):
        return cls.State(board=[0, 0, 0, 0, 0], winner=None, current_player=1)

    @staticmethod
    def determine(state):
        # we'll say only moving into the 2rd space is legal for this
        # determination
        return state._replace(board=[1, 0, 1, 1, 1])
