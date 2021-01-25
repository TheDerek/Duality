import React from 'react';
import ReactDOM from 'react-dom'
import { createStore, applyMiddleware } from "redux";
import { Provider } from "react-redux";
import thunk from 'redux-thunk';
import reduxWebsocket from '@giantmachines/redux-websocket';
import { connect } from '@giantmachines/redux-websocket';
import { composeWithDevTools } from 'redux-devtools-extension';

import './index.css'
import App from "./App"
import { reducer } from "./reducer"

export const LOCAL_STORAGE_PLAYER_NAME = "playerNameValue";
export const LOCAL_STORAGE_GAME_CODE = "gameCodeValue";
export const LOCAL_STORAGE_UUID = "uuid";

const WEBSOCKET_ADDRESS = process.env.REACT_APP_SERVER_ADDRESS;

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

    if (name === "finishedGame") {
      localStorage.removeItem(LOCAL_STORAGE_GAME_CODE);
    }
  }

  return next(action);
};

const store = createStore(reducer, composeWithDevTools(
  applyMiddleware(thunk, reduxWebsocketMiddleware, gameMiddleware)
));


store.dispatch(connect(WEBSOCKET_ADDRESS));

ReactDOM.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>,
  document.getElementById('root')
);
