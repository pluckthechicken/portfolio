"""Serves a single 'homepage' view showing portfolio overview.

Also shows an update view which updates static content and then redirects back
to the homepage.
"""

import os
import json
import pandas_datareader as pdr
from datetime import date, datetime

from django.shortcuts import render

from .models import Historical


start = datetime(2019, 10, 10)
end = datetime.today()


def home(request):
    """Show historical trend of stocks as graphs and tables."""
    def usd_fmt(value):
        """Comma-separate values over $10 and return string formatted."""
        if value < 10000:
            return '$%.2f' % value
        x = '%.2f' % value
        x, y = x.split('.')
        return '$%s,%s.%s' % (x[:-3], x[-3:], y)

    plot_data = fetch_plot_json()

    data = {}
    init_holdings = 0
    total_holding = 0
    total_pl = 0

    for h in Historical.objects.all():
        print('Loading data for %s' % h.stock)
        current = h.current
        pl_pc = 100 * (current - h.buy_price) / h.buy_price
        holding = h.buy_qty * current
        init_holding = h.buy_qty * h.buy_price
        init_holdings += init_holding
        pl_usd = init_holding * (pl_pc / 100)
        total_holding += holding
        total_pl += pl_usd
        data[h.stock] = [
            '%.2f' % h.buy_price,
            '%s' % h.buy_qty,
            '%.2f' % current,
            usd_fmt(holding),
            usd_fmt(pl_usd),
            '%.2f %%' % pl_pc,
            'plus' if pl_pc > 0 else 'minus',
        ]

    data['Total'] = [
        usd_fmt(init_holdings),
        '',
        '',
        usd_fmt(total_holding),
        usd_fmt(total_pl),
        '%.2f %%' % (100 * total_pl / init_holdings),
        'total',
    ]

    pl = total_holding / init_holdings
    yearfrac = 365 / (end - start).days

    return render(request, 'report/index.html', {
        'stocks': data,
        'plotData': plot_data,
        'projected': usd_fmt(init_holdings * (pl ** yearfrac)),
        'yearfrac': '%.0f' % (100 / yearfrac),
        }
    )


def fetch_plot_json():
    """Fetch stock P/L data and format for plotly."""
    def fetch_data(stocks):
        for stock in stocks:
            dfs = pdr.get_data_yahoo(stock.stock, start=start, end=end)
            close = dfs['Close']
            pl = close / close.iloc[0] - 1
            stock.update(list(pl.index), list(pl), close.iloc[-1])

    stocks = Historical.objects.all().order_by('stock')
    data = []

    colours = [
        'brown',   # EVX
        'red',     # GWPH
        'blue',    # IXN
        'orange',  # MOAT
        'green',   # QCLN
        'purple',  # SPY
        'grey',
        'yellow',
        'maroon',
        'cyan',
        'black',
    ][:len(stocks)]

    if stocks[0].series_x[-1] < date.today():
        # Hasn't been updated today
        fetch_data(stocks)

    for stock, clr in zip(stocks, colours):
        series = {'type': 'scatter', 'mode': 'lines', 'line': {'color': clr}}
        series['name'] = stock.stock
        series['x'] = [
            datetime.strftime(x, '%Y-%m-%d') for x in stock.series_x
        ]
        series['y'] = stock.series_y
        data.append(series)

    return json.dumps(data)
