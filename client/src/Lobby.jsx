import React from 'react';

class Lobby extends React.Component {
  render() {
    return (
      <div class="container">
        <div class="card mt-3">
          <h1 class="card-header">Boss Fight</h1>
          <div class="card-body">
            <form>
              <div class="mb-4">
                <label class="form-label">Player Name</label>
                <input type="text" class="form-control"/>
              </div>
              <div className="mt-4 mb-4">
                <label className="form-label">Room Code</label>
                <div className="input-group mb-3">
                  <input type="text" className="form-control" placeholder="BIGBAL"/>
                  <button className="btn btn-secondary" type="button" id="button-addon1">Join game</button>
                </div>
              </div>
              <hr/>
              <div className="row mt-4">
                <div className="col text-center">
                  <div className="d-grid">
                    <button className="btn btn-primary">Create public game</button>
                  </div>
                </div>
                <div className="col text-center">
                  <div className="d-grid">
                    <button className="btn btn-outline-secondary btn-block">Create private game</button>
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