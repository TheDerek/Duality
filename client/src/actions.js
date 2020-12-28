import { send } from '@giantmachines/redux-websocket';

export const REPORT_LOBBY_STATUS = "REPORT_LOBBY_STATUS";
export const SET_UUID = "SET_UUID";

export const LOBBY_STATUS = {
  NORMAL: "NORMAL",
  ERRORED: "ERRORED",
  JOINING_GAME: "JOINING_GAME",
  CREATING_GAME: "CREATING_GAME"
};

export function createGame(playerName) {
  return send({
    createGame: {
      playerName: playerName
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

export function reportLobbyStatus(status, errors=[]) {
  return {
    type: REPORT_LOBBY_STATUS,
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

export function startGame(playerName) {
  return send({
    startGame: {
    }
  });
}