from mittmcts import MCTS, Draw
from test.games import TicTacToeGame


def main():
    state = TicTacToeGame.initial_state()
    while True:
        if state.winner:
            TicTacToeGame.print_board(state)
            if state.winner is Draw:
                print 'Draw!'
            elif state.winner:
                print state.winner + ' wins'
            break
        if state.current_player == 'O':
            while True:
                TicTacToeGame.print_board(state)
                try:
                    move = int(raw_input('Move:'))
                    state = TicTacToeGame.apply_move(state, move)
                    break
                except ValueError:
                    print 'That is not a legal move'
        else:
            result = (MCTS(TicTacToeGame, state)
                      .get_simulation_result(100))
            state = TicTacToeGame.apply_move(state, result.move)


if __name__ == '__main__':
    main()
