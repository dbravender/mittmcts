from collections import defaultdict, namedtuple
from math import sqrt, log


class Draw(object):
    pass
Draw = Draw()


class Node(object):
    def __init__(self, game, state, parent, move, c):
        self.parent = parent
        self.__state = state
        self.__children = None
        self.game = game
        self.move = move
        self.visits = 0
        self.draws = 0
        self.wins_by_player = defaultdict(lambda: 0)
        self.misc_by_player = defaultdict(lambda: 0)
        self.c = c

    def ucb1(self, player):
        wins_by_player = self.wins_by_player.get(player, 0)
        try:
            ucb = (
             ((wins_by_player + (self.draws * 0.5)) / self.visits) +
              (self.c * sqrt(log(self.parent.visits) / self.visits)))
        except ZeroDivisionError:
            ucb = 0
        return ucb

    @property
    def winner(self):
        return self.game.get_winner(self.state)

    @property
    def state(self):
        if not self.__state:
            self.__state = self.game.apply_move(self.parent.state, self.move)
        return self.__state

    @property
    def children(self):
        if self.__children is None:
            self.__children = [Node(game=self.game,
                                    state=None,
                                    move=move,
                                    parent=self,
                                    c=self.c)
                             for move in self.game.get_moves(self.state)]
        return self.__children

    def get_best_child(self):
        player = self.game.current_player(self.state)
        # visit unplayed moves first
        # if all moves have been visited then visit the move with the highest
        # ucb1 payout
        children = sorted([(child.visits == 0, child.ucb1(player), child)
                          for child in self.children])
        if children:
            return children[-1][2]
        else:
            return None

    @property
    def most_visited_child(self):
        return sorted([(child.visits, child)
                       for child in self.children])[-1][1]

    def backprop(self):
        winner = self.winner
        current_node = self
        while current_node:
            current_node.visits += 1
            if winner is Draw:
                current_node.draws += 1
            else:
                current_node.wins_by_player[winner] += 1
            current_node = current_node.parent


class MCTS(object):
    def __init__(self, game, initial_state=None, c=sqrt(2)):
        self.game = game
        self.c = c
        if initial_state:
            self.__initial_state = initial_state
        else:
            self.__initial_state = game.initial_state()

    def get_move_and_root(self, iterations=1):
        MoveTree = namedtuple('MoveTree', 'move, tree')
        root_node = Node(game=self.game,
                         parent=None,
                         state=self.__initial_state,
                         move=None,
                         c=self.c)
        plays = 0
        while plays < iterations:
            current_node = root_node
            plays += 1
            while current_node.winner is None:
                current_node = current_node.get_best_child()
            current_node.backprop()
        return MoveTree(root_node.most_visited_child.move, root_node)
