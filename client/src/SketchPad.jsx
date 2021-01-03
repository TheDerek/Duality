import React from "react";

class SketchPad extends React.Component {
  constructor(props) {
    super(props);
    this.canvasRef = React.createRef();

    this.mousePos = {
      x: 0,
      y: 0
    }
    this.isDrawing = false;
    this.mouseInCanvas = false;
  }

  componentDidMount() {
    const canvas = this.canvasRef.current;
    const context = canvas.getContext("2d");

    canvas.addEventListener('mousedown', e => {
      context.beginPath();
      context.strokeStyle = 'black';
      context.lineWidth = 5;
      context.lineCap = "round";

      this.mousePos.x = e.offsetX;
      this.mousePos.y = e.offsetY;
      this.isDrawing = true;
    });

    canvas.addEventListener('mousemove', e => {
      if (this.isDrawing === true) {
        this.drawLine(context, this.mousePos.x, this.mousePos.y, e.offsetX, e.offsetY);
        this.mousePos.x = e.offsetX;
        this.mousePos.y = e.offsetY;
      }
    });

    canvas.addEventListener('mouseenter', e => {
      this.mouseInCanvas = true;
    });

    canvas.addEventListener('mouseout', e => {
      this.mouseInCanvas = false;
      this.isDrawing = false;
      context.closePath();
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

  drawLine(context, x1, y1, x2, y2) {
    context.moveTo(x1, y1);
    context.lineTo(x2, y2);
    context.stroke();
    //context.closePath();
  }

  clearCanvas = (e) => {
    e.preventDefault();

    const canvas = this.canvasRef.current;
    canvas.getContext("2d").clearRect(0, 0, canvas.height, canvas.width);
  }

  render() {
    return (
      <div>
        <button type="button" className="btn btn-outline-secondary me-2">Undo</button>
        <button onClick={this.clearCanvas} type="button" className="btn btn-outline-secondary">Clear</button>
        <div className="mt-2 mb-2"/>
        <canvas height="400" width="400" ref={this.canvasRef} className="border rounded"/>
      </div>
    )
  }
}

export default SketchPad;