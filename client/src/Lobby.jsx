import React from 'react';

import {createGame,joinGame,reportErrors,disableInput} from "./actions";
import {connect} from "react-redux";
import Errors from "./Errors"

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
      alert: "",
      statusText: null,
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

    if (errored) {
      this.props.reportErrors(
        errors
      );
    }

    return !errored;
  }

  handleCreatePrivateGame = (event) => {
    event.preventDefault();

    if (!this.validateForm(false)) {
      return;
    }

    console.log("Successfully validated, creating game");
    this.props.createGame(this.state.playerName, this.props.uuid);
  };

  handleJoinGame = (event) => {
    event.preventDefault();

    if (!this.validateForm(true)) {
      return;
    }

    console.log("Successfully validated, joining game", this.state.gameCode);
    this.props.joinGame(this.state.playerName, this.state.gameCode, this.props.uuid);
  };

  render() {
    let errorDisplay = null;
    if (this.props.errors) {
      errorDisplay = <Errors errors={this.props.errors}/>;
    }

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
          <Alert statusText={this.state.statusText}/>
          {errorDisplay}
          <form onSubmit={this.handleDummySubmit}>
            <div className="mb-4">
              <label className="form-label">Player Name</label>
              <input
                name="playerName"
                value={this.state.playerName}
                onChange={this.handleChange}
                disabled={this.props.inputDisabled}
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
                  disabled={this.props.inputDisabled}
                  maxLength={this.GAME_CODE_LENGTH}
                  type="text"
                  className="form-control text-uppercase"
                  placeholder="BIGBAL" />
                <button
                  onClick={this.handleJoinGame}
                  disabled={this.state.gameCode.length < 5 || this.props.inputDisabled}
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
                  disabled={this.props.inputDisabled || this.state.gameCode}
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

function Alert(props) {
  if (props.statusText) {
    return (
      <div className="alert alert-primary">
        {props.text}
      </div>
    )
  }

  return null;
}

function mapStateToProps(state) {
  return {
    errors: state.errors,
    status: state.status,
    presetValues: state.presetLobbyFormValues,
    uuid: state.uuid,
    inputDisabled: state.inputDisabled,
  }
}

const mapDispatchToProps = {
  createGame,
  joinGame,
  reportErrors
};

export default connect(mapStateToProps, mapDispatchToProps)(Lobby);
