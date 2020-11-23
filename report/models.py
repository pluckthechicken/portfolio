"""Store each position as a historical data object.

Contains historical share prices which update each time the model is queried.
This improves efficiency since the data are only ever requested once.
All prices reflect daily close.
"""

import json
import pandas as pd
from datetime import datetime

from django.db import models
from django.contrib.postgres.fields import ArrayField

from . import finance, currency
from .colors import COLORS


class Position(models.Model):
    """Store historical share price data."""

    stock_code = models.CharField(max_length=15)
    buy_date = models.DateField()
    buy_price = models.FloatField()
    buy_qty = models.IntegerField()
    currency = models.CharField(max_length=10, default="USD")
    current = models.FloatField(null=True)
    holding = models.FloatField(null=True)
    series_x = ArrayField(models.DateField())
    series_y = ArrayField(models.FloatField(), null=True)
    date_updated = models.DateTimeField(auto_now=True)
    close_price = models.FloatField(null=True)
    date_closed = models.DateField(null=True)

    @classmethod
    def create(cls, stock_code, buy_date, buy_price, buy_qty, currency="USD"):
        """Fetch data and create new stock object."""
        p = cls.objects.create(
            stock_code=stock_code,
            buy_price=buy_price,
            buy_qty=buy_qty,
            series_x=[buy_date],
            buy_date=buy_date,
            currency=currency,
        )
        p.update()
        p.save()
        return p

    @classmethod
    def open(cls):
        """Return queryset of all open positions."""
        return cls.objects.filter(close_price__isnull=True)

    @classmethod
    def closed(cls):
        """Return queryset of all closed positions."""
        return cls.objects.exclude(close_price__isnull=True)

    @classmethod
    def render_report(cls):
        """Render data for portfolio report table."""
        positions = cls.objects.exclude(series_y__isnull=True)
        data = finance.format_for_render(positions)
        return data

    @classmethod
    def clean_duplicate_dates(cls):
        """Remove duplicate dates from each data series."""
        for p in cls.objects.all():
            df = pd.DataFrame(p.series_y, index=p.series_x)
            df = df.loc[~df.index.duplicated(keep='first')]
            p.series_x = list(df.index)
            p.series_y = list(df[0])
            p.save()

    @classmethod
    def refresh_all(cls):
        """Dump all data on open positions and refresh from API."""
        for p in cls.open():
            p.series_x = []
            p.series_y = []
            p.save()
            p.update()

    @classmethod
    def fetch_plot_json(cls):
        """Format stock P/L data for plotly."""
        def get_unique(base):
            """Make stock code unique by appending with number."""
            i = 2
            code = base
            while code in codes:
                code = base + f"_{i}"
                i += 1
            return code

        positions = cls.open().exclude(
            series_y__isnull=True).order_by('buy_date')
        data = []
        codes = []

        for i, position in enumerate(positions):
            series = {
                'type': 'scatter',
                'mode': 'lines',
                'line': {'color': COLORS[i]}
            }
            series['name'] = get_unique(position.stock_code)
            codes.append(series['name'])
            series['x'] = [
                datetime.strftime(x, '%Y-%m-%d') for x in position.series_x
            ]
            series['y'] = position.series_y
            data.append(series)
        return json.dumps(data)

    @classmethod
    def get(cls, stock, closed=False):
        """Get a position instance by stock_code."""
        positions = cls.objects.filter(stock_code__iexact=stock)
        if not closed:
            positions = positions.filter(close_price__isnull=True)
        return positions

    @classmethod
    def update_all(cls):
        """Call update() on all open positions."""
        for p in cls.open():
            p.update()

    def close(self, price, date):
        """Close the position after selling."""
        df = pd.DataFrame(self.series_y, index=self.series_x)
        df = df.loc[df.index < date]
        self.close_price = price
        self.date_closed = date
        self.holding = currency.exchange[self.currency](
            price * self.buy_qty
        )
        self.series_x = list(df.index) + [date]
        self.series_y = list(df[0]) + [price]
        self.save()

    def reopen(self):
        """Reopen the position after closing (i.e. closed by mistake)."""
        self.close_price = None
        self.date_closed = None
        self.save()
        self.update()
        print(f'{self.stock_code} has been reopened')

    def update(self):
        """Update the model with today's data."""
        close = finance.fetch_close(self)

        if close is None:
            print("Cannot fetch any more data for position %s today." %
                  self.stock_code)
            return

        if self.series_y is None:
            self.series_y = []

        PL = (close / self.buy_price - 1).round(2)
        self.series_x += list(PL.index)
        self.series_y += list(PL)

        # Don't know where this extra array item comes from
        # but it's super annoying!
        if len(self.series_x) > len(self.series_y):
            del self.series_x[-1]

        self.current = close.iloc[-1]
        self.holding = currency.exchange[self.currency](
            self.current * self.buy_qty
        )
        self.save()
