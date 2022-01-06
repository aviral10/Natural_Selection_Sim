class Creature {
  constructor(x, y, z) {
    this.x = x;
    this.y = y;
    this.genome = z;
  }

  draw() {
    let xpos = this.y * GLOBAL_SHAPE;
    let ypos = this.x * GLOBAL_SHAPE;
    // xpos += GLOBAL_SHAPE / 2;
    // ypos += GLOBAL_SHAPE / 2;
    fill(this.genome);
    noStroke();
    // noStroke();
    // square(xpos, ypos, GLOBAL_SHAPE);
    ellipseMode(CORNER);
    circle(xpos, ypos, GLOBAL_SHAPE);
    // console.log(xpos, ypos);
  }
}
