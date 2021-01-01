import React from "react";
import { connect } from "react-redux";

class DrawPrompts extends React.Component {
  render() {
    return (
     <p>Drawing prompts</p>
    )
  }
}

function mapStateToProps(state) {

}

const mapDispatchToProps = {

};

export default connect(mapStateToProps, mapDispatchToProps)(DrawPrompts);
