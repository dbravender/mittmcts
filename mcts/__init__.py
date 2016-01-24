from collections import namedtuple
from math import sqrt

# misc_by_player  can be used to track game-specific data not all games have
# (e.g. points)
Node = namedtuple('Node', 'state, visits, wins_by_player, draws, winner,'
                          'ucb1, children, misc_by_player')


class MCTS(object):
    def __init__(self, game, initial_state=None, c=sqrt(2)):
        self.__game = game
        self.__c = c
        if initial_state:
            self.__initial_state = initial_state
        else:
            self.__initial_state = game.initial_state()

    def get_move_and_root(self):
        MoveTree = namedtuple('MoveTree', 'move, tree')
        root_node = Node(state=self.__initial_state,
                         visits=None,
                         wins_by_player={},
                         draws=0,
                         winner=None,
                         ucb1=0,
                         children=[],
                         misc_by_player={})
        moves = self.__game.get_moves(root_node.state)
        if moves:
            return MoveTree(moves[0], root_node)
        return MoveTree(None, root_node)
