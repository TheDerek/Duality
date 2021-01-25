import React from "react";
import {connect} from "react-redux";

import { startGame } from "./actions";
import Errors from "./Errors";

function Player(props) {
  let listClass = "list-group-item";
  let badge = null;

  if (props.currentPlayer) {
    listClass += " list-group-item-primary";
  }

  if (props.player.admin) {
    listClass += " d-flex justify-content-between align-items-center";
    badge = <span className="badge bg-primary rounded-pill">Admin</span>;
  }

  return (
    <li className={listClass}>
      { props.player.name }
      { badge }
    </li>
  )
}

class WaitingRoom extends React.Component {
  startGame = () => {
    this.props.startGame(this.props.gameCode);
    console.log("Start game button clicked")
  };

  render() {
    const canStartGame = this.props.currentPlayer.admin
      && this.props.players.length >= this.props.minimumPlayers;

    return (
      <div className="card mt-3">
        <div className="card-header">
          Waiting room
        </div>
        <div className="card-body">
          <Errors errors={this.props.errors}/>
          <h4 className="card-title">Duality</h4>
          <p className="card-text">
            The fun party game in which you test your friends knowledge and try
            to predict their responses!
          </p>
          <dl>
            <dt>Players</dt>
            <dd>3-10</dd>

            <dt>Average game time</dt>
            <dd>20 minutes</dd>
          </dl>
        </div>
        <ul className="list-group list-group-flush">
          <li className="list-group-item list-group-item-secondary">
            <b>Connected players</b>
          </li>
          {
            this.props.players.map((player, i) =>
              <Player key={i} player={player} currentPlayer = {player.name === this.props.currentPlayer.name}/>
            )
          }
        </ul>
        <div className="card-footer">
          <div className="d-grid">
            <button
              onClick={this.startGame}
              disabled={!canStartGame}
              className="btn btn-primary btn-block">
              Start Game
            </button>
          </div>
        </div>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {
    errors: state.errors,
    players: state.players,
    gameCode: state.gameCode,
    admin: state.admin,
    currentPlayer: state.currentPlayer,
    minimumPlayers: state.minimumPlayers
  }
}

const mapDispatchToProps = {
  startGame
};

export default connect(mapStateToProps, mapDispatchToProps)(WaitingRoom);
