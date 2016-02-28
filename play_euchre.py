from six.moves import input

from mittmcts import MCTS
from test.euchre import EuchreGame, playable_cards, suit


def main():
    state = EuchreGame.initial_state()
    print state
    hands = EuchreGame.determine(state).hands
    while True:
        EuchreGame.print_board(state)
        winner = EuchreGame.get_winner(state)
        if winner is not None:
            print('Team %r wins!' % winner)
            print(state)
            break
        if state.current_player == 0:
            result = (
                MCTS(EuchreGame, state)
                .get_simulation_result(1000))
            print('ISMCTS chose >>%r<<' % result.move)
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
                    state = EuchreGame.apply_move(state, move)
                    break
                except ValueError:
                    print('That is not a legal move')
        else:
            actual_options = playable_cards(state.trump,
                                            suit(state.trump,
                                                 state.lead_card),
                                            hands[state.current_player])
            result = (
                MCTS(EuchreGame, state)
                .get_simulation_result(1000,
                                       actual_options))
            hands[state.current_player].remove(result.move)
            state = EuchreGame.apply_move(state, result.move)


if __name__ == '__main__':
    main()
