// let canv, WIDTH, HEIGHT;
// let request_button, simulate_button;
// let GLOBAL_SHAPE = 4;
// let interval = true;
// let queue;
// function setup() {
//   WIDTH = 128 * GLOBAL_SHAPE;
//   HEIGHT = 128 * GLOBAL_SHAPE;
//   canv = createCanvas(WIDTH, HEIGHT);
//   canv.parent("canv_holder");

//   request_button = createButton("request");
//   simulate_button = createButton("simulate");
//   request_button.parent("butts");
//   request_button.mousePressed(makeReqContinuous);
//   // request_button.mousePressed(makeRequest);
//   simulate_button.parent("butts");
//   simulate_button.mousePressed(staph);
//   noLoop();
//   background(200);
// }

// let creatures = [];
// function draw() {
//   // for (let frame of creatures) {
//   //   await sleep(1000);
//   //   background(200);
//   //   for (let ele of frame) {
//   //     ele.draw();
//   //   }
//   // }
//   // background(200);
// }

// function staph() {
//   // clearInterval(interval)
//   interval = false;
// }

// async function makeReqContinuous() {
//   if (interval == false) return;
//   await makeRequest();
//   setTimeout(makeReqContinuous, 4000);
// }

// async function makeRequest() {
//   const data = {
//     gens: 10,
//   };
//   const userAction = async () => {
//     const response = fetch("http://127.0.0.1:5000/test", {
//       method: "POST",
//       body: JSON.stringify(data),
//       headers: {
//         "Content-Type": "application/json",
//       },
//     });
//     // await sleep(2000);
//     reset();
//     const ress = await Promise.all([response]);
//     const content = await ress[0].json();
//     for (let frame of content) {
//       crets = [];
//       for (let ele of frame) {
//         crets.push(new Creature(ele["x"], ele["y"], ele["g"]));
//       }
//       creatures.push(crets);
//     }
//     // for (let ele of content) {
//     //   creatures.push(new Creature(ele["x"], ele["y"], ele["g"]));
//     // }
//     // console.log(content);
//   };
//   await userAction();
//   await simulate();
// }
// async function simulate() {
//   for (let i = 0; i < 300; i++) {
//     await setTimeout(() => {
//       background(240);
//       simulateHelp(i);
//     }, i * 5);
//   }
// }

// function simulateHelp(i) {
//   for (let ele of creatures[i]) {
//     ele.draw();
//   }
// }
// function sleep(ms) {
//   return new Promise((resolve) => {
//     setTimeout(resolve, ms);
//   });
// }
// function reset() {
//   creatures = [];
// }

function randint(min, max) {
  min = Math.ceil(min);
  max = Math.floor(max);
  return Math.floor(Math.random() * (max - min) + min); //The maximum is exclusive and the minimum is inclusive
}

function hex(num) {
  return num.toString(16);
}
function randColor() {
  return `#${hex(randint(0, 255))}${hex(randint(0, 255))}${hex(
    randint(0, 255)
  )}`;
}
console.log(randColor());
