var socket = new WebSocket('ws://' + location.hostname + (location.port ? (':' + location.port) : ''));

var Token = React.createClass({
  onClick: function() {
    socket.send(this.props.column);
  },
  render: function() {
    return <div onClick={this.onClick.bind(this)} className={'token ' + (this.props.player !== null ? ('player' + this.props.player) : '')} style={this.props.node && this.props.player === null ? ({'opacity': + this.props.node.visits / 1000}): {} }></div>;
  }
});

var Row = React.createClass({
  getNode: function(column) {
    if (typeof(this.props.children[column]) !== 'undefined') {
      return this.props.children[column];
    }
  },
  render: function() {
    var cells = null;
    if (this.props.cells) {
      cells = this.props.cells.map((player, column) => <td><Token player={player} column={column} node={this.getNode(column)}/></td>);
    }
    return <tr>{cells}</tr>;
  }
});

var Board = React.createClass({
  getInitialState: function() {
    return {board: [], percentChanceOfWinning: null};
  },
  componentDidMount: function() {
    socket.onmessage = function(event) {
      var data = JSON.parse(event.data);
      console.log(data);
      if (data.error) {
        alert(data.error);
        return;
      }
      this.setState({board: data.state.board,
                     children: data.children});
      if (typeof(data.overall_percent) !== 'undefined') {
        this.setState({percentChanceOfWinning: data.overall_percent});
      }
      if (data.state.winner !== null) {
        alert(data.state.winner);
      }
    }.bind(this);
  },
  render: function() {
    var rows = null;
    if (this.state.board) {
      rows = this.state.board.map((row) => <Row cells={row} children={this.state.children}/>);
    }
    return  <table>
      {rows}
    </table>;
  }
});

ReactDOM.render(
  <Board/>,
  document.getElementById('app')
);
