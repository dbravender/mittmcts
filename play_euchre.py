from six.moves import input

from mittmcts import MCTS
from test.euchre import EuchreGame, playable_cards, suit


def main():
    state = EuchreGame.initial_state()
    print(state)
    hands = EuchreGame.determine(state).hands
    print(hands)
    while True:
        EuchreGame.print_board(state)
        winner = EuchreGame.get_winner(state)
        if winner is not None:
            print('Team %r wins!' % winner)
            print(state)
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
        if state.current_player == 0:
            print('ISMCTS chose >>%r<<' % move)
            while True:
                try:
                    move = input('Move (or l to list child nodes, '
                                 's to show state):')
                    if move == 'l':
                        for x in result.root.children:
                            print(x)
                        continue
                    if move == 's':
                        print(state)
                        continue
                    assert move in hands[0]
                    break
                except (AssertionError, ValueError) as e:
                    print(str(e))
        hands[state.current_player].remove(move)
        state = EuchreGame.apply_move(state, move)


if __name__ == '__main__':
    main()
