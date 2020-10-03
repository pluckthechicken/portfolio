"""Store each position as a historical data object.

Contains historical share prices which update each time the model is queried.
This improves efficiency since the data are only ever requested once.
All prices reflect daily close.
"""

import json
from datetime import date, datetime, timedelta
import pandas_datareader as pdr
from forex_python.converter import CurrencyRates

from django.db import models
from django.contrib.postgres.fields import ArrayField

COLOURS = [
    'white',
    '#feb71a',
    '#ff4422',
    '#46f068',
    '#3388ff',
    '#c940f5',
    '#00ffe0',
    '#91c781',
    '#ff8dc8',
    '#f11a67',
    '#f4fc43',
]

class Position(models.Model):
    """Store historical share price data."""

    date_updated = models.DateTimeField(auto_now=True)
    stock_code = models.CharField(max_length=15)
    buy_price = models.FloatField()
    buy_qty = models.IntegerField()
    currency = models.CharField(max_length=10, default="USD")
    current = models.FloatField(null=True)
    holding = models.FloatField(null=True)
    series_x = ArrayField(models.DateField())
    series_y = ArrayField(models.FloatField(), null=True)

    @classmethod
    def create(cls, stock_code, buy_date, buy_price, buy_qty, currency="USD"):
        """Fetch data and create new stock object."""
        p = cls.objects.create(
            stock_code=stock_code,
            buy_price=buy_price,
            buy_qty=buy_qty,
            series_x=[buy_date],
            currency=currency,
        )
        try:
            p.update()
        except ValueError:
            print("Cannot update %s until tomorrow" % stock_code)
        p.save()
        return p

    @classmethod
    def render_report(cls):
        """Render data for portfolio report table."""
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
        positions = cls.objects.exclude(series_y__isnull=True)
        total_holdings = sum(positions.values_list("holding", flat=True))

        for p in positions:
            pl = (p.current - p.buy_price) / p.buy_price
            pl_pc = 100 * pl
            init_holding = exchange[p.currency](p.buy_qty * p.buy_price)
            init_holdings += init_holding
            pl_usd = init_holding * pl
            total_pl += pl_usd
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
        positions = cls.objects.exclude(
            series_y__isnull=True).order_by('stock_code')
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

    @classmethod
    def update_all(cls):
        """Call update() on all instances."""
        for p in cls.objects.all():
            p.update()

    def update(self):
        """Update the model with today's data."""
        def fetch_close():
            date_from = self.series_x[-1] + timedelta(days=1)
            if date_from >= date.today():
                return
            dfs = pdr.get_data_yahoo(
                self.stock_code,
                start=date_from,
                end=date.today()
            )
            # Remove duplicate dates (causes a small bug)
            dfs = dfs.loc[~dfs.index.duplicated(keep='first')]
            if len(dfs):
                return dfs['Close']

        close = fetch_close()

        if close is None:
            print("Cannot fetch any more data for position %s today." %
                  self.stock_code)
            return
        if self.series_y is None:
            self.series_y = []

        PL = (close / self.buy_price - 1).round(2)
        self.series_x += list(PL.index)
        self.series_y += list(PL)
        self.current = close.iloc[-1]
        self.holding = exchange[self.currency](
            self.current * self.buy_qty
        )
        self.save()


def USD_to_USD(usd):
    """Blank function to return USD unaltered."""
    return round(usd, 2)


def GBX_to_USD(pence):
    """Convert GBP pence to USD."""
    c = CurrencyRates()
    rate = c.get_rate('GBP', 'USD')
    return round((pence / 100) / rate, 2)


def AUD_to_USD(aud):
    """Convert AUD to USD."""
    c = CurrencyRates()
    rate = c.get_rate('AUD', 'USD')
    return round(aud / rate, 2)


exchange = {
    "USD": USD_to_USD,
    "GBX": GBX_to_USD,
    "AUD": AUD_to_USD,
}
