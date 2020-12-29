import React from "react";
import {connect} from "react-redux";
import {submitPrompt} from "./actions";

class SubmitPrompts extends React.Component {
  #PROMPT_MAX_LENGTH = 35;
  #PROMPT_MIN_LENGTH = 3;
  #PROMPT_REGEX = new RegExp(`^[a-zA-Z0-9\\s]{0,${this.#PROMPT_MAX_LENGTH}}$`);

  constructor(props) {
    super(props);

    this.state = {
      promptValue: "",
    }
  }

  handleChange = (event) => {
    const target = event.target;
    const value = target.value;

    const startPos = target.selectionStart;

    if (!value.match(this.#PROMPT_REGEX)) {
      window.requestAnimationFrame(() => {
        target.selectionStart = startPos - 1;
        target.selectionEnd = startPos - 1;
      });
      return;
    }

    this.setState({
      promptValue: value
    });
  };

  handleSubmit = (event) => {
    event.preventDefault();

    if (!this.canSubmit()) {
      return;
    }

    this.props.submitPrompt(this.state.promptValue.trim());
  };

  canSubmit = () => {
    return this.state.promptValue.match(this.#PROMPT_REGEX)
      && this.state.promptValue.length >= this.#PROMPT_MIN_LENGTH
  };

  getStatus = () => {

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
              What ability would be essential in a fight against a supervillain?
            </h5>
            <div className="ps-1 pe-2">
              <div className="float-start">
                <em>Prompt 1 of 2</em>
              </div>
              <div className="float-end">
                <em>{this.state.promptValue.length} / {this.#PROMPT_MAX_LENGTH} chars</em>
              </div>
              <div className="clearfix"/>
            </div>
            <form
              onSubmit={this.handleSubmit}
              className="input-group mb-1 mt-2">
              <input
                disabled={this.props.submitting}
                onChange={this.handleChange}
                value={this.state.promptValue}
                name="attribute"
                type="text"
                className="form-control"
                placeholder="emotionally stable" />
              <button
                disabled={!this.canSubmit() || this.props.submitting}
                className="btn btn-primary">
                Submit
              </button>
            </form>
          </div>
        </div>
        <div className="card-group mt-4">
          <div className="card">
            <div className="card-header">
              Waiting for
            </div>
            <ul className="list-group list-group-flush">
              <li className="list-group-item border-0">Derek</li>
              <li className="list-group-item border-0">Cras justo odio</li>
            </ul>
          </div>
          <div className="card">
            <div className="card-header">
              Done
            </div>
            <ul className="list-group list-group-flush">
              <li className="list-group-item border-0">Cras justo odio</li>
              <li className="list-group-item border-0">Dapibus ac facilisis in</li>
              <li className="list-group-item border-0">Vestibulum at eros</li>
            </ul>
          </div>
        </div>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {
    submitting: state.submitting
  }
}

const mapDispatchToProps = {
  submitPrompt
};

export default connect(mapStateToProps, mapDispatchToProps)(SubmitPrompts);