import { send } from '@giantmachines/redux-websocket';

export const REPORT_STATUS = "REPORT_STATUS";
export const SET_UUID = "SET_UUID";
export const SET_SUBMITTING = "SET_SUBMITTING";

export const GAME_STATUS = {
  NORMAL: "NORMAL",
  ERRORED: "ERRORED",
  JOINING_GAME: "JOINING_GAME",
  CREATING_GAME: "CREATING_GAME",
  SUBMITTING_PROMPT: "SUBMITTING_PROMPT"
};

export function createGame(playerName, uuid) {
  return send({
    createGame: {
      playerName: playerName,
      uuid: uuid
    }
  });
}

export function joinGame(playerName, gameCode, uuid) {
  return send({
    joinGame: {
      playerName: playerName,
      gameCode: gameCode,
      uuid: uuid
    }
  });
}

export function reportGameStatus(status, errors=[]) {
  return {
    type: REPORT_STATUS,
    status: status,
    errors: errors
  }
}

export function setUuid() {
  let uuid = localStorage.getItem("uuid");
  if (uuid) {
    return {
      type: SET_UUID,
      uuid: uuid
    }
  }

  return send({
    generateUuid: {

    }
  })
}

export function startGame(gameCode) {
  return send({
    startGame: {
      gameCode: gameCode
    }
  });
}

export function submitPrompt(prompt) {
  return dispatch => {
    dispatch(reportGameStatus(GAME_STATUS.SUBMITTING_PROMPT));
    dispatch(send({
      submitPrompt: {
        prompt: prompt
      }
    }));
  }
}
