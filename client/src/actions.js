import { send } from '@giantmachines/redux-websocket';

export const INCREMENT = "INCREMENT";
export const DECREMENT = "DECREMENT";
export const RESET = "RESET";
export const GET_TODOS = "GET_TODOS";
export const REPORT_LOBBY_STATUS = "REPORT_LOBBY_STATUS";

export const LOBBY_STATUS = {
  NORMAL: "NORMAL",
  ERRORED: "ERRORED",
  JOINING_GAME: "JOINING_GAME",
  CREATING_GAME: "CREATING_GAME"
};

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

export function joinGame(playerName, gameCode) {
  return send({
    joinGame: {
      playerName: playerName,
      gameCode: gameCode
    }
  });
}

export function reportLobbyStatus(status, errors=[]) {
  return {
    type: REPORT_LOBBY_STATUS,
    status: status,
    errors: errors
  }
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