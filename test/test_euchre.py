import unittest

from mittmcts import MCTS

from test.euchre import (
    second_highest_jack, winning_card, deal, sort_by_trump_and_lead,
    playable_cards, suit, potential_cards_given_voids,
    EuchreGame
)


class TestEuchre(unittest.TestCase):
    def test_deal(self):
        self.assertEqual(deal(),
                         ['ad', 'kd', 'qd', 'jd', '0d', '9d',
                          'ah', 'kh', 'qh', 'jh', '0h', '9h',
                          'as', 'ks', 'qs', 'js', '0s', '9s',
                          'ac', 'kc', 'qc', 'jc', '0c', '9c'])

    def test_second_highest_jack(self):
        self.assertEqual(second_highest_jack('c'), 'js')
        self.assertEqual(second_highest_jack('s'), 'jc')
        self.assertEqual(second_highest_jack('d'), 'jh')
        self.assertEqual(second_highest_jack('h'), 'jd')

    def test_suit(self):
        self.assertEqual(suit('s', 'jc'), 's')
        self.assertEqual(suit('c', 'js'), 'c')
        self.assertEqual(suit('d', 'jh'), 'd')
        self.assertEqual(suit('h', 'jd'), 'h')

    def test_sort_by_trump_and_lead(self):
        self.assertEqual(sort_by_trump_and_lead('d', 'h', deal())[:12],
                         ['jd', 'jh', 'ad', 'kd', 'qd', '0d', '9d',
                          'ah', 'kh', 'qh', '0h', '9h'])
        self.assertEqual(sort_by_trump_and_lead('c', 'd', deal())[:13],
                         ['jc', 'js', 'ac', 'kc', 'qc', '0c', '9c',
                          'ad', 'kd', 'qd', 'jd', '0d', '9d'])

    def test_winning_card(self):
        self.assertEqual(winning_card('c', 'c', ['jc', 'js', 'as', '0s']),
                         'jc')
        self.assertEqual(winning_card('c', 'c', ['js', 'ac', 'jd', '0s']),
                         'js')
        self.assertEqual(winning_card('d', 'c', ['jc', 'ac', '0s', '9s']),
                         'ac')
        self.assertEqual(winning_card('d', 'c', ['9d', 'ac', '0s', '9s']),
                         '9d')

    def test_playable_cards(self):
        self.assertEqual(playable_cards('c', 'd', deal()),
                         ['ad', 'kd', 'qd', 'jd', '0d', '9d'])
        self.assertEqual(playable_cards('c', 'c', deal()),
                         ['js', 'ac', 'kc', 'qc', 'jc', '0c', '9c'])
        self.assertEqual(playable_cards('c', 'c', deal()),
                         ['js', 'ac', 'kc', 'qc', 'jc', '0c', '9c'])
        self.assertEqual(playable_cards('c', 'c', ['ad']),
                         ['ad'])

    def test_potential_cards_given_voids(self):
        self.assertEqual(
            potential_cards_given_voids('c', ['d'], ['jd', 'jc']), ['jc'])
        self.assertEqual(
            potential_cards_given_voids('d', ['d'], ['jd', 'jh']), [])

    def test_initial_state(self):
        try:
            EuchreGame.initial_state(
                ['notacard', 'notacard2', 'notacard4', 'notacard5'])
            self.fail('Should not allow invalid starting hands')
        except ValueError:
            pass
        try:
            EuchreGame.initial_state(['js'])
            self.fail('initial_state should require a hand of 5 cards')
        except ValueError:
            pass

        state = EuchreGame.initial_state(['ad', 'kd', 'qd', 'jd', '0d'])
        self.assertEqual(sorted(state.remaining_cards),
                         sorted(['9d',
                                 'ah', 'kh', 'qh', 'jh', '0h', '9h',
                                 'as', 'ks', 'qs', 'js', '0s', '9s',
                                 'ac', 'kc', 'qc', 'jc', '0c', '9c']))
        state = EuchreGame.initial_state()
        self.assertEqual(len(state.visible_hand), 5)
        state = EuchreGame.initial_state(trump='c')
        self.assertEqual(state.trump, 'c')

        try:
            EuchreGame.initial_state(trump='p')
            self.fail('initial_state should require valid trump')
        except ValueError:
            pass

    def test_apply_move_sets_a_winner_after_4_plays(self):
        state = EuchreGame.initial_state()
        for x in range(4):
            if state.current_player == 0:
                move = state.visible_hand[0]
            else:
                move = state.remaining_cards[0]
            state = EuchreGame.apply_move(state, move)
        self.assertEqual(sum(state.tricks_won_by_team), 1)

    def test_a_whole_hand(self):
        state = EuchreGame.initial_state(['jd', 'jh', '9c', '9h', 'as'], 'd')
        state = EuchreGame.apply_move(state, 'jd')
        state = EuchreGame.apply_move(state, 'qd')
        state = EuchreGame.apply_move(state, '9d')
        state = EuchreGame.apply_move(state, '0d')
        self.assertEqual(state.tricks_won_by_team, [1, 0])
        self.assertEqual(state.current_player, 0)
        state = EuchreGame.apply_move(state, 'jh')
        state = EuchreGame.apply_move(state, 'ah')
        state = EuchreGame.apply_move(state, 'jc')
        state = EuchreGame.apply_move(state, '0c')
        self.assertEqual(state.tricks_won_by_team, [2, 0])
        self.assertEqual(state.current_player, 0)
        state = EuchreGame.apply_move(state, '9h')
        state = EuchreGame.apply_move(state, '0h')
        state = EuchreGame.apply_move(state, 'kh')
        state = EuchreGame.apply_move(state, 'qh')
        self.assertEqual(state.tricks_won_by_team, [3, 0])
        self.assertEqual(state.current_player, 2)
        state = EuchreGame.apply_move(state, 'qc')
        state = EuchreGame.apply_move(state, 'ac')
        state = EuchreGame.apply_move(state, '9c')
        state = EuchreGame.apply_move(state, 'kc')
        self.assertEqual(state.tricks_won_by_team, [3, 1])
        self.assertEqual(state.current_player, 3)
        self.assertIsNone(state.winning_team)
        state = EuchreGame.apply_move(state, '0s')
        try:
            EuchreGame.apply_move(state, 'ad')
            self.fail('Did not follow suit earlier')
        except ValueError:
            pass
        state = EuchreGame.apply_move(state, 'as')
        state = EuchreGame.apply_move(state, 'js')
        state = EuchreGame.apply_move(state, '9s')
        self.assertEqual(state.tricks_won_by_team, [4, 1])
        self.assertEqual(state.winning_team, 0)
        self.assertEqual(EuchreGame.get_winner(state), 0)
        self.assertEqual(EuchreGame.current_player(state), 0)

    def test_with_mcts(self):
        state = EuchreGame.initial_state(['0d', '0h', 'as', 'ac', 'ah'], 'd')
        result = MCTS(EuchreGame, state).get_simulation_result(100)
        self.assertEqual(result.max_depth, 20)
        # there is no longer option now so all players playing will always
        # result in 20 cards being played
        self.assertEqual(result.avg_depth, 20)

    def test_why_are_we_not_evaluating_all_potential_determinizations(self):
        state = EuchreGame.State(
            cards_played_by_player=[None, None, None, None],
            current_player=0,
            lead_card=None,
            trump='c',
            winning_team=None,
            visible_hand=['qs', 'qh'],
            remaining_cards=['0s', 'kd', 'js', 'ks', 'as',
                             'qd', 'jd', '9s', '0h', 'jc'],
            tricks_won_by_team=[1, 2],
            voids_by_player=[set(['d']), set([]), set([]), set([])])
        result = MCTS(EuchreGame, state).get_simulation_result(1000)
        for child in result.root.children:
            for grandchild in child.children:
                self.assertTrue(grandchild.visits > 0)

    def test_this_hand_should_win_every_time(self):
        state = EuchreGame.State(
            cards_played_by_player=[None, None, None, None],
            current_player=0,
            lead_card=None,
            trump='d',
            winning_team=None,
            visible_hand=['qc', 'jh', 'jd', '9s'],
            remaining_cards=['9h', 'qs', 'kh', 'ad', '0s', 'ah', 'kd', '9d',
                             'js', 'ks', 'as', 'qd', '0d', 'qh', '0h', 'jc'],
            tricks_won_by_team=[1, 0],
            voids_by_player=[set([]), set([]), set([]), set([])])
        result = (MCTS(EuchreGame, state)
                  .get_simulation_result(100, get_leaf_nodes=True))
        for node in result.leaf_nodes:
            self.assertGreaterEqual(node.state.tricks_won_by_team[0], 3)
