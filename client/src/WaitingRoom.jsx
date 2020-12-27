import React from "react";
import {connect} from "react-redux";
import {createGame, joinGame, reportLobbyStatus} from "./actions";

function Player(props) {
  let listClass = "list-group-item";
  let badge = null;

  if (props.player.currentPlayer) {
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
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div className="container-sm">
        <div className="card mt-3">
          <div className="card-header">
            <div className="float-start">
              Waiting room
            </div>
            <div className="float-end">
              <em className="text-right">Game code: {this.props.gameCode}</em>
            </div>
            <div className="clearfix"/>
          </div>
          <div className="card-body">
            <h4 className="card-title">In the know</h4>
            <p className="card-text">
              The fun party game in which you test your friends knowledge and try
              to predict their responses!
            </p>
          </div>
          {/*<div className="card-header">Conencted Players</div>*/}
          <ul className="list-group list-group-flush">
            <li className="list-group-item list-group-item-secondary">
              <b>Connected players</b>
            </li>
            {
              this.props.players.map((player, i) =>
                <Player key={i} player={player}/>
              )
            }
          </ul>
          <div className="card-footer">
            <div className="d-grid">
              <button
                disabled={!this.props.currentPlayer.admin}
                className="btn btn-primary btn-block">
                Start Game
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {
    players: state.waitingRoom.players,
    gameCode: state.waitingRoom.gameCode,
    admin: state.waitingRoom.admin,
    currentPlayer: state.currentPlayer
  }
}

const mapDispatchToProps = {

};

export default connect(mapStateToProps, mapDispatchToProps)(WaitingRoom);