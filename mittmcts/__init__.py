from collections import defaultdict, namedtuple, Counter
from copy import deepcopy
from time import time

from math import sqrt, log
from random import choice, random

from six import iteritems


class Draw(object):
    pass


Draw = Draw()


class Node(object):
    def __init__(self, game, state, parent, move, c, depth=0):
        self.parent = parent
        self.__state = state
        if parent is None:
            self.__initial_state = deepcopy(state)
        self.__children = {}
        self.game = game
        self.move = move
        self.visits = 0
        self.draws = 0
        self.wins_by_player = defaultdict(lambda: 0)
        self.misc_by_player = defaultdict(dict)
        self.impossible_state = False
        self.c = c
        self.depth = depth

    def ucb1(self, player):
        if not self.parent:
            return 0
        wins_by_player = self.wins_by_player.get(player, 0)
        try:
            ucb = (
                (float(wins_by_player + (self.draws * 0.5)) / self.visits) +
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

    def determine(self):
        # if games implement a determine classmethod then we are
        # doing ISMCTS so we randomly pick the hidden state every time
        # we play out
        if hasattr(self.game, 'determine'):
            self.__state = self.game.determine(self.__initial_state)

    def add_new_children_for_determination(self, moves):
        self.__children.update({move: Node(game=self.game,
                                           state=None,
                                           move=move,
                                           parent=self,
                                           c=self.c,
                                           depth=self.depth + 1)
                                for move in moves
                                if move not in self.__children})

    @property
    def children(self):
        is_random, moves = self.game.get_moves(self.state)
        self.is_random = is_random
        self.add_new_children_for_determination(moves)
        return [child for move, child in iteritems(self.__children)
                if move in moves]

    def get_best_child(self):
        # force instantiation of child nodes and get self.is_random set
        children = self.children

        if not children:
            raise ValueError('Need to have children to find the '
                             'best child')

        if self.is_random:
            return choice(children)

        # visit unplayed moves first
        # if all moves have been visited then visit the move with the highest
        # ucb1 payout
        children = sorted(children,
                          key=lambda c: (c.visits == 0 and random() or -1,
                                         c.ucb1(self.current_player)))
        return children[-1]

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
            self.add_new_children_for_determination(actual_options)
            children = [child for move, child in iteritems(self.__children)
                        if move in actual_options]
        if not children:
            raise Exception('No children when trying to find most visited '
                            'move\n actual_options=%r children=%r' %
                            (actual_options, children))

        return sorted(children, key=lambda c: c.visits)[-1]

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

    def reset_state(self):
        self.__state = None

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

        self.__initial_state = deepcopy(self.__initial_state)

    def get_simulation_result(self,
                              iterations=1,
                              actual_options=None,
                              get_leaf_nodes=False,
                              max_seconds=None):
        root_node = Node(game=self.game,
                         parent=None,
                         state=self.__initial_state,
                         move=None,
                         c=self.c)
        MCTSResult = namedtuple('MCTSResult', 'root, move, leaf_nodes,'
                                              'max_depth, avg_depth')
        if max_seconds:
            iterations = float('inf')
        plays = 0
        max_depth = 0
        total_depth = 0
        leaf_nodes = []
        determined = hasattr(self.game, 'determine')
        start_time = time()
        while plays < iterations:
            if max_seconds is not None and time() - start_time > max_seconds:
                break
            root_node.determine()
            current_node = root_node
            while current_node.winner is None and current_node.children:
                current_node = current_node.get_best_child()
                if determined:
                    current_node.reset_state()
            if current_node.winner is None:
                raise ValueError('A game cannot have a terminal node that '
                                 'has no winner. If the game was a draw '
                                 'return Draw')
            current_node.backprop()
            max_depth = max(max_depth, current_node.depth)
            total_depth += current_node.depth
            plays += 1
            if get_leaf_nodes:
                    leaf_nodes.append(current_node)

        move = root_node.most_visited_child(actual_options).move
        return MCTSResult(root=root_node,
                          move=move,
                          leaf_nodes=leaf_nodes,
                          avg_depth=float(total_depth) / plays,
                          max_depth=max_depth)


def flamegraph(mcts_result, depth=None):
    root_node = mcts_result.root
    leaf_nodes = mcts_result.leaf_nodes
    walks = Counter()
    current_player = root_node.current_player
    for node in leaf_nodes:
        moves = []
        while node:
            extra = ''
            if node == root_node:
                break
            else:
                move = node.move
            if node.parent.current_player != current_player:
                extra = '-opp'
            if node.winner == Draw:
                moves.insert(0, '{}-draw'.format(current_player))
            elif node.winner == current_player:
                moves.insert(0, '{}-win'.format(current_player))
            elif node.winner is not None:
                moves.insert(0, '{}-lose'.format(current_player))
            moves.insert(0, str(move) + extra)
            node = node.parent
        if depth is not None:
            moves = moves[:depth]
        walks[';'.join(moves)] += 1
    for path, count in walks.iteritems():
        print('{} {}'.format(path, count))
