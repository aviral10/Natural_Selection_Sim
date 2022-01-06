let ctx = document.getElementById("canvas").getContext("2d");

const DATA_COUNT = 7;
Chart.defaults.global.defaultFontSize = 15;
const labels = [0];
const data = {
  labels: labels,
  datasets: [
    {
      label: "Survival Rate over the last 50 generations",
      data: [0],
    },
  ],
};
let options = {
  //   responsive: true,
  //   maintainAspectRatio: false,
};

const config = {
  type: "line",
  data: data,
  options: {
    responsive: false,
    maintainAspectRatio: false,
    aspectRatio: 0.5,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: "Line Chart",
      },
    },
    scales: {
      xAxes: [
        {
          display: true,
          scaleLabel: {
            display: true,
            labelString: "Generation",
          },
        },
      ],
      yAxes: [
        {
          display: true,
          ticks: {
            beginAtZero: true,
            steps: 10,
            stepValue: 5,
            max: 100,
          },
        },
      ],
    },
  },
};

// let chart = new Chart(ctx, config);

async function addData(val, lab) {
  const data = chart.data;
  data.labels.push(lab);
  data.datasets[0].data.push(val);
  if (data.labels.length > 50) {
    data.labels.shift();
    data.datasets[0].data.shift();
  }
  await chart.update();
}
