import React from 'react';

class Lobby extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      playerName: "",
      roomCode: ""
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

  handleCreatePrivateGame = (event) => {
    event.preventDefault();

    console.log("Creating private game");
  };

  render() {
    return (
      <div className="container">
        <div className="card mt-3">
          <h1 className="card-header">Boss Fight</h1>
          <div className="card-body">
            <form onSubmit={this.handleDummySubmit}>
              <div className="mb-4">
                <label className="form-label">Player Name</label>
                <input
                  required
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
              <div className="row mt-4 mb-1">
                <div className="col text-center">
                  <div className="d-grid">
                    <button
                      className="btn btn-primary">
                      Create public game
                    </button>
                  </div>
                </div>
                <div className="col text-center">
                  <div className="d-grid">
                    <button
                      onClick={this.handleCreatePrivateGame}
                      className="btn btn-outline-secondary btn-block">
                      Create private game
                    </button>
                  </div>
                </div>
              </div>
            </form>
          </div>
        </div>
        <div className="card mt-3">
          <h3 className="card-header">Active games</h3>
          <ul className="list-group list-group-flush">
            <li className="list-group-item">Cras justo odio</li>
            <li className="list-group-item">Dapibus ac facilisis in</li>
            <li className="list-group-item">Vestibulum at eros</li>
          </ul>
        </div>
      </div>
    );
  }
}

export default Lobby;