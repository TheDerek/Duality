import React from "react";
import {connect} from "react-redux";

class WaitingRoom extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div>
        Waiting room!
      </div>
    )
  }
}

export default connect()(WaitingRoom);