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
    if (this.props.serverId === 'back') {
      return <div className="card back"/>;
    }
    return <div data-hint={this.props.node ? this.props.node.visits : ''} className={"hint--top hint--always card rank-" + this.value() + " " + this.suit()} onClick={this.sendCard}>
      <span className="rank">{this.value().toUpperCase()}</span>
      <span className="suit" dangerouslySetInnerHTML={{__html: '&' + this.suit()  + ';'}}></span>
    </div>
  }
});

var Hand = React.createClass({
  getChildNode: function(card) {
    return this.props.children[card];
  },
  render: function() {
    var self = this;
    return <ul className="a-hand">
      {this.props.cards.map(function(card) {return <li><Card key={card} serverId={card} node={self.getChildNode(card)}/></li>;})}
    </ul>
  }
});

var Table = React.createClass({
  getInitialState: function() {
    return {hand: [], playedCards: [], trump: '', tricksWonByTeam: [], children: '', percentChanceOfWinning: null};
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
      this.setState({hand: hand,
                     playedCards: data.table,
                     trumpValue: valueLookup(data.state.trump_card[0]).toUpperCase(),
                     trumpSuit: suitLookup[data.state.trump],
                     tricksWonByTeam: data.state.tricks_won_by_team,
                     children: data.children});
      if (typeof(data.overall_percent) !== 'undefined') {
        this.setState({percentChanceOfWinning: data.overall_percent});
      }
    }.bind(this);
  },
  getCard: function(index) {
    var card = this.state.playedCards[index];
    return card ? <Card key={index} serverId={card}/> : <Card key={index} serverId="back"/>;
  },
  render: function() {
    return <div>
      <div>trump: <span classname="suit" dangerouslySetInnerHTML={{__html: (this.state.trumpValue ? this.state.trumpValue : '') + (this.state.trumpSuit ? '&' + this.state.trumpSuit  + ';' : '')}}></span> tricks won by team: {this.state.tricksWonByTeam.join(',')} percent chance of winning: {this.state.percentChanceOfWinning}</div>
      <div className="table">{this.getCard(2)}</div>
      <div className="table">{this.getCard(1)} {this.getCard(3)}</div>
      <div className="table">{this.getCard(0)}</div>
      <Hand cards={this.state.hand} children={this.state.children}/>
    </div>;
  }
});

ReactDOM.render(
  <Table/>,
  document.getElementById('app')
);
