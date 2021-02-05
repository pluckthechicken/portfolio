// Plot positions chart

function plot() {
  const mobile = window.innerWidth < 576;
  const legend_y_mobile = 1.0 + plotData.length * 0.03;

  const layout = {
    plot_bgcolor:"#232524",
    paper_bgcolor:"#232524",

    xaxis: {
      type: 'date',
      color: 'white',
      tickfont: {
        size: mobile ? 10 : 18,
      },
    },

    yaxis: {
      tickformat: ',.0%',
      color: 'white',
      tickfont: {
        size: mobile ? 10 : 18,
      },
    },

    legend: {
      x: mobile ? 0.5 : 1.05,
      y: mobile ? legend_y_mobile : 0.5,
      xanchor: mobile ? 'center' : 'left',
      yanchor: mobile ? 'top' : 'center',
      orientation: mobile ? 'h' : 'v',
      font: {
        color: '#FFFFFF',
        size: mobile ? 12 : 18,
      },
    },

    margin: {
      l: mobile ? 25 : 50,
      r: mobile ? 10 : 20,
      b: mobile ? 25 : 50,
      t: mobile ? 80 : 60,
      pad: mobile ? 5 : 15,
    },
  };

  Plotly.newPlot(
    'chart-div',
    plotData,
    layout,
    {
      responsive: true,
      scrollZoom: mobile,
      displaylogo: false,
    },
  );
}
