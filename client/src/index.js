import React from 'react';
import ReactDOM from 'react-dom'
import { createStore, applyMiddleware, compose } from "redux";
import { Provider } from "react-redux";
import thunk from 'redux-thunk';
import reduxWebsocket from '@giantmachines/redux-websocket';
import { connect } from '@giantmachines/redux-websocket';

import Lobby from "./Lobby"
import { INCREMENT, DECREMENT, RESET, GET_TODOS } from "./actions";

const WEBSOCKET_ADDRESS = 'ws://localhost:6789';

const initialState = {
  count: 0,
  todos: [],
  connected: false,
  // One of NORMAL, ERRORED, JOINING_GAME or CREATING_GAME
  lobbyStatus: "NORMAL"
};

function reducer(state = initialState, action) {
  console.log('reducer', state, action);

  switch(action.type) {
    case INCREMENT:
      return {
        ...state,
        count: state.count + 1
      };
    case DECREMENT:
      return {
        ...state,
        count: state.count - 1
      };
    case RESET:
      return initialState;
    case GET_TODOS:
      return {
        ...state,
        todos: action.todos
      };
    case 'REDUX_WEBSOCKET::CLOSED':
      return {
        ...state,
        connected: false
      };
    case 'REDUX_WEBSOCKET::OPEN':
      return {
        ...state,
        connected: true
      };
    case 'REDUX_WEBSOCKET::MESSAGE':
      let data = JSON.parse(action.payload.message);
      console.log("Got data from websocket", data);
      return state;
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

const App = () => (
  <Provider store={store}>
    <Lobby/>
  </Provider>
);

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
