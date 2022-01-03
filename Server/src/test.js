const userAction = async () => {
  const response = await fetch("http://127.0.0.1:5000/test", {
    method: "POST",
    body: { name: "pp" },
    headers: {
      "Content-Type": "application/json",
    },
  });
  const myJson = await response.json(); //extract JSON from the http response
  // do something with myJson
  console.log(myJson);
};
async function main() {
  const ans = await userAction();
  console.log("PP");
}
main();
