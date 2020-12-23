import React from 'react';
import {createGame,joinGame} from "./actions";
import {connect} from "react-redux";

class Lobby extends React.Component {
  NAME_MIN_LENGTH = 2;
  NAME_MAX_LENGTH = 10;
  PLAYER_NAME_REGEX = /^[a-zA-Z0-9\s]+$/;
  ROOM_CODE_REGEX = /^[A-Z0-9]{5}$/;

  constructor(props) {
    super(props);
    this.state = {
      playerName: "",
      gameCode: "",
      errors: [],
      formDisabled: false,
      alert: ""
    };
  }

  handleChange = (event) => {
    const target = event.target;
    const value = target.value;
    const name = target.name;

    this.setState({
      [name]: value
    })
  };

  handleDummySubmit = (event) => {
    event.preventDefault();
  };

  validateForm(validategameCode) {
    const playerName = this.state.playerName;
    const gameCode = this.state.gameCode;
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

    if (validategameCode && !gameCode.match(this.ROOM_CODE_REGEX)) {
      errors.push("Invalid room code");
    }


    this.setState({
      ...this.state,
      errors: errors
    });

    return errors.length < 1;
  }

  handleCreatePrivateGame = (event) => {
    event.preventDefault();

    if (!this.validateForm(false)) {
      return;
    }

    this.setState({
      ...this.state,
      errors: [],
      formDisabled: true,
      alert: "Creating game..."
    });

    console.log("Successfully validated, creating game");
    this.props.createGame(this.state.playerName);
  };

  handleJoinGame = (event) => {
    event.preventDefault();

    if (!this.validateForm(true)) {
      return;
    }

    this.setState({
      ...this.state,
      errors: [],
      formDisabled: true,
      alert: `Joining game ${this.state.gameCode}...`
    });

    console.log("Successfully validated, joining game", this.state.gameCode);
    this.props.joinGame(this.state.playerName, this.state.gameCode);
  };

  render() {
    let errorDisplay = null;
    if (this.state.errors.length > 0) {
      errorDisplay = <Errors errors={this.state.errors}/>;
    }

    let alert = null;
    if (this.state.alert) {
      alert = <Alert text={this.state.alert}/>;
    }
    return (
      <div className="container">
        <div className="card mt-3">
          <h1 className="card-header">In the know</h1>
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
                  disabled={this.state.formDisabled}
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
                    disabled={this.state.formDisabled}
                    type="text"
                    className="form-control"
                    placeholder="BIGBAL" />
                  <button
                    onClick={this.handleJoinGame}
                    disabled={this.state.formDisabled}
                    className="btn btn-secondary">
                    Join game
                  </button>
                </div>
              </div>
              <hr/>
              <div className="text-center">
                <div className="d-grid">
                  <button
                    onClick={this.handleCreatePrivateGame}
                    disabled={this.state.formDisabled}
                    className="btn btn-primary btn-block">
                    Create new game
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }
}

function Errors(props) {
  return (
    <div className="alert alert-warning">
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

function mapStateToProps() {
  return {

  }
}

const mapDispatchToProps = {
  createGame,
  joinGame
};

export default connect(mapStateToProps,mapDispatchToProps)(Lobby);