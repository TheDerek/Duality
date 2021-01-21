import React from "react";
import {connect} from "react-redux";
import {useSprings, animated, useChain, useTrail} from 'react-spring';
import {useRef} from "react";

import {nextRound} from "./actions"

const PERCENT_PER_POINT = 100 / 6;


function getWidth(score) {
  const width = score * PERCENT_PER_POINT;
  return `${width}%`;
}

function PlayerScore(props) {
  return (
    <animated.div className="mb-3" style={props.fadeIn}>
      <h5>
        <div className="float-start">
          {props.player.name}
        </div>
        <div className="float-end">
          {props.player.score.previous}
          <animated.span style={props.newScore}>
            &nbsp;+ {props.player.score.current_round} &#8680; {props.player.score.total}
          </animated.span>
        </div>
        <div className="clearfix"/>
      </h5>
      <div className="progress" style={{height: "30px"}}>
        <div
          className="progress-bar"
          role="progressbar"
          style={{width: getWidth(props.player.score.previous_round)}}/>
        <animated.div
          className="progress-bar bg-success"
          role="progressbar"
          style={props.elongate}/>
      </div>
    </animated.div>
  )
}

function Scores(props) {
  const fadeInRef = useRef()
  const fadeIn = useSprings(props.players.length, props.players.map((player, index) => ({
    from: {opacity: 0},
    to: {opacity: 1},
    delay: 500 + index * 500,
    ref: fadeInRef,
  })));

  const elongateRef = useRef()
  const elongate = useSprings(props.players.length, props.players.map((player, index) => ({
    from: {width: '0%'},
    to: {width: getWidth(player.score.current_round)},
    delay: 500 + index * 1000,
    ref: elongateRef,
  })));

  const newScoreRef = useRef()
  const newScore = useSprings(props.players.length, props.players.map((player, index) => ({
    from: {opacity: 0},
    to: {opacity: 1},
    ref: newScoreRef,
    delay: 500 + index * 1000,
    onRest: index + 1 === props.players.length ? props.onFinishedAnimation : null,
  })));

  useChain([fadeInRef, elongateRef, newScoreRef])

  return (
    <div>
      {/*{ trail.map(props => <animated.div style={props}>Heyoh</animated.div>) }*/}
      {props.players.map((player, index) => <PlayerScore key={index} player={player} fadeIn={fadeIn[index]} elongate={elongate[index]} newScore={newScore[index]}/>)}
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
          <Scores players={this.props.players} onFinishedAnimation={this.onFinishedAnimation}/>
          <button
            disabled={!this.props.player.admin || !this.state.canContinue || this.props.inputDisabled}
            onClick={this.props.nextRound}
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
  nextRound,
}

export default connect(mapStateToProps, mapDispatchToProps)(DisplayScores);
