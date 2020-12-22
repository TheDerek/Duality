import React from 'react';
import { increment, decrement, reset, getTodos } from "./actions";
import { connect } from 'react-redux'

class Counter extends React.Component {

  increment = () => {
    this.props.increment();
  };

  decrement = () => {
    this.props.decrement();
  };

  reset = () => {
    this.props.reset();
  };

  getTodos = () => {
    this.props.getTodos();
  };

  render() {
    return (
      <div>
        <h2>Counter</h2>
        <div>
          <button onClick={this.decrement}>-</button>
          <span>
            { this.props.count }
          </span>
          <button onClick={this.increment}>+</button>
          <br/>
          <button onClick={this.reset}>Reset</button>
          <br/>
          <button onClick={this.getTodos}>Get Todos</button>
          <div>
            <h2>Todos:</h2>
            <ol>
              {
                this.props.todos.map((todo, i) => {
                  return (<li key={i}>{todo}</li>);
                })
              }
            </ol>
          </div>
        </div>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {
    count: state.count,
    todos: state.todos
  };
}

const mapDispatchToProps = {
  increment,
  decrement,
  reset,
  getTodos
};

export default connect(mapStateToProps, mapDispatchToProps)(Counter);
