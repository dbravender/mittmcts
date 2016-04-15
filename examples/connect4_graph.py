from mittmcts import MCTS, flamegraph
from test.connect4 import ConnectFourGame


def main():
    result = (MCTS(ConnectFourGame)
              .get_simulation_result(1000, get_leaf_nodes=True))
    flamegraph(result)


if __name__ == '__main__':
    main()
