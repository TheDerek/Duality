import React from "react";
import {connect} from "react-redux";
import {useSpring, animated} from 'react-spring';

const PERCENT_PER_POINT = 100/6;

function getWidth(score) {
  const width = score * PERCENT_PER_POINT;
  return `${width}%`;
}

function PlayerScore(props) {
  return (
    <div className="mb-3">
      <h5>{props.player.name} - {props.player.score.total}</h5>
      <div className="progress" style={{height: "30px"}}>
        <div
          className="progress-bar"
          role="progressbar"
          style={{width: getWidth(props.player.score.previous_round)}}/>
        <div
          className="progress-bar bg-success"
          role="progressbar"
          style={{width: getWidth(props.player.score.current_round)}}/>
      </div>
    </div>
  )
}

function Scores(props) {
  return (
    <div>
      { props.players.map((player, index) => <PlayerScore key={index} player={player}/>) }
    </div>
  )
}

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
    let displayContinueClass = "mt-2 btn btn-primary ";

    if (!this.props.player.admin) {
      displayContinueClass += "d-none"
    }

    return (
      <div>
        <h3 className="text-center mb-3">Results for round 1</h3>
        <div className="d-grid">
          <Scores players={this.props.players}/>
          <button
            disabled={!this.props.player.admin || !this.state.canContinue || this.props.inputDisabled}
            onClick={this.props.finishResults}
            className={displayContinueClass}>
            Continue
          </button>
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
}

export default connect(mapStateToProps, mapDispatchToProps)(DisplayScores);
