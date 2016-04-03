from collections import namedtuple
from random import shuffle, choice
from itertools import chain

from constraint import AllDifferentConstraint, Problem

from six import iteritems
from six.moves import filter, range


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


team = {
    0: 0,
    1: 1,
    2: 0,
    3: 1
}


same_color = {
    'd': 'h',
    'h': 'd',
    'c': 's',
    's': 'c'
}


suits = ['d', 'h', 's', 'c']


def deal():
    return [value + suit
            for suit in suits
            for value in ['a', 'k', 'q', 'j', '0', '9']]


def jack_of_trump(trump):
    return 'j' + trump


def second_highest_jack(trump):
    return 'j' + same_color[trump]


def value(card):
    return {
        '9': 9,
        '0': 10,
        'j': 11,
        'q': 12,
        'k': 13,
        'a': 14
    }[card[0]]


def sort_by_trump_and_lead(trump, lead_suit, cards):
    return sorted(cards,
                  key=lambda c: (c == jack_of_trump(trump),
                                 c == second_highest_jack(trump),
                                 suit(trump, c) == trump,
                                 suit(trump, c) == lead_suit,
                                 value(c)),
                  reverse=True)


def winning_card(trump, lead_suit, cards):
    return sort_by_trump_and_lead(trump, lead_suit, cards)[0]


def suit(trump, card):
    if card == second_highest_jack(trump):
        return trump
    if card is not None:
        try:
            return card[1]
        except IndexError:
            return ValueError('Cards need to be two characters long')


def playable_cards(trump, lead_suit, hand):
    if lead_suit is None:
        return hand

    must_play = [card for card in hand
                 if suit(trump, card) == lead_suit]
    if must_play:
        return must_play

    return hand


def potential_cards_given_voids(trump, voids, cards):
    """During the simulation we will distribute cards to players and track
    when they have played off on a certain lead. This function returns the
    cards a player can select when they have played off on certain suits"""
    return [card for card in cards if suit(trump, card) not in voids]


class EuchreGame(object):
    """A simple trick-taking card game"""

    State = namedtuple('EuchreState',
                       ['hands',
                        'cards_played_by_player',
                        'current_player',
                        'lead_card',
                        'trump',
                        'trump_card',
                        'winning_team',
                        'tricks_won_by_team',
                        'cards_played',
                        'voids_by_player'])

    @classmethod
    def initial_state(cls, visible_hand=None, trump_card=None):
        all_cards = deal()
        if visible_hand is None:
            visible_hand = []
        for card in visible_hand:
            if card not in all_cards:
                raise ValueError('Invalid starting hand')
        if trump_card is None:
            trump_card = choice(all_cards)
        trump = trump_card[1]
        if trump not in suits:
            raise ValueError('Invalid trump suit')
        return cls.State(hands=[visible_hand, [], [], []],
                         cards_played_by_player=[None] * 4,
                         current_player=0,
                         lead_card=None,
                         trump=trump,
                         trump_card=trump_card,
                         winning_team=None,
                         tricks_won_by_team=[0, 0],
                         cards_played=[trump_card],
                         voids_by_player=[set(), set(), set(), set()])

    @classmethod
    def apply_move(cls, state, move):
        cards_played_by_player = state.cards_played_by_player[:]
        voids_by_player = state.voids_by_player
        hands = [hand[:] for hand in state.hands]
        tricks_won_by_team = state.tricks_won_by_team
        lead_card = state.lead_card
        cards_played = state.cards_played[:]

        if state.lead_card is None:
            lead_card = move

        lead_suit = suit(state.trump, lead_card)
        if (suit(state.trump, move) in
                state.voids_by_player[state.current_player]):
            raise ValueError('Did not follow suit voids_by_player=%r move=%r '
                             'hand=%r' % (state.voids_by_player, move,
                                          state.hands[state.current_player]))

        if (state.lead_card and move not in
                playable_cards(state.trump,
                               lead_suit,
                               state.hands[state.current_player])):
            raise ValueError('Cheating trump=%r lead=%r hand=%r move=%r' %
                             (state.trump,
                              lead_suit,
                              state.hands[state.current_player],
                              move))
        cards_played_by_player[state.current_player] = move
        cards_played.append(move)
        hands[state.current_player].remove(move)

        if lead_suit != suit(state.trump, move):
            voids_by_player = [set(x) for x in state.voids_by_player]
            voids_by_player[state.current_player].add(lead_suit)

        next_player = (state.current_player + 1) % 4

        number_of_cards_played = len(
            list(filter(None, cards_played_by_player)))

        if number_of_cards_played == 4:
            winner = winning_card(state.trump,
                                  lead_suit,
                                  cards_played_by_player)
            winning_player = cards_played_by_player.index(winner)
            tricks_won_by_team = tricks_won_by_team[:]
            winning_team = team[winning_player]
            tricks_won_by_team[winning_team] = (
                tricks_won_by_team[winning_team] + 1)

            # reset the state for a new trick
            next_player = winning_player
            cards_played = cards_played[:]
            cards_played_by_player = [None] * 4
            lead_card = None

        winning_team = None
        if sum(tricks_won_by_team) == 5:
            if tricks_won_by_team[0] > tricks_won_by_team[1]:
                winning_team = 0
            else:
                winning_team = 1

        return cls.State(hands=hands,
                         cards_played_by_player=cards_played_by_player,
                         current_player=next_player,
                         lead_card=lead_card,
                         winning_team=winning_team,
                         trump=state.trump,
                         trump_card=state.trump_card,
                         tricks_won_by_team=tricks_won_by_team,
                         cards_played=cards_played,
                         voids_by_player=voids_by_player)

    @staticmethod
    def get_moves(state):
        return (False,
                playable_cards(state.trump,
                               suit(state.trump, state.lead_card),
                               state.hands[state.current_player]))

    @staticmethod
    def determine(state):
        card_played_this_round = [card is not None and 1 or 0
                                  for card in state.cards_played_by_player]
        remaining_hand_size = 5 - sum(state.tricks_won_by_team)
        hand_size_by_player = [remaining_hand_size - played
                               for played in card_played_this_round]
        cards = list(set(deal()) -
                     set(list(chain(*state.hands))) -
                     set(state.cards_played))
        shuffle(cards)

        problem = Problem()
        for player in range(4):
            if state.hands[player]:
                for card_index, card in enumerate(state.hands[player]):
                    problem.addVariable('p{}{}'.format(player, card_index),
                                        [card])
            else:
                voids_by_player = state.voids_by_player[player]
                for card_index in range(hand_size_by_player[player]):
                    variable_name = 'p{}{}'.format(player, card_index)
                    if voids_by_player:
                        potential_cards = potential_cards_given_voids(
                            state.trump, voids_by_player, cards)
                        shuffle(potential_cards)
                        problem.addVariable(variable_name, potential_cards)
                    else:
                        problem.addVariable(variable_name, cards)
        problem.addConstraint(AllDifferentConstraint())

        cards = sorted(iteritems(problem.getSolution()))
        hands = [[], [], [], []]
        for player in range(4):
            hands[player] = [c[1] for c in cards[:hand_size_by_player[player]]]
            del cards[:hand_size_by_player[player]]

        state = state._replace(hands=hands)
        return state

    @staticmethod
    def get_winner(state):
        return state.winning_team

    @staticmethod
    def current_player(state):
        return team[state.current_player]

    @staticmethod
    def print_board(state):
        print('lead_suit=%r trump=%r cards_played_by_player=%r\nhands=%r' % (
            state.lead_card and suit(state.trump, state.lead_card) or '?',
            state.trump,
            state.cards_played_by_player,
            state.hands))
        print('')
