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
import { LOBBY_STATUS, REPORT_LOBBY_STATUS} from "./actions";

export const LOCAL_STORAGE_PLAYER_NAME = "playerNameValue";
export const LOCAL_STORAGE_GAME_CODE = "gameCodeValue";
export const LOCAL_STORAGE_UUID = "uuid";

const WEBSOCKET_ADDRESS = 'ws://localhost:6789';

const initialState = {
  uuid: localStorage.getItem(LOCAL_STORAGE_UUID),
  minimumPlayers: 3,
  gameState: GAME_STATES.LOBBY,
  lobby: {
    status: LOBBY_STATUS.NORMAL,
    errors: [],
    presetFormValues: {
      name: localStorage.getItem(LOCAL_STORAGE_PLAYER_NAME),
      gameCode: localStorage.getItem(LOCAL_STORAGE_GAME_CODE)
    }
  },
  players: [],
  gameCode: "",
  admin: false,
  currentPlayer: null
};

function messageReducer(state, name, data) {
  switch(name) {
    case "error": {
      if (data.type === "LOBBY_ERROR") {
        return {
          ...state,
          lobby: {
            status: LOBBY_STATUS.ERRORED,
            errors: [data.user_message]
          }
        };
      } else {
        console.error(data);
        return;
      }
    }
    case "joinGame": {
      return {
        ...state,
        gameState: GAME_STATES.WAITING_ROOM,
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
    default:
      return state;
  }
}

function reducer(state = initialState, action) {
  console.log('reducer', state, action);

  switch(action.type) {
    case REPORT_LOBBY_STATUS:
      console.log("Setting lobby status");
      return {
        ...state,
        lobby: {
          status: action.status,
          errors: action.errors
        }
      };
    case 'REDUX_WEBSOCKET::MESSAGE':
      const data = JSON.parse(action.payload.message);
      const name = Object.keys(data)[0];
      console.log("Got data from websocket", data);

      return messageReducer(state, name, data[name]);
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
      localStorage.setItem(LOCAL_STORAGE_UUID, current_player.uuid)
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
      <nav className="navbar navbar-light bg-light">
        <div className="container-fluid">
          <span className="navbar-brand mb-0 h1">Big Boss Battle</span>
        </div>
      </nav>
      <App />
    </Provider>
  </React.StrictMode>,
  document.getElementById('root')
);
