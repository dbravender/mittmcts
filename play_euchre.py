from copy import deepcopy

from mittmcts import MCTS
from test.euchre import EuchreGame, playable_cards, suit


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def main():
    state = EuchreGame.initial_state()
    cards = deepcopy(state.remaining_cards)
    hands = list(chunks(cards, 5))
    EuchreGame.print_board(state)
    while True:
        winner = EuchreGame.get_winner(state)
        if winner is not None:
            EuchreGame.print_board(state)
            print 'Team %r wins!' % winner
            print state
            break
        if state.current_player == 0:
            result = (
                MCTS(EuchreGame, state)
                .get_simulation_result(1000))
            print 'ISMCTS chose >>%r<<' % result.move
            while True:
                try:
                    move = raw_input('Move (or l to list child nodes, '
                                     's to show state):')
                    if move == 'l':
                        for x in result.root.children:
                            print x
                        continue
                    if move == 's':
                        print state
                        continue
                    state = EuchreGame.apply_move(state, move)
                    break
                except ValueError:
                    print 'That is not a legal move'
        else:
            actual_options = playable_cards(state.trump,
                                            suit(state.trump,
                                                 state.lead_card),
                                            hands[state.current_player - 1])
            result = (
                MCTS(EuchreGame, state)
                .get_simulation_result(1000,
                                       actual_options))
            print result.move
            hands[state.current_player - 1].remove(result.move)
            state = EuchreGame.apply_move(state, result.move)
            EuchreGame.print_board(state)


if __name__ == '__main__':
    main()
