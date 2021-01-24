import { send } from '@giantmachines/redux-websocket';

export const SET_UUID = "SET_UUID";
export const DISABLE_INPUT = "DISABLE_INPUT";
export const REPORT_ERRORS = "REPORT_ERRORS";

export function createGame(playerName, uuid) {
  return (dispatch) => {
    dispatch(reportErrors());
    dispatch(send({
      createGame: {
        playerName: playerName,
        uuid: uuid
      }
    }));
  }
}

export function joinGame(playerName, gameCode, uuid) {
  return (dispatch) => {
    dispatch(disableInput());
    dispatch(send({
      joinGame: {
        playerName: playerName,
        gameCode: gameCode,
        uuid: uuid
      }
    }));
  }
}

export function reportErrors(errors=[]) {
  return {
    type: REPORT_ERRORS,
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

export function submitDrawing(gameCode, drawing) {
  return send({
    submitDrawing: {
      gameCode: gameCode,
      drawing: drawing
    }
  });
}

export function submitPrompt(gameCode, prompt) {
  return dispatch => {
    dispatch(disableInput());
    dispatch(reportErrors());
    dispatch(send({
      submitPrompt: {
        gameCode: gameCode,
        prompt: prompt
      }
    }));
  }
}

export function assignPrompt(prompt) {
  return (dispatch, getState) => {
    dispatch(disableInput());
    dispatch(send({
      assignPrompt: {
        gameCode: getState().gameCode,
        prompt: prompt
      }
    }));
  }
}

export function finishResults() {
  return (dispatch, getState) => {
    dispatch(disableInput());
    dispatch(send({
      finishResults: {
        gameCode: getState().gameCode,
      }
    }));
  }
}

export function disableInput() {
  return {
    type: DISABLE_INPUT
  }
}

export function nextRound() {
  return (dispatch, getState) => {
    dispatch(disableInput());
    dispatch(send({
      nextRound: {
        gameCode: getState().gameCode,
      }
    }));
  }
}
