let canv, WIDTH, HEIGHT;
let request_button, simulate_button, save_button;
let GLOBAL_SHAPE = 4;
let interval = true;
let queue;
let total_generations = 0;
function setup() {
  WIDTH = 128 * GLOBAL_SHAPE;
  HEIGHT = 128 * GLOBAL_SHAPE;
  canv = createCanvas(WIDTH, HEIGHT);
  canv.parent("canv_holder");

  request_button = createButton("Run Simulation");
  simulate_button = createButton("Stop requests");
  save_button = createButton("Save Generation");
  request_button.parent("butts");
  request_button.mousePressed(makeReqContinuous);
  // request_button.mousePressed(makeRequest);
  simulate_button.parent("butts");
  simulate_button.mousePressed(staph);
  save_button.parent("butts");
  save_button.mousePressed(saveData);
  noLoop();
  background(200);
}

let creatures = [];
function draw() {}

function staph() {
  // clearInterval(interval)
  interval = false;
}

function saveData() {
  fetch("http://127.0.0.1:5000/save")
    .then((response) => response.json())
    .then();
}

let survivors;
async function makeRequest() {
  const data = {
    gens: 10,
  };
  const userAction = async () => {
    const response = fetch("http://127.0.0.1:5000/test", {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
      },
    });
    // await sleep(2000);
    reset();
    const ress = await Promise.all([response]);
    const content_A = await ress[0].json();
    const content = content_A["d"];
    survivors = content_A["s"][0];
    total_generations = content_A["s"][1];
    // await addData(survivors / 10, total_generations);
    for (let frame of content) {
      crets = [];
      for (let ele of frame) {
        crets.push(new Creature(ele["x"], ele["y"], ele["g"]));
      }
      creatures.push(crets);
    }
  };
  await userAction();
  await simulate();

  total_generations++;
}

let secs = 5;
let delay = 2000;
async function makeReqContinuous() {
  if (interval == false) return;
  await makeRequest();

  setTimeout(makeReqContinuous, delay);
}

function simulate() {
  for (let i = 0; i < 300; i++) {
    setTimeout(() => {
      background(240);
      changeText(total_generations);
      simulateHelp(i);
    }, i * secs);
  }
}

function simulateHelp(i) {
  for (let ele of creatures[i]) {
    ele.draw();
  }
}

function changeText(n) {
  document.getElementById("score").innerHTML =
    "Gen: " +
    total_generations +
    " Survivors: " +
    survivors +
    " Rate: " +
    ((survivors / creatures[0].length) * 100).toPrecision(3) +
    "%";
}

function sleep(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}
function reset() {
  creatures = [];
}

function randint(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min) + min); //The maximum is exclusive and the minimum is inclusive
}

function hexx(num) {
  return num.toString(16);
}
const randColor = () => {
  let n = (Math.random() * 0xfffff * 1000000).toString(16);
  return "#" + n.slice(0, 6);
};
