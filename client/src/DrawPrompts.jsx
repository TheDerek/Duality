import React from "react";
import { connect } from "react-redux";

import { submitDrawing } from "./actions"
import SketchPad from "./SketchPad";

class DrawPrompts extends React.Component {
  constructor(props) {
    super(props);
    this.sketchPadRef = React.createRef();
  }

  submit = () => {
    const drawing = this.sketchPadRef.current.getPng();
    this.props.submitDrawing(this.props.gameCode, drawing);
  }

  render() {
    return (
      <div className="text-center">
        <div className="text-center card d-inline-block">
          <div className="card-body">
            <h3 className="mb-4 text-center">
              { this.props.situation.replace("_", this.props.drawingPrompts[0]).replace("_", this.props.drawingPrompts[1]) }
            </h3>
            <div className="text-center">
              <SketchPad ref={this.sketchPadRef} />
              <button
                onClick={this.submit}
                className="btn btn-primary mt-1">
                Submit drawing
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {
    gameCode: state.gameCode,
    drawingPrompts: state.drawingPrompts,
    situation: state.situation.drawing
  }
}

const mapDispatchToProps = {
  submitDrawing
};

export default connect(mapStateToProps, mapDispatchToProps)(DrawPrompts);
