import unittest

from test.fourcity import (
    valid_purchases, valid_builds, tiles,
    tile_for_player_count, Park, Tower, score_board,
    Shop, Factory, Harbor, Service, THROW_OUT, find_best_resource_allocation,
    FourCityGame
)


class TestFourCityGame(unittest.TestCase):
    def test_valid_purchases(self):
        ______ = None
        _arch_ = 'occupied'
        _urba_ = 'urbanist'

        bid_board = [
            [______, _arch_, ______, ______, ______, ______, ______],
            [______, ______, ______, ______, ______, ______, ______],
            [______, ______, ______, ______, ______, ______, ______],
            [______, ______, ______, ______, ______, ______, ______],
            [______, ______, ______, ______, _urba_, ______, ______],
            [______, ______, ______, ______, ______, ______, ______],
            [______, ______, ______, ______, ______, ______, ______],
        ]

        self.assertEqual(valid_purchases(bid_board, (4, 4)),
                         [(0, 2), (0, 3), (0, 5), (6, 1), (6, 2),
                          (6, 3), (6, 5), (1, 0), (2, 0), (3, 0),
                          (5, 0), (1, 6), (2, 6), (3, 6), (5, 6)])

        bid_board = [
            [______, _arch_, ______, ______, ______, ______, ______],
            [_arch_, ______, ______, ______, ______, ______, ______],
            [______, _urba_, ______, ______, ______, ______, ______],
            [______, ______, ______, ______, ______, ______, ______],
            [______, ______, ______, ______, ______, ______, ______],
            [______, ______, ______, ______, ______, ______, ______],
            [______, ______, ______, ______, ______, ______, ______],
        ]

        self.assertEqual(valid_purchases(bid_board, (2, 1)),
                         [(0, 2), (0, 3), (0, 4), (0, 5), (6, 2),
                          (6, 3), (6, 4), (6, 5), (3, 0), (4, 0),
                          (5, 0), (1, 6), (3, 6), (4, 6), (5, 6)])

    def test_build(self):
        city_board = [[None] * 4 for _ in range(4)]
        heights = [[0] * 4 for _ in range(4)]
        self.assertEqual(valid_builds(city_board, heights, Tower(), 3),
                         [THROW_OUT, (0, 2), (1, 2), (2, 0), (2, 1),
                         (2, 2), (2, 3), (3, 2)])
        city_board = [[None] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                city_board[x][y] = Park()
        city_board[3][2] = Tower()
        heights[3][2] = 2
        self.assertEqual(valid_builds(city_board, heights, Tower(), 3),
                         [THROW_OUT, (3, 2)])
        self.assertEqual(valid_builds(city_board, heights, Tower(), 4),
                         [THROW_OUT, (3, 2)])
        self.assertEqual(valid_builds(city_board, heights, Park(), 3),
                         [THROW_OUT])
        self.assertEqual(valid_builds(city_board, heights, Park(), 2),
                         [THROW_OUT])

    def test_tiles(self):
        self.assertEqual([25] * 4, [len(round) for round in tiles])

        def tiles_for_player_count(player_count, tiles):
            return len(list(filter(
                lambda tile: tile_for_player_count(player_count, tile),
                round)))

        tiles_per_player_per_round = []

        self.assertTrue(tile_for_player_count(2, tiles[0][0]))
        self.assertFalse(tile_for_player_count(2, tiles[0][1]))
        self.assertFalse(tile_for_player_count(2, tiles[0][4]))

        for round in tiles:
            tiles_per_player_per_round.append({
                2: tiles_for_player_count(2, round),
                3: tiles_for_player_count(3, round),
                4: tiles_for_player_count(4, round),
            })
        self.assertEqual(tiles_per_player_per_round[0],
                         {2: 16, 3: 20, 4: 25})
        self.assertEqual(tiles_per_player_per_round[1],
                         {2: 16, 3: 20, 4: 25})
        self.assertEqual(tiles_per_player_per_round[2],
                         {2: 16, 3: 20, 4: 25})
        self.assertEqual(tiles_per_player_per_round[3],
                         {2: 16, 3: 20, 4: 25})

    def test_scoring(self):
        heights = [[0] * 4 for _ in range(4)]
        ______ = None
        _park_ = Park()
        tower_ = Tower()
        player_board = [
            [______, _park_, ______, ______],
            [______, ______, ______, ______],
            [______, ______, ______, ______],
            [______, ______, ______, ______],
        ]
        self.assertEqual(score_board(player_board, heights, 0), 0)

        player_board = [
            [tower_, _park_, ______, ______],
            [______, ______, ______, ______],
            [______, ______, ______, ______],
            [______, ______, ______, ______],
        ]

        heights[0][0] = 1

        self.assertEqual(score_board(player_board, heights, 0), 3)

        player_board = [
            [tower_, _park_, tower_, ______],
            [______, ______, ______, ______],
            [______, ______, ______, ______],
            [______, ______, ______, ______],
        ]
        heights[0][2] = 1
        self.assertEqual(score_board(player_board, heights, 0), 6)

        player_board = [
            [tower_, ______, tower_, ______],
            [tower_, _park_, tower_, ______],
            [______, tower_, ______, ______],
            [______, ______, ______, ______],
        ]
        heights[1][0] = 1
        heights[1][2] = 1
        heights[2][1] = 1
        self.assertEqual(score_board(player_board, heights, 0), 12)

        player_board = [
            [tower_, tower_, tower_, ______],
            [tower_, _park_, tower_, ______],
            [______, tower_, ______, ______],
            [______, ______, ______, ______],
        ]
        heights[0][1] = 1
        self.assertEqual(score_board(player_board, heights, 0), 17)

        tower2 = Tower()
        tower3 = Tower()
        shop3_ = Shop(customers=3)
        shop4_ = Shop(customers=4)
        factry = Factory()
        harbor = Harbor()
        harbr3 = Harbor(points=3)
        harbr2 = Harbor(points=2)

        player_board = [
            [tower3, _park_, tower_, ______],
            [_park_, tower2, ______, ______],
            [harbor, shop3_, factry, shop4_],
            [harbr3, harbor, harbr2, factry],
        ]

        heights = [
            [3, 0, 1, 0],
            [0, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]

        self.assertEqual(score_board(player_board, heights, 0), 59)

        serv__ = Service()
        serv_1 = Service(points=1)
        serv_2 = Service(points=2)

        player_board = [
            [serv_2, tower_, serv_1, harbor],
            [tower_, _park_, tower2, harbor],
            [_park_, tower_, _park_, harbr3],
            [______, serv_2, serv__, harbor],
        ]

        heights = [
            [0, 1, 0, 0],
            [1, 0, 2, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0]
        ]

        self.assertEqual(score_board(player_board, heights, 1), 58)

    def test_apply_move_increases_height_when_building_a_tower(self):
        state = FourCityGame.initial_state(2)
        self.assertEqual(state.city_board_heights[0][0][0], 0)
        state = state._replace(current_tile=Tower(),
                               current_architect=1)
        state = FourCityGame.apply_move(state, (0, 0))
        self.assertEqual(state.city_board_heights[0][0][0], 1)
        state = state._replace(current_tile=Tower(),
                               current_architect=1,
                               current_player=0)
        state = FourCityGame.apply_move(state, (0, 0))
        self.assertEqual(state.city_board_heights[0][0][0], 2)

    def test_scoring_picks_best_resource_allocation(self):
        ______ = None
        _park_ = Park()
        tower_ = Tower()
        heights = [[0] * 4 for _ in range(4)]

        board = [
            [tower_, _park_, tower_, ______],
            [______, ______, ______, ______],
            [______, ______, ______, ______],
            [______, ______, ______, ______],
        ]

        heights[0][0] = 1
        heights[0][2] = 4

        self.assertEqual(find_best_resource_allocation(board, heights,
                                                       people=0,
                                                       energy=1),
                         12)

        self.assertEqual(find_best_resource_allocation(board, heights,
                                                       people=0,
                                                       energy=2),
                         15)

        # the park will absorb the pollution
        self.assertEqual(find_best_resource_allocation(board, heights,
                                                       people=0,
                                                       energy=3),
                         15)

        # when there is no place to put the energy it takes away points
        self.assertEqual(find_best_resource_allocation(board, heights,
                                                       people=0,
                                                       energy=4),
                         14)
