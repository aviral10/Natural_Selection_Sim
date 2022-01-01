const express = require("express");
var cors = require("cors");
const app = express();
app.use(cors());
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.get("/", (req, res) => {
  console.log("Hit at /");
  res.send("Home page");
});

app.get("/about", (req, res) => {
  console.log("Hit at /about");
  res.send("About page");
});

generations = [];
function generateAll() {
  let n = 1000;
  for (let i = 0; i < n; i++) {
    gen = [];
    for (let j = 0; j < 128; j++) {
      genn = [];
      for (let k = 0; k < 128; k++) {
        genn.push(Math.random());
      }
      gen.push(genn);
    }
    generations.push(gen);
  }
}
generateAll();
app.post("/test", (req, res) => {
  const name = req.body;
  console.log(name);
  return res.json(generations);
});

app.all("*", (req, res) => {
  res.status(404).send("Resource not found");
});

app.listen(5000, () => {
  console.log("Listening at port on port: 5000");
});

// function sleep(ms) {
//     return new Promise((resolve) => {
//         setTimeout(resolve, ms);
//     });
// }
