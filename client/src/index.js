import React from 'react';
import ReactDOM from 'react-dom'
import { createStore, applyMiddleware, compose } from "redux";
import { Provider } from "react-redux";
import thunk from 'redux-thunk';
import reduxWebsocket from '@giantmachines/redux-websocket';
import { connect } from '@giantmachines/redux-websocket';

import './index.css'
import App from "./App"
import { GAME_STATES } from "./App";
import { LOBBY_STATUS, REPORT_LOBBY_STATUS } from "./actions";

const WEBSOCKET_ADDRESS = 'ws://localhost:6789';

const initialState = {
  gameState: GAME_STATES.LOBBY,
  lobby: {
    status: LOBBY_STATUS.NORMAL,
    errors: []
  },
  waitingRoom: {
    players: [

    ],
    admin: false,
    gameCode: "NULL"
  },
  currentPlayer: null
};

function messageReducer(state, name, data) {
  switch(name) {
    case "noGameFound": {
      const code = data.gameCode;
      return {
        ...state,
        lobby: {
          status: LOBBY_STATUS.ERRORED,
          errors: [`Could not find game with code ${code}`]
        }
      };
    }
    case "joinGame": {
      return {
        ...state,
        gameState: GAME_STATES.WAITING_ROOM,
        waitingRoom: data,
        currentPlayer: data.players.find(p => p.currentPlayer)
      };
    }
    case "playerJoinedGame": {
      return {
        ...state,
        gameState: GAME_STATES.WAITING_ROOM,
        waitingRoom: {
          ...state.waitingRoom,
          players: [
            ...state.waitingRoom.players,
            data.player
          ]
        }
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

const store = createStore(
  reducer,
  applyMiddleware(thunk, reduxWebsocketMiddleware)
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
