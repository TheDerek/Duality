import React from 'react';
import ReactDOM from 'react-dom'
import { createStore, applyMiddleware } from "redux";
import { Provider } from "react-redux";
import thunk from 'redux-thunk';
import reduxWebsocket from '@giantmachines/redux-websocket';
import { connect } from '@giantmachines/redux-websocket';

import './index.css'
import App from "./App"
import { GAME_STATES } from "./App";
import { GAME_STATUS, REPORT_STATUS } from "./actions";

export const LOCAL_STORAGE_PLAYER_NAME = "playerNameValue";
export const LOCAL_STORAGE_GAME_CODE = "gameCodeValue";
export const LOCAL_STORAGE_UUID = "uuid";

const WEBSOCKET_ADDRESS = 'ws://localhost:6789';

const initialState = {
  uuid: localStorage.getItem(LOCAL_STORAGE_UUID),
  minimumPlayers: 3,
  gameState: GAME_STATES.LOBBY,
  presetLobbyFormValues: {
    name: localStorage.getItem(LOCAL_STORAGE_PLAYER_NAME) || "",
    gameCode: localStorage.getItem(LOCAL_STORAGE_GAME_CODE) || ""
  },
  players: [],
  errors: [],
  gameCode: "",
  admin: false,
  currentPlayer: null,
  promptSubmissionNumber: 1,
  status: GAME_STATUS.NORMAL
};

function messageReducer(state, name, data) {
  switch(name) {
    case "error": {
      console.error(data);
      return {
          ...state,
          status: GAME_STATUS.ERRORED,
          errors: [data.userMessage]
        };
    }
    case "joinGame": {
      return {
        ...state,
        gameState: data.gameState,
        players: data.players,
        admin: data.admin,
        gameCode: data.gameCode,
        currentPlayer: data.currentPlayer
      };
    }
    case "playerJoinedGame": {
      return {
        ...state,
        gameState: GAME_STATES.WAITING_ROOM,
        players: [
          ...state.players,
          data.player
        ]
      };
    }
    case "updateGameState": {
      return {
        ...state,
        gameState: data.gameState
      };
    }
    default:
      return state;
  }
}

function reducer(state = initialState, action) {
  console.log('reducer', state, action);

  switch(action.type) {
    case 'REDUX_WEBSOCKET::MESSAGE':
      const data = JSON.parse(action.payload.message);
      const name = Object.keys(data)[0];
      console.log("Got data from websocket", data);

      return messageReducer(state, name, data[name]);
    case REPORT_STATUS:
      console.log("Setting lobby status");
      return {
        ...state,
        status: action.status,
        errors: action.errors
      };
    default:
      return state;
  }
}

const reduxWebsocketMiddleware = reduxWebsocket({
  reconnectOnClose: true,
});

const gameMiddleware = storeAPI => next => action => {
  // Save the players and game code for easy reconnecting
  if (action.type === "REDUX_WEBSOCKET::MESSAGE") {
    const data = JSON.parse(action.payload.message);
    const name = Object.keys(data)[0];

    if (name === "joinGame") {
      let current_player = data.joinGame.currentPlayer;

      localStorage.setItem(LOCAL_STORAGE_PLAYER_NAME, current_player.name);
      localStorage.setItem(LOCAL_STORAGE_GAME_CODE, data.joinGame.gameCode);
      localStorage.setItem(LOCAL_STORAGE_UUID, data.joinGame.uuid)
    }
  }

  return next(action);
};

const store = createStore(
  reducer,
  applyMiddleware(thunk, reduxWebsocketMiddleware, gameMiddleware)
);


store.dispatch(connect(WEBSOCKET_ADDRESS));

ReactDOM.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>,
  document.getElementById('root')
);
