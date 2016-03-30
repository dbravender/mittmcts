from json import JSONEncoder, dumps
from sys import stdout

from six.moves import input

from mittmcts import MCTS
from test.euchre import EuchreGame, playable_cards, suit


class EuchreJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return JSONEncoder.default(self, obj)


def dump_state(state, hands, children=None, move=None):
    if children is None:
        children = []

    children = {
        child.move: {'ucb': child.ucb1(child.parent.current_player),
                     'visits': child.visits,
                     'wins': child.wins_by_player[child.parent.current_player]}
        for child in children}

    print(dumps({'state': state.__dict__,
                 'hands': hands,
                 'children': children,
                 'error': None},
                cls=EuchreJSONEncoder))
    stdout.flush()


def main():
    state = EuchreGame.initial_state()
    hands = EuchreGame.determine(state).hands
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
        result = (
            MCTS(EuchreGame, state)
            .get_simulation_result(1000, actual_options))
        move = result.move
        dump_state(state, hands, result.root.children, move)
        if state.current_player == 0:
            while True:
                try:
                    move = input('')
                    assert move in hands[0]
                    break
                except (AssertionError, ValueError) as e:
                    print(dumps({'error': 'That is not a legal move'}))
        hands[state.current_player].remove(move)
        state = EuchreGame.apply_move(state, move)


if __name__ == '__main__':
    main()
