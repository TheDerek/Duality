import {getInitialState, GAME_STATES} from "./state";
import {DISABLE_INPUT, REPORT_ERRORS, BACK_TO_MENU} from "./actions";

function messageReducer(state, name, data) {
  switch(name) {
    case "error": {
      console.error(data);
      return {
        ...state,
        errors: [data.userMessage],
        inputDisabled: false,
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
        assignedPrompts: data.assignedPrompts,
        errors: [],
        inputDisabled: false,
        isGameFinished: data.isGameFinished,
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
        errors: [],
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
        gameState: data.gameState,
        inputDisabled: false,
        errors: [],
      }
    }
    case "finishedGame": {
      return {
        ...state,
        isGameFinished: true,
      }
    }
    default:
      return state;
  }
}

export function reducer(state = getInitialState(), action) {
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
    case REPORT_ERRORS:
      console.log("Setting lobby status");
      return {
        ...state,
        inputDisabled: false,
        errors: action.errors
      };
    case DISABLE_INPUT:
      return {
        ...state,
        inputDisabled: true
      }
    case BACK_TO_MENU:
      return getInitialState();
    default:
      return state;
  }
}
