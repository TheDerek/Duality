import React from "react";
import {connect} from "react-redux";
import {LOBBY_STATUS} from "./actions";

class SubmitAttributes extends React.Component {
  #ATTRIBUTE_REGEX = /^[a-zA-Z0-9\s]{0,35}$/;

  constructor(props) {
    super(props);

    this.state = {
      attributeValue: ""
    }
  }

  handleChange = (event) => {
    const target = event.target;
    const value = target.value;

    const startPos = target.selectionStart;

    if (!value.match(this.#ATTRIBUTE_REGEX)) {
      window.requestAnimationFrame(() => {
        target.selectionStart = startPos - 1;
        target.selectionEnd = startPos - 1;
      });
      return;
    }

    this.setState({
      attributeValue: value
    });
  };

  handleSubmit = (event) => {
    event.preventDefault();
  };

  render() {
    return (
      <div>
        <div className="card">
          <div className="card-body">
            <div className="progress">
              <div className="progress-bar" role="progressbar" style={{width: "25%"}}/>
            </div>
            <p className="mt-2 mb-0">
              <em>Remaining time: <span className="ps-1">5 seconds</span></em>
            </p>
          </div>
        </div>
        <div className="card mt-4">
          <div className="card-body">
            <h5 className="card-title mb-3">
              What attribute would be essential in a fight against a supervillain?
            </h5>
            <div className="ps-1 pe-2">
              <div className="float-start">
                <em>Attribute 1 of 2</em>
              </div>
              <div className="float-end">
                <em>{this.state.attributeValue.length} / 35 chars</em>
              </div>
              <div className="clearfix"/>
            </div>
            <form
              onSubmit={this.handleSubmit}
              className="input-group mb-1 mt-2">
              <input
                onChange={this.handleChange}
                value={this.state.attributeValue}
                name="attribute"
                type="text"
                className="form-control"
                placeholder="emotionally stable" />
              <button
                className="btn btn-secondary">
                Submit
              </button>
            </form>
            <p className="mb-1 ps-1">
              <em>e.g. bravery, strength, courage</em>
            </p>
          </div>
        </div>
        <div className="card-group mt-4">
          <div className="card">
            <div className="card-header">
              Waiting for
            </div>
            <ul className="list-group list-group-flush">
              <li className="list-group-item">Derek</li>
              <li className="list-group-item">Cras justo odio</li>
            </ul>
          </div>
          <div className="card">
            <div className="card-header">
              Done
            </div>
            <ul className="list-group list-group-flush">
              <li className="list-group-item">Cras justo odio</li>
              <li className="list-group-item">Dapibus ac facilisis in</li>
              <li className="list-group-item">Vestibulum at eros</li>
            </ul>
          </div>
        </div>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {

  }
}

const mapDispatchToProps = {

};

export default connect(mapStateToProps, mapDispatchToProps)(SubmitAttributes);