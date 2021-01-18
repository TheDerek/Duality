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
import { GAME_STATES } from "./App";
import {DISABLE_INPUT, GAME_STATUS, REPORT_STATUS} from "./actions";

export const LOCAL_STORAGE_PLAYER_NAME = "playerNameValue";
export const LOCAL_STORAGE_GAME_CODE = "gameCodeValue";
export const LOCAL_STORAGE_UUID = "uuid";

const WEBSOCKET_ADDRESS = 'ws://localhost:6789';

function getInitialState() {
  return {
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
    currentDrawing: null,
    status: GAME_STATUS.NORMAL,
    drawingPrompts: [],
    drawing: null,
    inputDisabled: false,
    assignedPrompts: []
  }
}

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
        currentPlayer: data.currentPlayer,
        drawingPrompts: data.drawingPrompts,
        drawing: data.drawing,
        assignedPrompts: data.assignedPrompts
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
        gameState: data.gameState,
        inputDisabled: false,
      };
    }
    case "updatePlayer": {
      return {
        ...state,
        status: data.status || state.status,
        currentPlayer: data.player.name === state.currentPlayer.name
          ? data.player
          : state.currentPlayer,
        players: state.players.map((player) => {
          if (player.name === data.player.name) {
            return data.player
          }

          return player
        })
      }
    }
    case "setDrawingPrompts": {
      return {
        ...state,
        drawingPrompts: data.prompts
      }
    }
    case "setDrawing": {
      return {
        ...state,
        drawing: data.drawing
      }
    }
    case "setAssignedPrompts": {
      return {
        ...state,
        assignedPrompts: data.prompts
      }
    }
    case "resetSubmissionStatus": {
      return {
        ...state,
        players: state.players.map(player => ({
          ...player,
          submissionFinished: false,
        }))
      }
    }
    case "updateAllPlayers": {
      return {
        ...state,
        players: data.players,
        currentPlayer: data.currentPlayer,
      }
    }
    default:
      return state;
  }
}

function reducer(state = getInitialState(), action) {
  console.log('reducer', state, action);

  switch(action.type) {
    case 'REDUX_WEBSOCKET::CLOSED':
    case 'REDUX_WEBSOCKET::BROKEN':
      if (state.gameState === GAME_STATES.LOBBY) {
        return state;
      } else {
        console.log("Lost connection, returning to lobby..")
        return {
          ...getInitialState(),
          errors: ["Lost connection to server, please rejoin"]
        };
      }
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
    case DISABLE_INPUT:
      return {
        ...state,
        inputDisabled: true
      }
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
