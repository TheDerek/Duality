import {LOCAL_STORAGE_GAME_CODE, LOCAL_STORAGE_PLAYER_NAME, LOCAL_STORAGE_UUID} from "./index";

export const GAME_STATES = {
  LOBBY: "LOBBY",
  WAITING_ROOM: "WAITING_ROOM",
  SUBMIT_PROMPTS: "SUBMIT_PROMPTS",
  DRAW_PROMPTS: "DRAW_PROMPTS",
  WAITING_FOR_PLAYERS: "WAITING_FOR_PLAYERS",
  ASSIGN_PROMPTS: "ASSIGN_PROMPTS",
  DISPLAY_RESULTS: "DISPLAY_RESULTS",
  DISPLAY_SCORES: "DISPLAY_SCORES"
};

export function getInitialState() {
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
    drawingPrompts: [],
    drawing: null,
    inputDisabled: false,
    assignedPrompts: [],
    isGameFinished: false,
    situation: null,
  }
}
