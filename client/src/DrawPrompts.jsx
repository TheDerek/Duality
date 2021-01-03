import React from "react";
import { connect } from "react-redux";
import SketchPad from "./SketchPad";

class DrawPrompts extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div>
        <h3 className="mb-4">Draw a hero that posses both strength and cunning</h3>
        <div className="text-center">
          <SketchPad/>
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
