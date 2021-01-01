import React from "react";
import ReactDOM from "react-dom";
import { connect } from "react-redux";
import CanvasDraw from "react-canvas-draw";

class DrawPrompts extends React.Component {
  constructor(props) {
    super(props);

    this.canvas = <CanvasDraw
      canvasWidth={400}
      canvasHeight={400}
      lazyRadius={0}
      hideGrid={true}/>;

  }

  render() {
    return (
      <div>
        <div className="card mt-4">
          <div className="card-body">
            <h5 className="card-title mb-3 text-center">
              Draw a hero that posses both strength and cunning
            </h5>
            <div className="w-100 d-flex justify-content-center">
              <div className="border">
                { this.canvas }
              </div>
            </div>
          </div>
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
