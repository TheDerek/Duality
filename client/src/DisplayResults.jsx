import React from "react";
import { connect } from "react-redux";

import { submitDrawing } from "./actions"
import SketchPad from "./SketchPad";

class DisplayResults extends React.Component {
  constructor(props) {
    super(props);
  }


  render() {
    return (
      <div>
        <h3 className="mb-4 text-center">Displaying results!</h3>
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

export default connect(mapStateToProps, mapDispatchToProps)(DisplayResults);
