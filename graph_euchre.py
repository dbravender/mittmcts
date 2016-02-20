from mittmcts import MCTS, flamegraph
from test.euchre import EuchreGame


def main():
    state = EuchreGame.State(
        cards_played_by_player=[None, None, None, None],
        current_player=0,
        lead_card=None,
        trump='d',
        winning_team=None,
        visible_hand=['qc', 'jh', 'ad', '9s'],
        remaining_cards=['9h', 'qs', 'kh', 'jd', '0s', 'ah', 'kd', '9d',
                         'js', 'ks', 'as', 'qd', '0d', 'qh', '0h', 'jc'],
        tricks_won_by_team=[1, 0],
        voids_by_player=[set([]), set([]), set([]), set([])])
    result = (MCTS(EuchreGame, state)
              .get_simulation_result(1000, get_leaf_nodes=True))
    flamegraph(result)


if __name__ == '__main__':
    main()
