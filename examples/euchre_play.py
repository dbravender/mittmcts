from json import JSONEncoder, dumps
from sys import stdout
from time import sleep

from six.moves import input

from mittmcts import MCTS
from test.euchre import EuchreGame, playable_cards, suit


class EuchreJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return JSONEncoder.default(self, obj)


def dump_state(state, hands, children=None, move=None, table=None):
    if children is None:
        children = []
    if table is None:
        table = []

    children = {
        child.move: {'ucb': child.ucb1(child.parent.current_player),
                     'visits': child.visits,
                     'wins': child.wins_by_player[child.parent.current_player]}
        for child in children}

    print(dumps({'state': state.__dict__,
                 'hands': hands,
                 'children': children,
                 'table': table,
                 'error': None},
                cls=EuchreJSONEncoder))
    stdout.flush()


def main():
    state = EuchreGame.initial_state()
    hands = EuchreGame.determine(state).hands
    table = [None] * 4
    while True:
        winner = EuchreGame.get_winner(state)
        if winner is not None:
            dump_state(state, hands)
            break
        state_hands = [player == state.current_player and hand[:] or []
                       for player, hand in enumerate(hands)]
        state = state._replace(hands=state_hands)
        actual_options = playable_cards(state.trump,
                                        suit(state.trump,
                                             state.lead_card),
                                        hands[state.current_player])
        legal_moves = EuchreGame.get_moves(state)[1]
        result = (
            MCTS(EuchreGame, state)
            .get_simulation_result(1000, actual_options))
        move = result.move
        dump_state(state, hands, result.root.children, move, table)
        if state.current_player == 0:
            while True:
                try:
                    move = input('')
                    assert move in legal_moves
                    hands[0].remove(move)
                    table[state.current_player] = move
                    state = EuchreGame.apply_move(state, move)
                    break
                except (AssertionError, ValueError):
                    print(dumps({'error': 'That is not a legal move'}))
        else:
            hands[state.current_player].remove(move)
            table[state.current_player] = move
            state = EuchreGame.apply_move(state, move)
        if len(filter(None, table)) == 4:
            dump_state(state, hands, result.root.children, move, table)
            table = [None] * 4
            sleep(4)  # wait for the player to see the table before clearing it


if __name__ == '__main__':
    main()
