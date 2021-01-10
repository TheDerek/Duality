import React from "react";
import { connect } from "react-redux";

import { submitDrawing } from "./actions"
import SketchPad from "./SketchPad";

class AssignPrompts extends React.Component {
  constructor(props) {
    super(props);
  }


  render() {
    return (
      <div>
        <h3 className="text-center">What weaknesses does this monster have?</h3>
        <p className="text-center"><em>Drawing 1 / 4</em></p>
        <div className="text-center mb-4">
          <img
            className="border mw-100"
            src={ this.props.drawing }
            />
        </div>
        <div className="">
          <div className="row row-cols-1 row-cols-sm-3">
            <div className="col text-center d-grid mb-3">
              <button type="button" className="btn btn-outline-primary">{ this.props.player.private.prompts[0] }</button>
            </div>
            <div className="col text-center d-grid mb-3">
              <button type="button" className="btn btn-outline-primary">{ this.props.player.private.prompts[1] }</button>
            </div>
            <div className="col text-center d-grid mb-3">
              <button type="button" className="btn btn-outline-secondary">
                Nothing that I can identify
              </button>
            </div>
          </div>
        </div>
        <div className="alert alert-warning" role="alert">
          Each drawing matches exactly two player submitted prompts. <b>You can only use
          each prompt once</b>, so pick carefully! If you don't believe that
          you have a prompt to match the drawing choose <em>Nothing that I can identify
          </em> and you can save your prompts for another drawing.
        </div>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {
    player: state.currentPlayer,
    drawing: state.drawing
  }
}

const mapDispatchToProps = {

};

export default connect(mapStateToProps, mapDispatchToProps)(AssignPrompts);
