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
      <div>
        <h3 className="mb-4 text-center">Draw a hero that posses both strength and cunning</h3>
        <div className="text-center">
          <SketchPad ref={this.sketchPadRef} />
          <button
            onClick={this.submit}
            className="btn btn-primary mt-1">
            Submit drawing
          </button>
        </div>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {
    gameCode: state.gameCode
  }
}

const mapDispatchToProps = {
  submitDrawing
};

export default connect(mapStateToProps, mapDispatchToProps)(DrawPrompts);
