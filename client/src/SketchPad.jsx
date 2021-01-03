import React from "react";

class SketchPad extends React.Component {
  constructor(props) {
    super(props);

    this.colors = [
      {
        name: "Black",
        value: "#191919"
      },
      {
        name: "Red",
        value: "#F8333C"
      },
      {
        name: "Yellow",
        value: "#FCAB10"
      },
      {
        name: "Green",
        value: "#44AF69"
      },
      {
        name: "Blue",
        value: "#2B9EB3"
      },
      {
        name: "Grey",
        value: "#DBD5B5"
      }
    ]

    this.thicknesses = [
      {
        name: "Thin",
        value: 2
      },
      {
        name: "Medium",
        value: 5
      },
      {
        name: "Thick",
        value: 7
      }
    ]

    this.state = {
      selectedColor: this.colors[0]
    }

    this.canvasRef = React.createRef();

    this.mousePos = {
      x: 0,
      y: 0
    }
    this.isDrawing = false;
    this.mouseInCanvas = false;
    this.justEntered = false;
    this.strokes = [];
  }

  componentDidMount() {
    const canvas = this.canvasRef.current;
    const context = canvas.getContext("2d");

    context.strokeStyle = this.state.selectedColor.value;
    context.lineWidth = 5;
    context.lineCap = "round";

    canvas.addEventListener('mousedown', e => {
      this.mousePos.x = e.offsetX;
      this.mousePos.y = e.offsetY;

      this.beginStroke(context);
    });

    canvas.addEventListener('mousemove', e => {
      if (this.isDrawing === true) {
        this.drawLine(context, this.mousePos.x, this.mousePos.y, e.offsetX, e.offsetY);
        this.mousePos.x = e.offsetX;
        this.mousePos.y = e.offsetY;
      }
    });

    canvas.addEventListener('mouseenter', e => {
      this.justEntered = true;
    });

    window.addEventListener('mouseup', e => {
      if (this.isDrawing === true) {
        this.drawLine(context, this.mousePos.x, this.mousePos.y, e.offsetX, e.offsetY);
        this.mousePos.x = 0;
        this.mousePos.y = 0;
        this.isDrawing = false;

        context.closePath();
      }
    });
  }

  beginStroke(context) {
    context.beginPath();
    context.strokeStyle = this.state.selectedColor.value;
    this.isDrawing = true;
    this.strokes.push({
      color: this.state.selectedColor.value,
      lines: []
    });
  }

  drawLine(context, x1, y1, x2, y2) {
    let xm = x1;
    let ym = y1;

    if (this.justEntered) {
      this.justEntered = false;
      xm = x2;
      ym = y2;
    }

    this.strokes[this.strokes.length -1].lines.push({
      moveTo: {x: xm, y: ym},
      lineTo: {x: x2, y: y2}
    });

    context.moveTo(xm, ym);
    context.lineTo(x2, y2);
    context.stroke();
  }

  clearCanvas = (e) => {
    e.preventDefault();

    const canvas = this.canvasRef.current;
    canvas.getContext("2d").clearRect(0, 0, canvas.height, canvas.width);
    this.strokes = [];
  }

  redrawCanvas() {
    // First clear the canvas
    const canvas = this.canvasRef.current;
    const context = canvas.getContext("2d");
    context.clearRect(0, 0, canvas.height, canvas.width);

    this.strokes.forEach(stroke => {
      context.beginPath();
      context.strokeStyle = stroke.color

      stroke.lines.forEach(line => {
        context.moveTo(line.moveTo.x, line.moveTo.y);
        context.lineTo(line.lineTo.x, line.lineTo.y);
        context.stroke();
      });
      context.closePath();
    });
  }

  undo = () => {
    if (this.strokes.length < 1) {
      return;
    }

    this.strokes.pop();
    this.redrawCanvas();
  }

  setColor = (colorName) => {
    return () => {
      console.log("Setting color to " + colorName)
      this.setState({
        ...this.state,
        selectedColor: this.colors.find(color => color.name === colorName)
      })
    };
  }

  render() {
    return (
      <div>
        <button onClick={this.clearCanvas} type="button" className="btn btn-outline-secondary me-2">Clear</button>
        <button onClick={this.undo} type="button" className="btn btn-outline-secondary me-2">Undo</button>
        <div className="dropdown d-inline-block">
          <button
            className="btn btn-outline-secondary me-2 dropdown-toggle"
            data-bs-toggle="dropdown">
            <span style={{color: this.state.selectedColor.value}} className="me-2">&#11044;</span>
            Colour&nbsp;
          </button>
          <ul className="dropdown-menu">
            {
              this.colors.map((color, index) => (
                <li key={index}>
                  <button
                    onClick={this.setColor(color.name)}
                    className="dropdown-item">
                    <span style={{color: color.value}} className="me-2">&#11044;</span> { color.name }
                  </button>
                </li>
              ))
            }
          </ul>
        </div>
        <div className="dropdown d-inline-block">
          <button
            className="btn btn-outline-secondary me-2 dropdown-toggle"
            data-bs-toggle="dropdown">
            <span style={{color: this.state.selectedColor.value}} className="me-2">&#11044;</span>
            Thickness
          </button>
          <ul className="dropdown-menu">
            {
              this.thicknesses.map((thickness, index) => (
                <li key={index}>
                  <button
                    // onClick={this.setColor(color.name)}
                    className="dropdown-item">
                    <span className="me-2">&#11044;</span> { thickness.name }
                  </button>
                </li>
              ))
            }
          </ul>
        </div>
        <div className="mt-2 mb-2"/>
        <canvas height="400" width="400" ref={this.canvasRef} className="border rounded"/>
      </div>
    )
  }
}

export default SketchPad;