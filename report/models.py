"""Store each position as a historical data object.

Contains historical share prices which update each time the model is queried.
This improves efficiency since the data are only ever requested once.
All prices reflect daily close.
"""

import json
from datetime import date, datetime
import pandas_datareader as pdr

from django.db import models
from django.contrib.postgres.fields import ArrayField

COLOURS = [
    'orange',   # EVX
    'red',      # GWPH
    'green',    # QCLN
    'blue',
    'purple',
    'grey',
    'yellow',
    'maroon',
    'cyan',
    'brown',
    'black',
]


class Position(models.Model):
    """Store historical share price data."""

    date_updated = models.DateTimeField(auto_now=True)
    stock_code = models.CharField(max_length=15)
    series_x = ArrayField(models.DateField())
    series_y = ArrayField(models.FloatField())
    buy_price = models.FloatField()
    buy_qty = models.IntegerField()
    current = models.FloatField()
    holding = models.FloatField()

    @classmethod
    def create(cls, stock_code, buy_date, buy_price, buy_qty):
        """Fetch data and create new stock object."""
        dfs = pdr.get_data_yahoo(
            stock_code,
            start=buy_date,
            end=date.today()
        )
        close = dfs['Close']
        PL = (close / buy_price - 1).round(2)
        return cls.objects.create(
            stock_code=stock_code,
            buy_price=buy_price,
            buy_qty=buy_qty,
            series_x=list(PL.index),
            series_y=list(PL),
            current=close.iloc[-1],
            holding=round(close.iloc[-1] * buy_qty, 2)
        )

    @classmethod
    def get_all(cls):
        """Update and return all stocks."""
        positions = cls.objects.all()
        for p in positions:
            p.update()
        return positions

    @classmethod
    def render_report(cls):
        """Render data for portfolio report."""
        def usd_fmt(value):
            """Comma-separate values over $10 and return string formatted."""
            if value < 10000:
                return '$%.2f' % value
            x = '%.2f' % value
            x, y = x.split('.')
            return '$%s,%s.%s' % (x[:-3], x[-3:], y)

        data = {}
        total_pl = 0
        init_holdings = 0
        total_holdings = sum(cls.objects.all().values_list(
            "holding", flat=True))

        for p in cls.objects.all():
            print('Loading data for %s' % p.stock_code)
            pl = (p.current - p.buy_price) / p.buy_price
            pl_pc = 100 * pl
            init_holding = p.buy_qty * p.buy_price
            init_holdings += init_holding
            pl_usd = init_holding * pl
            total_pl += (pl_usd * p.holding / total_holdings)
            data[p.stock_code] = [
                '%.2f' % p.buy_price,
                '%s' % p.buy_qty,
                '%.2f' % p.current,
                usd_fmt(p.holding),
                usd_fmt(pl_usd),
                '%.2f %%' % pl_pc,
                'plus' if pl_pc > 0 else 'minus',
            ]

        data['Total'] = [
            usd_fmt(init_holdings),
            '',
            '',
            usd_fmt(total_holdings),
            usd_fmt(total_pl),
            '%.2f %%' % (100 * total_pl / init_holdings),
            'total',
        ]

        return data

    @classmethod
    def fetch_plot_json(cls):
        """Fetch stock P/L data and format for plotly."""
        positions = cls.get_all().order_by('stock_code')
        colours = COLOURS[:len(positions)]
        data = []

        for position, clr in zip(positions, colours):
            series = {
                'type': 'scatter',
                'mode': 'lines',
                'line': {'color': clr}
            }
            series['name'] = position.stock_code
            series['x'] = [
                datetime.strftime(x, '%Y-%m-%d') for x in position.series_x
            ]
            series['y'] = position.series_y
            data.append(series)
        return json.dumps(data)

    def update(self):
        """Update the model with today's data."""
        def fetch_close():
            date_from = self.series_x[-1]
            dfs = pdr.get_data_yahoo(
                self.stock_code,
                start=date_from,
                end=date.today()
            )
            # Remove duplicate dates (causes a bug)
            dfs = dfs.loc[~dfs.index.duplicated(keep='first')]
            if len(dfs):
                return dfs['Close']

        close = fetch_close()
        if close is None:
            return
        PL = (close / self.buy_price - 1).round(2)
        self.series_x += list(PL.index)
        self.series_y += list(PL)
        self.current = close.iloc[-1]
        self.holding = round(self.current * self.buy_qty, 2)
        self.save()
