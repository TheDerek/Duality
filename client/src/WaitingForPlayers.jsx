import React from "react";
import {connect} from "react-redux";


function Player(props) {
  let classes = "list-group-item";

  if (props.player.currentPlayer) {
    classes += " list-group-item-secondary";
  }

  return (
    <li className={classes}>{ props.player.name }</li>
  )
}

function Players(props) {
  return (
      <ul className="list-group list-group-flush">
        { props.players.map((player, index) => (
          <Player key={index} player={player} />
        )) }
      </ul>
    )
}

function WaitingForPlayers(props) {
  return (
    <div>
      <h3 className="mb-4 text-center text-white">
        Waiting for players<br/>
      </h3>
      <div className="card-group mt-4">
        <div className="card">
          <div className="card-header">
            Waiting for
          </div>
          <Players players={ props.players.filter((player => !player.submissionFinished)) } />
        </div>
        <div className="card">
          <div className="card-header">
            Done
          </div>
          <Players players={ props.players.filter((player => player.submissionFinished)) } />
        </div>
      </div>
      </div>
  );
}

function mapStateToProps(state) {
  return {
    players: state.players,
    currentPlayer: state.currentPlayer
  }
}

const mapDispatchToProps = {

};

export default connect(mapStateToProps, mapDispatchToProps)(WaitingForPlayers);
