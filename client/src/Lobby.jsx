import React from 'react';
import {createGame,joinGame,reportLobbyStatus,LOBBY_STATUS} from "./actions";
import {connect} from "react-redux";

class Lobby extends React.Component {
  NAME_MIN_LENGTH = 2;
  NAME_MAX_LENGTH = 10;
  GAME_CODE_LENGTH = 5;
  PLAYER_NAME_REGEX = /^[a-zA-Z0-9\s]+$/;
  ROOM_CODE_REGEX = /^[A-Z0-9]{5}$/;

  constructor(props) {
    super(props);
    this.state = {
      playerName: this.props.presetValues.name,
      gameCode: this.props.presetValues.gameCode,
      alert: ""
    };
  }

  handleChange = (event) => {
    const target = event.target;
    const name = target.name;
    const value = target.value;

    const startPos = target.selectionStart;

    if (value && name === "gameCode" && !value.match(/^[a-zA-Z0-9]+$/i)) {
      window.requestAnimationFrame(() => {
        target.selectionStart = startPos - 1;
        target.selectionEnd = startPos - 1;
      });
      return;
    }

    if (value && name === "playerName" && !value.match(this.PLAYER_NAME_REGEX)) {
      window.requestAnimationFrame(() => {
        target.selectionStart = startPos - 1;
        target.selectionEnd = startPos - 1;
      });
      return;
    }

    this.setState({
      [name]: value
    });
  };

  handleDummySubmit = (event) => {
    event.preventDefault();
  };

  validateForm(validateGameCode) {
    const playerName = this.state.playerName.trim();
    const gameCode = this.state.gameCode.toUpperCase();
    let errors = [];

    console.log("Validating playerName=" + playerName);

    if (playerName.length < this.NAME_MIN_LENGTH) {
      errors.push(`Please enter a name longer than or equal to ${this.NAME_MIN_LENGTH} characters`);
    }

    if (playerName.length > this.NAME_MAX_LENGTH) {
      errors.push(`Please enter a name shorter than or equal to ${this.NAME_MAX_LENGTH} characters`);
    }

    if (playerName.length > 0 && !playerName.match(this.PLAYER_NAME_REGEX)) {
      errors.push('Please enter a name containing only ASCII letters, numbers and spaces');
    }

    if (validateGameCode && !gameCode.match(this.ROOM_CODE_REGEX)) {
      errors.push("Invalid game code");
    }

    let errored = errors.length > 0;

    this.props.reportLobbyStatus(
      errored ? LOBBY_STATUS.ERRORED : LOBBY_STATUS.NORMAL,
      errors
    );

    return !errored;
  }

  handleCreatePrivateGame = (event) => {
    event.preventDefault();

    if (!this.validateForm(false)) {
      return;
    }

    this.props.reportLobbyStatus(LOBBY_STATUS.CREATING_GAME);

    console.log("Successfully validated, creating game");
    this.props.createGame(this.state.playerName);
  };

  handleJoinGame = (event) => {
    event.preventDefault();

    if (!this.validateForm(true)) {
      return;
    }

    this.props.reportLobbyStatus(LOBBY_STATUS.JOINING_GAME);

    console.log("Successfully validated, joining game", this.state.gameCode);
    this.props.joinGame(this.state.playerName, this.state.gameCode, this.props.uuid);
  };

  getAlert() {
    const status = this.props.status;

    if (status === LOBBY_STATUS.CREATING_GAME) {
      return <Alert text="Creating game..."/>;
    }

    if (status === LOBBY_STATUS.JOINING_GAME) {
      return <Alert text="Joining game..."/>;
    }

    return null;
  }

  isFormDisabled() {
    return this.props.status === LOBBY_STATUS.JOINING_GAME
      || this.props.status === LOBBY_STATUS.CREATING_GAME;
  }

  render() {
    let errorDisplay = null;
    if (this.props.status === LOBBY_STATUS.ERRORED) {
      errorDisplay = <Errors errors={this.props.errors}/>;
    }

    let alert = this.getAlert();

    let gameCodeWarning = null;
    if (this.state.gameCode) {
      gameCodeWarning = <p><em>
        Please remove the game code in order to create a new game
      </em></p>;
    }

    return (
      <div className="card mt-3">
        <div className="card-header">Lobby</div>
        <div className="card-body">
          {alert}
          {errorDisplay}
          <form onSubmit={this.handleDummySubmit}>
            <div className="mb-4">
              <label className="form-label">Player Name</label>
              <input
                name="playerName"
                value={this.state.playerName}
                onChange={this.handleChange}
                disabled={this.isFormDisabled()}
                maxLength={this.NAME_MAX_LENGTH}
                type="text"
                className="form-control"
                placeholder="Mr. Woshy" />
            </div>
            <div className="mt-4 mb-4">
              <label className="form-label">Game Code</label>
              <div className="input-group mb-3">
                <input
                  name="gameCode"
                  value={this.state.gameCode}
                  onChange={this.handleChange}
                  disabled={this.isFormDisabled()}
                  maxLength={this.GAME_CODE_LENGTH}
                  type="text"
                  className="form-control text-uppercase"
                  placeholder="BIGBAL" />
                <button
                  onClick={this.handleJoinGame}
                  disabled={this.isFormDisabled()}
                  className="btn btn-secondary">
                  Join game
                </button>
              </div>
            </div>
            <hr/>
            <div className="text-center">
              <div className="d-grid">
                { gameCodeWarning }
                <button
                  onClick={this.handleCreatePrivateGame}
                  disabled={this.isFormDisabled() || this.state.gameCode}
                  className="btn btn-primary btn-block">
                  Create new game
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    );
  }
}

function Errors(props) {
  return (
    <div className="alert alert-danger">
      <ul className="mb-0">
        {
          props.errors.map((error, i) => <li key={i}>{error}</li>)
        }
      </ul>
    </div>
  );
}

function Alert(props) {
  return (
    <div className="alert alert-primary">
      {props.text}
    </div>
  )
}

function mapStateToProps(state) {
  return {
    errors: state.lobby.errors,
    status: state.lobby.status,
    presetValues: state.lobby.presetFormValues,
    uuid: state.uuid
  }
}

const mapDispatchToProps = {
  createGame,
  joinGame,
  reportLobbyStatus
};

export default connect(mapStateToProps, mapDispatchToProps)(Lobby);