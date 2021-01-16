import React from "react";
import {connect} from "react-redux";
import {useSpring, animated} from 'react-spring';

import { finishResults } from './actions';


class DisplayScores extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      canContinue: false
    }
  }

  onFinishedAnimation = () => {
    this.setState({
      ...this.state,
      canContinue: true,
    })
  }

  render() {
    let continueButton = null;
    if (this.props.player.admin) {
      continueButton = (
        <div className="d-grid">
          <button
            disabled={!this.props.player.admin || !this.state.canContinue || this.props.inputDisabled}
            onClick={this.props.finishResults}
            className="mb-2 btn btn-primary">
            Continue
          </button>
        </div>
      );
    }

    return (
      <div>
        <h3 className="text-center">Results for round 1</h3>
        <div className="row">
          <div className="col-sm">
          </div>
          <div className="col-sm">
            { continueButton }
          </div>
        </div>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {
    player: state.currentPlayer,
    players: state.players
  }
}

const mapDispatchToProps = {
  finishResults,
}

export default connect(mapStateToProps, mapDispatchToProps)(DisplayScores);
