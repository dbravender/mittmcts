from itertools import chain
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

    def test_initial_state_bad_cards(self):
        try:
            EuchreGame.initial_state(
                ['notacard', 'notacard2', 'notacard4', 'notacard5'])
            self.fail('Should not allow invalid starting hands')
        except ValueError:
            pass

    def test_initial_state_set_trump_and_determine_deals(self):
        state = EuchreGame.initial_state(['ad', 'kd', 'qd', 'jd', '0d'])
        state = EuchreGame.determine(state)
        self.assertEqual(len(list(chain(*state.hands))), 20)
        state = EuchreGame.initial_state(trump_card='jc')
        self.assertEqual(state.trump, 'c')

    def test_initial_state_invalid_trump(self):
        try:
            EuchreGame.initial_state(trump_card='xp')
            self.fail('initial_state should require valid trump')
        except ValueError:
            pass

    def test_initial_state_trump_determined_by_kitty(self):
        state = EuchreGame.initial_state()
        state = EuchreGame.determine(state)
        self.assertEqual(len(state.cards_played), 1)
        self.assertEqual(suit(state.trump, state.cards_played[0]), state.trump)
        self.assertIn(state.trump_card, state.cards_played)

    def test_apply_move_sets_a_winner_after_4_plays(self):
        state = EuchreGame.initial_state()
        state = EuchreGame.determine(state)
        for x in range(4):
            lead_suit = suit(state.trump, state.lead_card)
            move = playable_cards(state.trump,
                                  lead_suit,
                                  state.hands[state.current_player], )[0]
            state = EuchreGame.apply_move(state, move)
        self.assertEqual(sum(state.tricks_won_by_team), 1)

    def test_determine(self):
        state = EuchreGame.initial_state()
        state = state._replace(trump_card='jd',
                               trump='d',
                               cards_played=['jd', 'ad', 'kd', 'qd', 'qc'],
                               tricks_won_by_team=[1, 0],
                               hands=[['jc', 'kc', 'ah', 'js'],
                                      [],
                                      [],
                                      []],
                               voids_by_player=[set(),
                                                set(['d', 'h', 'c']),
                                                set(),
                                                set(['s', 'c', 'd'])])
        state = EuchreGame.determine(state)
        self.assertTrue(all([suit('d', card) == 's'
                             for card in state.hands[1]]))
        self.assertTrue(all([suit('d', card) == 'h'
                             for card in state.hands[3]]))

    def test_determine_in_the_middle_of_a_trick(self):
        state = EuchreGame.initial_state()
        state = state._replace(trump_card='jd',
                               trump='d',
                               tricks_won_by_team=[1, 0],
                               cards_played_by_player=['jh', None, None, None],
                               hands=[[],
                                      [],
                                      [],
                                      []],
                               voids_by_player=[set(),
                                                set(['d', 'h', 'c']),
                                                set(),
                                                set(['s', 'c', 'd'])])
        state = EuchreGame.determine(state)
        self.assertEqual(len(state.hands[0]), 3)
        self.assertEqual(len(state.hands[1]), 4)
        self.assertEqual(len(state.hands[2]), 4)
        self.assertEqual(len(state.hands[3]), 4)

    def test_a_whole_hand(self):
        state = EuchreGame.initial_state(['jd', 'jh', '9c', '9h', 'as'], 'kd')
        state = state._replace(hands=[['jd', 'jh', '9c', '9h', 'as'],
                                      ['qd', 'ah', '0h', 'kc', 'js'],
                                      ['9d', 'jc', 'kh', 'qc', '9s'],
                                      ['0d', '0c', 'qh', 'ac', '0s']])
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
        state = EuchreGame.initial_state(['0d', '0h', 'as', 'ac', 'ah'], 'jd')
        result = MCTS(EuchreGame, state).get_simulation_result(100)
        self.assertEqual(result.max_depth, 20)
        # there is no longer option now so all players playing will always
        # result in 20 cards being played
        self.assertEqual(result.avg_depth, 20)

    def test_this_hand_should_win_every_time(self):
        state = EuchreGame.State(
            cards_played_by_player=[None, None, None, None],
            current_player=0,
            lead_card=None,
            trump_card='0d',
            trump='d',
            winning_team=None,
            hands=[['jd', 'jh', 'ad', 'kd', 'qd'], [], [], []],
            tricks_won_by_team=[0, 0],
            cards_played=['0d'],
            voids_by_player=[set([]), set([]), set([]), set([])])
        result = (MCTS(EuchreGame, state)
                  .get_simulation_result(100, get_leaf_nodes=True))
        for node in result.leaf_nodes:
            self.assertGreaterEqual(node.state.tricks_won_by_team[0], 5)

    def test_determine_deals_5_cards_to_each_player(self):
        state = EuchreGame.initial_state()
        state = EuchreGame.determine(state)
        self.assertTrue(all(len(hand) == 5 for hand in state.hands))
