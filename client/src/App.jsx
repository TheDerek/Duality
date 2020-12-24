import React from 'react';
import {connect} from "react-redux";

import Lobby from "./Lobby";
import WaitingRoom from "./WaitingRoom";

export const GAME_STATES = {
  LOBBY: "LOBBY",
  WAITING_ROOM: "WAITING_ROOM"
};

class App extends React.Component {
  #gameStates = {
    [GAME_STATES.LOBBY]: <Lobby/>,
    [GAME_STATES.WAITING_ROOM]: <WaitingRoom/>
  };

  constructor(props) {
    super(props)
  }

  getGameState() {
    return this.#gameStates[this.props.gameState];
  }

  render() {
    return this.getGameState();
  }
}

function mapStateToProps(state) {
  return {
    gameState: state.gameState
  }
}

export default connect(mapStateToProps)(App);