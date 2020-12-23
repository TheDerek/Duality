import React from 'react';

class Lobby extends React.Component {
  NAME_MIN_LENGTH = 2;
  NAME_MAX_LENGTH = 10;
  PLAYER_NAME_REGEX = /^[a-zA-z0-9\s]+$/;

  constructor(props) {
    super(props);
    this.state = {
      playerName: "",
      roomCode: "",
      errors: []
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

  validateForm(validateRoomCode) {
    const playerName = this.state.playerName;
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

    console.log("Successfully validated, creating game");
  };

  render() {
    let errorDisplay = null;
    if (this.state.errors.length > 0) {
      errorDisplay = <Errors errors={this.state.errors}/>;
    }
    return (
      <div className="container">
        <div className="card mt-3">
          <h1 className="card-header">In the know</h1>
          <div className="card-body">
            {errorDisplay}
            <form onSubmit={this.handleDummySubmit}>
              <div className="mb-4">
                <label className="form-label">Player Name</label>
                <input
                  name="playerName"
                  value={this.state.playerName}
                  onChange={this.handleChange}
                  type="text"
                  className="form-control"
                  placeholder="Mr. Woshy" />
              </div>
              <div className="mt-4 mb-4">
                <label className="form-label">Room Code</label>
                <div className="input-group mb-3">
                  <input
                    name="roomCode"
                    value={this.state.roomCode}
                    onChange={this.handleChange}
                    type="text"
                    className="form-control"
                    placeholder="BIGBAL" />
                  <button
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

export default Lobby;