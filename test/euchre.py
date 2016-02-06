from collections import namedtuple
from copy import deepcopy
from random import shuffle, choice

from mittmcts import ImpossibleState


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
        return card[1]


def playable_cards(trump, lead_suit, hand):
    must_play = [card for card in hand
                 if suit(trump, card) == lead_suit]
    if must_play:
        return must_play
    return hand


def potential_cards_given_voids(trump, voids, cards):
    """During the simulation we will distribute cards to players and track
    when they have played off on a certain lead. This function returns the
    cards a player can select when they have played off on certain suits and
    raises an ImpossibleState exception when there are no cards left that they
    could legally play"""
    cards = [card for card in cards if suit(trump, card) not in voids]
    if not cards:
        raise ImpossibleState('No cards that can be played')
    return cards


class EuchreGame(object):
    """A simple trick-taking card game"""

    State = namedtuple('EuchreState', 'cards_played_by_player,'
                                      'current_player,'
                                      'lead_card,'
                                      'trump,'
                                      'winning_team,'
                                      'visible_hand,'
                                      'remaining_cards,'
                                      'tricks_won_by_team,'
                                      'voids_by_player')

    @classmethod
    def initial_state(cls, visible_hand=None, trump=None):
        all_cards = deal()
        if not visible_hand:
            visible_hand = deal()
            shuffle(visible_hand)
            visible_hand = visible_hand[:5]
        if len(visible_hand) != 5:
            raise ValueError('visible_hand should have 5 cards')
        for card in visible_hand:
            if card not in all_cards:
                raise ValueError('Invalid card in visible hand')
        remaining_cards = list(set(all_cards) - set(visible_hand))
        if trump is None:
            trump = choice(suits)
        if trump not in suits:
            raise ValueError('Invalid trump suit')
        return cls.State(remaining_cards=remaining_cards,
                         visible_hand=visible_hand,
                         cards_played_by_player=[None] * 4,
                         current_player=0,
                         lead_card=None,
                         winning_team=None,
                         trump=trump,
                         tricks_won_by_team=[0, 0],
                         voids_by_player=[set(), set(), set(), set()])

    @classmethod
    def apply_move(cls, state, move):
        cards_played_by_player = deepcopy(state.cards_played_by_player)
        voids_by_player = state.voids_by_player
        remaining_cards = deepcopy(state.remaining_cards)
        visible_hand = state.visible_hand
        tricks_won_by_team = state.tricks_won_by_team
        lead_card = state.lead_card

        if state.lead_card is None:
            lead_card = move

        lead_suit = suit(state.trump, lead_card)

        cards_played_by_player[state.current_player] = move
        if state.current_player == 0:
            visible_hand = deepcopy(state.visible_hand)
            if (state.lead_card and move not in
                    playable_cards(state.trump,
                                   lead_suit,
                                   visible_hand)):
                raise ValueError('Cheating')
            visible_hand.remove(move)
        else:
            remaining_cards.remove(move)

        if lead_suit != suit(state.trump, move):
            voids_by_player = deepcopy(state.voids_by_player)
            voids_by_player[state.current_player].add(lead_suit)

        next_player = (state.current_player + 1) % 4

        number_of_cards_played = len(filter(None, cards_played_by_player))

        if number_of_cards_played == 4:
            winner = winning_card(state.trump,
                                  lead_suit,
                                  cards_played_by_player)
            winning_player = cards_played_by_player.index(winner)
            tricks_won_by_team = deepcopy(tricks_won_by_team)
            winning_team = team[winning_player]
            tricks_won_by_team[winning_team] = (
                tricks_won_by_team[winning_team] + 1)

            # reset the state for a new trick
            next_player = winning_player
            cards_played_by_player = [None] * 4
            lead_card = None

        winning_team = None
        if (len(remaining_cards) + len(visible_hand)) == 4:
            # all the cards left are in the kitty
            if tricks_won_by_team[0] > tricks_won_by_team[1]:
                winning_team = 0
            else:
                winning_team = 1

        return cls.State(remaining_cards=remaining_cards,
                         visible_hand=visible_hand,
                         cards_played_by_player=cards_played_by_player,
                         current_player=next_player,
                         lead_card=lead_card,
                         winning_team=winning_team,
                         trump=state.trump,
                         tricks_won_by_team=tricks_won_by_team,
                         voids_by_player=voids_by_player)

    @classmethod
    def get_moves(cls, state):
        if state.current_player == 0:
            return (False,
                    playable_cards(state.trump,
                                   suit(state.trump, state.lead_card),
                                   state.visible_hand))
        else:
            return (False, potential_cards_given_voids(
                state.trump, state.voids_by_player[state.current_player],
                state.remaining_cards))

    @classmethod
    def determine(cls, state):
        # This could be made more efficient by properly detecting impossible
        # distributions of cards sooner rather than waiting for
        # potential_cards_given_voids to raise ImpossibleState later
        cards_remaining_in_hand = 5 - sum(state.tricks_won_by_team)
        if state.current_player == 0:
            return state.visible_hand
        return potential_cards_given_voids(
            state.trump, state.voids_by_player[state.current_player],
            state.remaining_cards)[:cards_remaining_in_hand]

    @classmethod
    def get_winner(cls, state):
        return state.winning_team

    @classmethod
    def current_player(cls, state):
        return team[state.current_player]

    @classmethod
    def print_board(cls, state):
        print 'lead_suit=%r trump=%r hand=%r' % (
            state.lead_card and suit(state.trump, state.lead_card) or '?',
            state.trump,
            state.visible_hand)
        for player, card in enumerate(state.cards_played_by_player):
            print '%d %s' % (player, card),
        print
