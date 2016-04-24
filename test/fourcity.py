from collections import namedtuple
from itertools import groupby
from random import shuffle


THROW_OUT = 'throw-out'
TOWER = 0
FACTORY = 1
HARBOR = 2
SERVICE = 3
SHOP = 4
PARK = 5


Tile = namedtuple('Tile', ['type', 'people', 'points', 'players',
                           'pollution', 'customers', 'mayor'])
Tile.__new__.__defaults__ = (None, 0, 0, None, 0, 0, False)


def Tower(**kwargs):
    return Tile(type=TOWER, **kwargs)


def Factory(**kwargs):
    return Tile(type=FACTORY, **kwargs)


def Harbor(**kwargs):
    return Tile(type=HARBOR, **kwargs)


def Service(**kwargs):
    return Tile(type=SERVICE, **kwargs)


def Shop(**kwargs):
    return Tile(type=SHOP, **kwargs)


def Park(**kwargs):
    return Tile(type=PARK, **kwargs)


tiles = [
    [
        Tower(people=2),
        Tower(people=2, players=[4]),
        Tower(people=1, mayor=True),
        Tower(people=1),
        Tower(people=2, players=[3, 4]),
        Tower(people=1),
        Tower(people=3),
        Factory(pollution=3),
        Factory(pollution=2),
        Factory(pollution=1, players=[3, 4]),
        Factory(pollution=1),
        Harbor(people=2),
        Harbor(pollution=2),
        Harbor(people=1, pollution=1, players=[3, 4]),
        Harbor(points=1, players=[4]),
        Service(points=2),
        Service(points=0),
        Service(points=1, players=[4]),
        Service(points=1, players=[3, 4]),
        Shop(),
        Shop(),
        Shop(players=[4]),
        Park(),
        Park(),
        Park(players=[4]),
    ],
    [
        Tower(people=3),
        Tower(people=2),
        Tower(people=1, mayor=True),
        Tower(people=2, players=[3, 4]),
        Tower(people=2, players=[4]),
        Tower(people=1),
        Tower(people=1),
        Factory(pollution=3),
        Factory(pollution=2),
        Factory(pollution=2, players=[3, 4]),
        Factory(pollution=1),
        Harbor(pollution=1, people=1),
        Harbor(points=2),
        Harbor(people=2, players=[3, 4]),
        Harbor(pollution=1, people=1, players=[4]),
        Service(points=2),
        Service(),
        Service(points=1, players=[3, 4]),
        Service(points=1, players=[4]),
        Shop(),
        Shop(),
        Shop(players=[4]),
        Park(),
        Park(),
        Park(players=[4]),
    ],
    [
        Tower(people=3),
        Tower(people=2),
        Tower(people=1, mayor=True),
        Tower(people=1),
        Tower(people=2, players=[4]),
        Tower(people=2, players=[3, 4]),
        Factory(pollution=3),
        Factory(pollution=2),
        Factory(pollution=2, players=[3, 4]),
        Factory(pollution=1),
        Harbor(people=2),
        Harbor(points=2),
        Harbor(pollution=2, players=[3, 4]),
        Harbor(pollution=1, people=1, players=[4]),
        Service(points=2),
        Service(),
        Service(points=1, players=[3, 4]),
        Service(points=1, players=[4]),
        Shop(),
        Shop(),
        Shop(players=[4]),
        Park(),
        Park(),
        Park(),
        Park(players=[4])
    ],
    [
        Tower(people=3),
        Tower(people=2),
        Tower(people=1),
        Tower(people=2, players=[4]),
        Tower(people=1),
        Tower(people=2, players=[3, 4]),
        Factory(pollution=2),
        Factory(pollution=2, players=[3, 4]),
        Factory(pollution=1),
        Harbor(pollution=2),
        Harbor(pollution=3),
        Harbor(points=3),
        Harbor(pollution=1, people=1, players=[4]),
        Harbor(pollution=1, people=1),
        Harbor(people=2, players=[3, 4]),
        Service(points=2),
        Service(),
        Service(points=1, players=[3, 4]),
        Service(points=1, players=[4]),
        Shop(),
        Shop(),
        Shop(players=[4]),
        Park(),
        Park(),
        Park(players=[4]),
    ],
]


def tile_for_player_count(player_count, tile):
    return not tile.players or player_count in tile.players


# For reference this is what the bid_board looks like
#    [
#        [______, (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), ______],
#        [(1, 0), ______, ______, ______, ______, ______, (1, 6)],
#        [(2, 0), ______, ______, ______, ______, ______, (2, 6)],
#        [(3, 0), ______, ______, ______, ______, ______, (3, 6)],
#        [(4, 0), ______, ______, ______, ______, ______, (4, 6)],
#        [(5, 0), ______, ______, ______, ______, ______, (5, 6)],
#        [______, (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), ______],
#    ]


def get_legal_bid_moves():
    return ([(0, y) for y in range(1, 6)] +
            [(6, y) for y in range(1, 6)] +
            [(x, 0) for x in range(1, 6)] +
            [(x, 6) for x in range(1, 6)])


def get_legal_city_moves():
    return [(x, y)
            for x in range(6)
            for y in range(6)]


def valid_purchases(bid_board, urbanist_location):
    legal_moves = get_legal_bid_moves()
    legal_moves = filter(lambda spot: (
        (spot[1] != urbanist_location[1] and
         spot[0] != urbanist_location[0])
        and bid_board[spot[0]][spot[1]] is None),
        legal_moves)
    return legal_moves


def valid_builds(city_board, city_board_height, tile, architect):
    # all the boards are 0 - 3 but the architects are 1 - 4
    architect -= 1
    # you "may" place the piece you take
    # so you can discard it if you want
    moves = [THROW_OUT]
    for x in range(4):
        for y in range(4):
            if (((x == architect or y == architect)
                 and city_board[x][y] is None)
                or (city_board[x][y] and city_board[x][y].type == TOWER and
                    city_board_height[x][y] == architect
                    and tile.type == TOWER)):
                moves.append((x, y))
    return moves


def adjacent_iterator(city_board):
    zones = [
        [0, 0, 1, 1],
        [0, 0, 1, 1],
        [2, 2, 3, 3],
        [2, 2, 3, 3]
    ]
    for x in range(4):
        for y in range(4):
            yield (x, y, city_board[x][y],
                   [city_board[xd][yd]
                    for xd, yd in [(x - 1, y), (x + 1, y),
                                   (x, y - 1), (x, y + 1)]
                    if xd >= 0 and xd <= 3 and yd >= 0 and yd <= 3],
                   zones[x][y])


def get_longest_harbors(city_board):
    widest = 0
    tallest = 0
    for i in range(4):
        harbors = [tile and tile.type == HARBOR for tile in city_board[i]]
        widest = max(widest,
                     max(sum(x and 1 or 0 for x in l)
                         for n, l in groupby(harbors)))
        harbors = [tile and tile.type == HARBOR for tile in [city_board[0][i],
                                                             city_board[1][i],
                                                             city_board[2][i],
                                                             city_board[3][i]]]
        tallest = max(tallest,
                      max(sum(x and 1 or 0 for x in l)
                          for n, l in groupby(harbors)))
    return tallest, widest


harbor_scores = {1: 0, 2: 3, 3: 7, 4: 12}
park_scores = {1: 2, 2: 4, 3: 7, 4: 11}
service_scores = {1: 2, 2: 5, 3: 9, 4: 14}
shop_scores = {1: 1, 2: 2, 3: 4, 4: 7}
tower_scores = {1: 1, 2: 3, 3: 6, 4: 10}


def score_board(city_board, city_board_heights, unused_pieces):
    score = 0
    seen_service = [0] * 4
    for x, y, tile, adjacent_tiles, zone in adjacent_iterator(city_board):
        if not tile:
            continue
        if tile.type == TOWER:
            score += tower_scores[city_board_heights[x][y]]
        elif tile.type == PARK:
            score += park_scores.get(
                len([adjacent_tile for adjacent_tile in adjacent_tiles
                     if adjacent_tile and adjacent_tile.type == TOWER]),
                0)
        elif tile.type == FACTORY:
            for adjacent_tile in adjacent_tiles:
                if not adjacent_tile:
                    continue
                if adjacent_tile.type == SHOP:
                    score += 2
                if adjacent_tile.type == HARBOR:
                    score += 3
        elif tile.type == SHOP:
            score += shop_scores.get(tile.customers, 0)
        elif tile.type == SERVICE:
            seen_service[zone] = 1

        score += tile.points

    score += service_scores.get(sum(seen_service), 0)
    for length in get_longest_harbors(city_board):
        score += harbor_scores.get(length, 0)

    score -= unused_pieces

    return score


class FourCityGame(object):
    """A game not in any way related to Quadropolis"""

    State = namedtuple('FourCityGameState',
                       ['construction_site',
                        'city_boards',
                        'city_board_heights',
                        'current_player',
                        'current_architect',
                        'urbanist_location',
                        'current_tile',
                        'architects_by_player',
                        'energy_by_player',
                        'people_by_player',
                        'remaining_tiles'])

    @classmethod
    def initial_state(cls, players):
        return cls.State(construction_site=[[None for _ in range(7)]
                                            for _ in range(7)],
                         city_boards=[[[None for _ in range(4)]
                                       for _ in range(4)]
                                      for _ in range(players)],
                         city_board_heights=[[[0 for _ in range(4)]
                                              for _ in range(4)]
                                             for _ in range(players)],
                         current_tile=None,
                         current_architect=None,
                         urbanist_location=None,
                         energy_by_player=[0 for _ in range(players)],
                         people_by_player=[0 for _ in range(players)],
                         current_player=0,
                         architects_by_player=[range(1, 5)
                                               for _ in range(players)],
                         remaining_tiles=None)

    @classmethod
    def apply_move(cls, state, move):
        construction_site = state.construction_site
        city_boards = state.city_boards
        city_board_heights = state.city_board_heights
        current_tile = state.current_tile
        current_architect = state.current_architect
        urbanist_location = state.urbanist_location
        current_player = state.current_player
        energy_by_player = state.energy_by_player[:]
        people_by_player = state.people_by_player[:]
        architects_by_player = state.architects_by_player[:]

        return cls.State(construction_site=construction_site,
                         city_boards=city_boards,
                         city_board_heights=city_board_heights,
                         current_tile=current_tile,
                         current_architect=current_architect,
                         urbanist_location=urbanist_location,
                         current_player=current_player,
                         energy_by_player=energy_by_player,
                         people_by_player=people_by_player,
                         architects_by_player=architects_by_player)

    @staticmethod
    def get_moves(state):
        if state.current_tile:
            return (False,
                    valid_builds(
                        state.city_boards[state.current_player],
                        state.city_board_heights[state.current_player],
                        state.current_tile,
                        state.current_architect))
        else:
            purchases = valid_purchases(state.construction_site,
                                        state.urbanist_location)
            architects = state.architects_by_player[state.current_player]
            return (False,
                    [(architect, x, y)
                     for architect in architects
                     for x, y in purchases])

    @staticmethod
    def determine(state):
        if state.remaining_tiles is None:
            remaining_tiles = [round[:] for round in tiles]
            for round in remaining_tiles:
                shuffle(round)

        return state._replace(remaining_tiles=remaining_tiles,
                              )

    @staticmethod
    def get_winner(state):
        return state.winning_team

    @staticmethod
    def current_player(state):
        return state.current_player
