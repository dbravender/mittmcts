from json import dumps, JSONEncoder
from sys import stdout

from six.moves import input

from mittmcts import MCTS, Draw
from test.connect4 import ConnectFourGame


class GameEncoder(JSONEncoder):
    def default(self, o):
        if o is Draw:
            return 'draw'
        return JSONEncoder.default(self, o)


def dump_state(state, children=None, move=None):
    if children is None:
        children = []

    if state.current_player == 0:
        overall_percent = (sum(child.wins_by_player[0]
                               for child in children) / 1000.0) * 100
    else:
        overall_percent = None

    children = {
        child.move: {'ucb': child.ucb1(child.parent.current_player),
                     'visits': child.visits,
                     'wins': child.wins_by_player[child.parent.current_player]}
        for child in children}

    print(dumps({'state': state.__dict__,
                 'children': children,
                 'overall_percent': overall_percent,
                 'error': None},
                cls=GameEncoder))
    stdout.flush()


def main():
    state = ConnectFourGame.initial_state()
    while True:
        winner = ConnectFourGame.get_winner(state)
        if winner is not None:
            dump_state(state)
            break
        legal_moves = ConnectFourGame.get_moves(state)[1]
        result = (
            MCTS(ConnectFourGame, state)
            .get_simulation_result(1000))
        move = result.move
        dump_state(state, result.root.children, move)
        if state.current_player == 0:
            while True:
                try:
                    move = int(input(''))
                    assert move in legal_moves
                    state = ConnectFourGame.apply_move(state, move)
                    break
                except (AssertionError, ValueError):
                    print(dumps({'error': 'That is not a legal move'}))
        else:
            state = ConnectFourGame.apply_move(state, move)


if __name__ == '__main__':
    main()
