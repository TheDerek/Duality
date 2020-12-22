import React from 'react';
import ReactDOM from 'react-dom'
import { createStore, applyMiddleware } from "redux";
import { Provider } from "react-redux";
import thunk from 'redux-thunk';

import Counter from './Counter';
import { INCREMENT, DECREMENT, RESET, GET_TODOS } from "./actions";


const initialState = {
  count: 0,
  todos: []
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
    default:
      return state;
  }
}

const store = createStore(
  reducer,
  applyMiddleware(thunk)
);

store.dispatch({ type: "INCREMENT" });
store.dispatch({ type: "INCREMENT" });
store.dispatch({ type: "DECREMENT" });
store.dispatch({ type: "RESET" });
store.dispatch({ type: "INCREMENT" });

const App = () => (
  <Provider store={store}>
    <Counter/>
  </Provider>
);

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
