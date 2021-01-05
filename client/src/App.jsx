import React from 'react';
import {connect} from "react-redux";

import Lobby from "./Lobby";
import WaitingRoom from "./WaitingRoom";
import SubmitPrompts from "./SubmitPrompts";
import DrawPrompts from "./DrawPrompts";
import WaitingForPlayers from "./WaitingForPlayers";
import DisplayResults from "./DisplayResults";

export const GAME_STATES = {
  LOBBY: "LOBBY",
  WAITING_ROOM: "WAITING_ROOM",
  SUBMIT_ATTRIBUTES: "SUBMIT_ATTRIBUTES",
  DRAW_PROMPTS: "DRAW_PROMPTS",
  WAITING_FOR_PLAYERS: "WAITING_FOR_PLAYERS",
  DISPLAY_RESULTS: "DISPLAY_RESULTS"
};

class App extends React.Component {
  #gameStates = {
    [GAME_STATES.LOBBY]: <Lobby/>,
    [GAME_STATES.WAITING_ROOM]: <WaitingRoom/>,
    [GAME_STATES.SUBMIT_ATTRIBUTES]: <SubmitPrompts/>,
    [GAME_STATES.DRAW_PROMPTS]: <DrawPrompts/>,
    [GAME_STATES.WAITING_FOR_PLAYERS]: <WaitingForPlayers/>,
    [GAME_STATES.DISPLAY_RESULTS]: <DisplayResults/>,
  };

  getGameState() {
    return this.#gameStates[this.props.gameState];
  }

  getGameCode() {
    if (!this.props.gameCode) {
      return null;
    }

    return (
      <div className="d-flex">
        <div className="text-right">
          <em>Game Code: { this.props.gameCode }</em>
        </div>
      </div>
    );
  }

  render() {
    return (
      <div>
        <nav className="navbar navbar-light bg-light mb-4">
          <div className="container-fluid game-container">
            <span className="navbar-brand mb-0 h1">Supervillain Smackdown</span>
            { this.getGameCode() }
          </div>
        </nav>
        <div className="container-md game-container">
          { this.getGameState() }
        </div>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {
    gameState: state.gameState,
    gameCode: state.gameCode
  }
}

export default connect(mapStateToProps)(App);
