import React from "react";
import {connect} from "react-redux";

import {submitPrompt} from "./actions";
import Errors from "./Errors"

class SubmitPrompts extends React.Component {
  #PROMPT_SUBMISSIONS = 2;
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

    this.props.submitPrompt(this.props.gameCode, this.state.promptValue.trim());
    this.setState({promptValue: ""});
  };

  canSubmit = () => {
    return this.state.promptValue.match(this.#PROMPT_REGEX)
      && this.state.promptValue.length >= this.#PROMPT_MIN_LENGTH
  };

  isSubmitting = () => {
    return false;// this.props.status === GAME_STATUS.SUBMITTING_PROMPT;
  };

  getStatusText = () => {
    if (this.props.currentPlayer.submissionFinished) {
      return "Submissions finished, waiting on other players"
    }

    if (this.isSubmitting()) {
      return "Submitting...";
    }

    return `Submission ${this.props.currentPlayer.private.currentPromptNumber} of ${this.#PROMPT_SUBMISSIONS}`;
  };

  getCharacterCount = () => {
    if (this.props.currentPlayer.submissionFinished) {
      return null;
    }

    return <em>{ this.state.promptValue.length} / {this.#PROMPT_MAX_LENGTH } chars</em>

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
            <Errors errors={this.props.errors}/>
            <div className="ps-1 pe-2">
              <div className="float-start">
                <em>{ this.getStatusText() }</em>
              </div>
              <div className="float-end">
                { this.getCharacterCount() }
              </div>
              <div className="clearfix"/>
            </div>
            <form
              onSubmit={this.handleSubmit}
              className="input-group mb-1 mt-2">
              <input
                disabled={this.isSubmitting() || this.props.currentPlayer.submissionFinished}
                onChange={this.handleChange}
                value={this.state.promptValue}
                name="attribute"
                type="text"
                className="form-control"
                placeholder="emotionally stable" />
              <button
                disabled={!this.canSubmit() || this.isSubmitting() || this.props.currentPlayer.submissionFinished}
                className="btn btn-primary">
                Submit
              </button>
            </form>
          </div>
        </div>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {
    submitting: state.submitting,
    status: state.status,
    promptNumber: state.promptSubmissionNumber,
    errors: state.errors,
    gameCode: state.gameCode,
    players: state.players,
    currentPlayer: state.currentPlayer
  }
}

const mapDispatchToProps = {
  submitPrompt
};

export default connect(mapStateToProps, mapDispatchToProps)(SubmitPrompts);
