import {connect} from "react-redux";
import React from "react";

class Errors extends React.Component {
  render() {
    if (this.props.errors.length < 1) {
      return null;
    }

    return (
      <div className="alert alert-danger">
        <ul className="mb-0">
          {
            this.props.errors.map((error, i) => <li key={i}>{error}</li>)
          }
        </ul>
      </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    errors: state.errors,
  }
}

export default connect(mapStateToProps)(Errors);
