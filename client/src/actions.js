import { send } from '@giantmachines/redux-websocket';

export const INCREMENT = "INCREMENT";
export const DECREMENT = "DECREMENT";
export const RESET = "RESET";
export const GET_TODOS = "GET_TODOS";

export function increment() {
  return {
    type: INCREMENT
  }
}

export function decrement() {
  return {
    type: DECREMENT
  }
}

export function reset() {
  return {
    type: RESET
  }
}

function convertToTodos(todoJson) {
  return todoJson.map(json => json.title);
}

export function createGame(playerName) {
  return send({
    createGame: {
      playerName: playerName
    }
  });
}

export function getTodos() {
  return dispatch => {
    return fetch('https://jsonplaceholder.typicode.com/todos/')
      .then(res => res.json())
      .then(json => convertToTodos(json))
      .then(todos => dispatch({
        type: GET_TODOS,
        todos: todos
      }));
  }
}