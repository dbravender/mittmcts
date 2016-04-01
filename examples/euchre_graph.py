from mittmcts import MCTS, flamegraph
from test.euchre import EuchreGame


def main():
    state = EuchreGame.initial_state(['ad', '0d', 'kd', '0s', '9s'], trump='d')
    result = (MCTS(EuchreGame, state)
              .get_simulation_result(1000, get_leaf_nodes=True))
    flamegraph(result)


if __name__ == '__main__':
    main()
