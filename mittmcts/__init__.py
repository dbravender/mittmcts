from collections import defaultdict, namedtuple
from math import sqrt, log
from random import choice, random


class Draw(object):
    pass
Draw = Draw()


class ImpossibleState(Exception):
    pass


class Node(object):
    def __init__(self, game, state, parent, move, c, depth=0):
        self.parent = parent
        self.__state = state
        self.__children = None
        self.game = game
        self.move = move
        self.visits = 0
        self.draws = 0
        self.wins_by_player = defaultdict(lambda: 0)
        self.misc_by_player = defaultdict(dict)
        self.determine = getattr(self.game, 'determine', None)
        self.impossible_state = False
        self.c = c
        self.depth = depth

    def ucb1(self, player):
        if not self.parent:
            return 0
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
            is_random, moves = self.game.get_moves(self.state)
            self.is_random = is_random
            self.__children = [Node(game=self.game,
                                    state=None,
                                    move=move,
                                    parent=self,
                                    c=self.c,
                                    depth=self.depth + 1)
                               for move in moves]
        return self.__children

    def get_best_child(self):
        # force instantiation of child nodes and get self.is_random set
        children = self.children
        if self.is_random:
            return choice(children)
        player = self.current_player
        # if games implement a determine classmethod then we are doing ISMCTS
        # so we randomly pick the hidden state every time we select a child
        # node
        if self.determine:
            available_moves_in_this_state = self.determine(self.state)
            children = [child for child in children
                        if (child.move in available_moves_in_this_state
                            and child.impossible_state is False)]
            if not children and self.winner is None:
                self.impossible_state = True
                raise ImpossibleState()
        # visit unplayed moves first
        # if all moves have been visited then visit the move with the highest
        # ucb1 payout
        children = sorted([(child.visits == 0 and random() or -1,
                            child.ucb1(player),
                            child)
                          for child in children])
        if children:
            return children[-1][2]
        else:
            return None

    @property
    def current_player(self):
        return self.game.current_player(self.state)

    def dump_tree(self):
        print(repr(self))
        children = self.children
        while children:
            next_children = []
            for child in children:
                print(repr(child))
                next_children.extend(child.children)
            children = next_children

    def most_visited_child(self, actual_options=None):
        children = self.children
        if actual_options:
            children = [child for child in children
                        if child.move in actual_options]
        return sorted([(child.visits, child)
                       for child in children])[-1][1]

    def backprop(self):
        winner = self.winner
        current_node = self
        update_misc = None
        if hasattr(self.game, 'update_misc'):
            update_misc = self.game.update_misc
        while current_node:
            current_node.visits += 1
            if winner is Draw:
                current_node.draws += 1
            else:
                current_node.wins_by_player[winner] += 1
            if update_misc:
                update_misc(self.state, current_node.misc_by_player)
            current_node = current_node.parent

    def __repr__(self):
        return 'state=%r move=%r visits=%r wins=%r ucb=%r' % (
            self.state,
            self.move,
            self.visits,
            self.wins_by_player[self.parent.current_player],
            self.ucb1(self.parent.current_player))


class MCTS(object):
    def __init__(self, game, initial_state=None, c=sqrt(2)):
        self.game = game
        self.c = c
        if initial_state:
            self.__initial_state = initial_state
        else:
            self.__initial_state = game.initial_state()

    def get_simulation_result(self,
                              iterations=1,
                              actual_options=None,
                              get_leaf_nodes=False):
        root_node = Node(game=self.game,
                         parent=None,
                         state=self.__initial_state,
                         move=None,
                         c=self.c)
        MCTSResult = namedtuple('MCTSResult', 'root, move, leaf_nodes,'
                                              'max_depth, avg_depth')
        plays = 0
        max_depth = 0
        total_depth = 0
        leaf_nodes = []
        while plays < iterations:
            current_node = root_node
            try:
                while current_node.winner is None and current_node.children:
                    current_node = current_node.get_best_child()
                if current_node.winner is not None:
                    current_node.backprop()
                    max_depth = max(max_depth, current_node.depth)
                    total_depth += current_node.depth
                    plays += 1
                    if get_leaf_nodes:
                            leaf_nodes.append(current_node)
            except ImpossibleState:
                continue

        move = root_node.most_visited_child(actual_options).move
        return MCTSResult(root=root_node,
                          move=move,
                          leaf_nodes=leaf_nodes,
                          avg_depth=float(total_depth) / plays,
                          max_depth=max_depth)
