var socket = new WebSocket('ws://' + location.hostname + (location.port ? (':' + location.port) : ''));

function valueLookup(value) {
  if (value === '0') {
    return '10';
  }
  return value;
}

var suitLookup = {
  'c': 'clubs',
  'd': 'diams',
  'h': 'hearts',
  's': 'spades',
};

var Card = React.createClass({
  sendCard: function() {
    socket.send(this.props.serverId);
  },
  value: function() {
    return valueLookup(this.props.serverId[0]);
  },
  suit: function() {
    return suitLookup[this.props.serverId[1]];
  },
  render: function() {
    return <div className={"card rank-" + this.value() + " " + this.suit()} onClick={this.sendCard}>
      <span className="rank">{this.value().toUpperCase()}</span>
      <span className="suit" dangerouslySetInnerHTML={{__html: '&' + this.suit()  + ';'}}></span>
    </div>
  }
});

var Hand = React.createClass({
  render: function() {
    return <ul className="hand">
      {this.props.cards.map(function(card) {return <Card key={card} serverId={card}/>;})}
    </ul>
  }
});

var Table = React.createClass({
  getInitialState: function() {
    return {hand: [], playedCards: [], trump: '', tricksWonByTeam: [], children: ''};
  },
  componentDidMount: function() {
    socket.onmessage = function(event) {
      var data = JSON.parse(event.data);
      console.log(data);
      if (data.error) {
        alert(data.error);
        return;
      }
      var hand = data.hands[0];
      this.setState({hand: hand, playedCards: data.table, trump: suitLookup[data.state.trump], tricksWonByTeam:data.state.tricks_won_by_team, children: JSON.stringify(data.children)});
    }.bind(this);
  },
  render: function() {
    return <div><Hand cards={this.state.hand}/>
    {this.state.playedCards.map(function(card) {return card ? <Card key={card} serverId={card}/> : '';})}
    <div>trump: <span classname="suit" dangerouslySetInnerHTML={{__html: this.state.trump ? '&' + this.state.trump  + ';' : ''}}></span>
    </div>
    <div>tricks won by team: {this.state.tricksWonByTeam.join(',')}</div>
    <div>{this.state.children}</div>
    </div>;
  }
});

ReactDOM.render(
  <Table/>,
  document.getElementById('app')
);
