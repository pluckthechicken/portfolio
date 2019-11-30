import os
import matplotlib
from matplotlib import pyplot as plt
import pandas_datareader as pdr
from datetime import datetime
from pandas.plotting import register_matplotlib_converters

from django.shortcuts import render, redirect
from django.conf import settings

from .models import Historical

register_matplotlib_converters()
matplotlib.use('Agg')

fpath = os.path.join(
    settings.BASE_DIR,
    'report',
    'static',
    'report',
    'img',
    'portfolio.png',
)

# Create your views here.
def home(request):
    """ Show historical trend of stocks as graphs and tables """
    def usd_fmt(value):
        """ Comma-separate values over $10 and return string formatted """
        if value < 10000:
            return '$%.2f' % value
        x = '$%.2f' % value
        x,y = x.split('.')
        return 'US$%s,%s.%s' % (x[:-3], x[-3:-1], y)

    if not os.path.exists(fpath):
        return redirect('/update')

    data = {}
    total_holding = 0
    total_pl = 0

    for h in  Historical.objects.all():
        print('Loading data for %s' % h.stock)
        current = h.current
        pl_pc = 100 * (current - h.buy_price) / h.buy_price
        holding = h.buy_qty * h.buy_price
        pl_usd = holding * (pl_pc / 100)
        total_holding += holding
        total_pl += pl_usd
        data[h.stock] = [
            '%.2f' % h.buy_price,
            '%s' % h.buy_qty,
            '%.2f' % current,
            usd_fmt(holding),
            '%.2f %%' % pl_pc,
            usd_fmt(pl_usd),
            'plus' if pl_pc > 0 else 'minus',
        ]

    data['Total'] = [
        '','','',
        '$%.2f' % total_holding,'',
        '$%.2f' % total_pl,''
    ]

    return render(request, 'report/index.html', {'stocks': data})

def plot_history(request=None):
    """ Plot relative stock P/L from date of purchase """
    plt.style.use('fivethirtyeight')

    fig = plt.figure(figsize=(8,6))
    s1 = plt.subplot(111)

    s = datetime(2019,10,10)
    e = datetime.today()

    stocks = Historical.objects.all()

    colours = [
        'black',
        'grey',
        'blue',
        'brown',
        'green',
        'orange',
        'purple',
        'yellow',
        'maroon',
        'cyan',
    ][:len(stocks)]

    for stock, clr in zip(stocks, colours):
        dfs = pdr.get_data_yahoo(stock.stock, start=s, end=e)
        close = dfs['Close']
        pl = close / close.iloc[0] - 1
        s1.plot(pl.index, pl, linestyle='solid', linewidth=2, label=stock.stock)
        stock.update(list(pl.index), list(pl), close.iloc[-1])

    s1.plot(pl.index, [0 for x in pl.index], 'k-', linewidth=1)
    s1.set_yticklabels(['%.2f %%' % (100 * x) for x in s1.get_yticks()])
    plt.xticks(rotation=80)
    plt.tight_layout()
    plt.legend(fontsize=12)
    txt = 'Updated %s' % datetime.today().strftime('%d-%m-%Y')
    plt.text(pl.index[0], plt.ylim()[0] * 0.9, txt, color='#999999')

    if not os.path.exists(os.path.dirname(fpath)):
        os.makedirs(os.path.dirname(fpath))

    plt.savefig(fpath, dpi=300, facecolor='w')
    return redirect('/') if request else None
