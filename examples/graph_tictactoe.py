from mittmcts import MCTS, flamegraph
from test.games import TicTacToeGame


def main():
    result = (MCTS(TicTacToeGame)
              .get_simulation_result(1000, get_leaf_nodes=True))
    flamegraph(result)


if __name__ == '__main__':
    main()
