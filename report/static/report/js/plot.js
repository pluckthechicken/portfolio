const mobile = window.innerWidth < 576;

function plot() {

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
        y: mobile ? -0.15 : 0.5,
        xanchor: mobile ? 'center' : 'left',
        yanchor: mobile ? 'top' : 'center',
        font: {
          color: '#FFFFFF',
          size: mobile ? 12 : 18,
        },
      },

      margin: {
        l: 25,
        r: 10,
        b: 25,
        t: 35,
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
      },
    );
}
