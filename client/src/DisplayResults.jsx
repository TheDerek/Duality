import React from "react";
import {connect} from "react-redux";
import {useSpring, animated} from 'react-spring';

import { finishResults } from './actions';

const FIRST_WAIT = 3500;
const NEXT_WAIT = 5000;
const CORRECT_DELAY = 2500;

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
    <animated.img style={animation} className="w-100 game-img" src={props.drawing}/>
  )
}

class DisplayResults extends React.Component {
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
        <h3 className="text-center">What weaknesses does this monster have?</h3>
        <p className="text-center"><em>Drawing 1 / 4</em></p>
        <div className="row">
          <div className="col-sm">
            <Drawing drawing={this.props.drawing}/>
          </div>
          <div className="col-sm">
            { continueButton }
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
    inputDisabled: state.inputDisabled
  }
}

const mapDispatchToProps = {
  finishResults,
}

export default connect(mapStateToProps, mapDispatchToProps)(DisplayResults);
