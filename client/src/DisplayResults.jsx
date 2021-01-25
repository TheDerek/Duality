import React from "react";
import {connect} from "react-redux";
import {useSpring, animated} from 'react-spring';

import { finishResults } from './actions';

const FIRST_WAIT = 1500;
const NEXT_WAIT = 2000;
const CORRECT_DELAY = 1500;

function CorrectText(props) {
  if (props.correct) {
    return <em className="text-success">&#x2713; Correct</em>;

  } else
    return <em className="text-danger">&#x2717; Incorrect</em>;
}

function Prompt(props) {
  let classes = "card mb-2";

  const animation = useSpring({
    from: {
      opacity: 0,
      transform: 'translate3d(130%,0,0)',
    },
    to: {
      opacity: 1,
      transform: 'translate3d(0,0px,0)',
    },
    delay: FIRST_WAIT + NEXT_WAIT * props.index
  });

  const animation2 = useSpring({
    from: {
      opacity: 0,
    },
    to: {
      opacity: 1,
    },
    delay: FIRST_WAIT + CORRECT_DELAY + NEXT_WAIT * props.index,
    onRest: props.last ? props.onFinishedAnimation : null,
  });

  return (
    <animated.div className={classes} style={animation}>
      <div className="card-header">
        <div className="float-start">
          { props.prompt.player_name }
        </div>
        <animated.div className="float-end" style={animation2}>
          <CorrectText correct={props.prompt.correct}/>
        </animated.div>
        <div className="clearfix"/>
      </div>
      <div className="card-body">{ props.prompt.prompt }</div>
    </animated.div>
  )
}

function PromptList(props) {
  const prompts = props.prompts;
  return prompts.map((prompt, index) => (
    <Prompt
      key={index}
      prompt={prompt}
      index={index}
      last={index+1 === prompts.length}
      onFinishedAnimation={props.onFinishedAnimation}
    />
  ));
}

function Drawing(props) {
  const animation = useSpring({
    from: {
      opacity: 0,
      transform: 'translate3d(-140px,0px,0px)'
    },
    to: {
      opacity: 1,
      transform: 'translate3d(0px,0px,0px)'
    },
    delay: 500,
  });

  return (
    <animated.img style={animation} className="w-100 game-img bg-white" src={props.drawing}/>
  )
}

class DisplayResults extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      // Can continue automatically if there are no prompts
      canContinue: this.props.prompts.length === 0
    }
  }

  onFinishedAnimation = () => {
    this.setState({
      ...this.state,
      canContinue: true,
    })
  }

  render() {
    let displayContinueClass = "mb-2 btn btn-primary ";

    if (!this.props.player.admin) {
      displayContinueClass += "d-none"
    }

    return (
      <div>
        <h3 className="text-center mb-3 text-white">{ this.props.situation }</h3>
        <div className="row">
          <div className="col-sm">
            <Drawing drawing={this.props.drawing}/>
          </div>
          <div className="col-sm">
            <div className="d-grid">
              <button
                disabled={!this.props.player.admin || !this.state.canContinue || this.props.inputDisabled}
                onClick={this.props.finishResults}
                className={displayContinueClass}>
                Continue
              </button>
            </div>
            <PromptList
              prompts={this.props.prompts}
              onFinishedAnimation={this.onFinishedAnimation}
            />
          </div>
        </div>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {
    prompts: state.assignedPrompts,
    drawing: state.drawing,
    player: state.currentPlayer,
    inputDisabled: state.inputDisabled,
    situation: state.situation.results
  }
}

const mapDispatchToProps = {
  finishResults,
}

export default connect(mapStateToProps, mapDispatchToProps)(DisplayResults);
