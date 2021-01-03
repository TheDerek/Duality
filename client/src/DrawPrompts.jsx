import React from "react";
import { connect } from "react-redux";
import SketchPad from "./SketchPad";

class DrawPrompts extends React.Component {
  render() {
    return (
      <div>
        <h3 className="mb-4 text-center">Draw a hero that posses both strength and cunning</h3>
        <div className="text-center">
          <SketchPad/>
          <button className="btn btn-primary mt-1">Submit drawing</button>
        </div>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {

  }
}

const mapDispatchToProps = {

};

export default connect(mapStateToProps, mapDispatchToProps)(DrawPrompts);
