[![Circle CI](https://circleci.com/gh/dbravender/mittmcts.svg?style=svg)](https://circleci.com/gh/dbravender/mittmcts)

# Man In The Table (Information Set) Monte Carlo Tree Search

This library is hopefully an easy-to-understand implementation of Information Set Monte Carlo Tree search written in Python.

The mascot of this project is [the Turk](https://en.wikipedia.org/wiki/The_Turk):

<p align="center">
<img src="/the-turk.jpg">
</p>

## Features

* An easy-to-understand simple implementation of MCTS/ISMCTS so others can see how it works
* Aid board game designers by giving them information about their games that make the game match their criteria of a fun game e.g.:
  * tree depth report - how many moves on average does a game take to complete - is my game too long or short?
  * custom evaluation functions so other metrics can be tracked

## How to add a game

Implement a class with the following classmethods:

* `initial_state()` - returns the initial state of a game
* `apply_move(state, move)` - returns a copy of state with the move applied - you are responsible for ensuring that if there is structural sharing it is done in a way that mutable changes to game state don't accidentally affect other nodes (when in doubt deepcopy the whole state - if you want to optimize for memory you only need to copy parts of the state that changed)
* `get_moves(state)` - return a list of moves (that are passed back into apply_move when they are selected)
* `get_winner(state)` - returns `None` if no one won, the player that won or `Draw` if there was a tie
* `current_player(state)` - returns the current player

Optional methods:

* `print_board(state)` - prints the board for the given state
* `determine(state)` - if this is defined it randomly selects possible moves a player could play given their play history (so in a trick taking game if they haven't followed a particular suit when it was lead then they can't possibly have that suit - see the Euchre example in the tests directory)

## Future

* More aids for board game designers:
  * lead changes - presumably the more often this happens the more engaged players are
  * is there a dominant strategy that always seems to win or do a variety of strategies win? (could be determined by counting occurrences of certain moves or abilities that players collected in leaf nodes)
  * should a particular ability be nerfed or made non-exclusive (i.e. if players end up with it do they win most games)?
  * branching factor report - can help with analysis paralysis detection - does my game offer too many choices to players on every turn?
