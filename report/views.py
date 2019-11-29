import pandas_datareader as pdr
from datetime import datetime
from matplotlib import pyplot as plt

from django.shortcuts import render

from .models import Historical

# Create your views here.
def index(request):
    """ Show historical trend of stocks as graphs and tables """
    data = {}
    for stock in settings.STOCKS:
        d = Historical.objects.get(stock=stock)
        current = d.y_data[-1]
        pl_pc = 100 * (1 - current / d.buy_price)
        data[stock] = [d.buy_price, current, pl_pc, pl_usd]
    return render(request, 'report/index.html', data)

def plot_history():
    """ Plot relative stock P/L from date of purchase """
    plt.style.use('fivethirtyeight')

    fig = plt.figure(figsize=(8,6))
    s1 = plt.subplot(111)

    s = datetime(2019,10,10)
    e = datetime.today()

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
    ][:len(settings.STOCKS)]

    for stock, clr in zip(settings.STOCKS, colours):
        dfs = pdr.get_data_yahoo(stock, start=s, end=e)
        close = dfs['Close']
        pl = close / close.iloc[0] - 1
        s1.plot(pl.index, pl, linestyle='solid', linewidth=2)
        data = Historical.objects.get(stock=stock)
        data.update(list(pl.index), list(pl))

    s1.plot(pl.index, [0 for x in pl.index], 'r-', linewidth=1)
    s1.set_yticklabels(['%.2f %%' % x for x in s1.get_yticks()])
    plt.xticks(rotation=80)
    plt.tight_layout()
    fname = os.path.join(settings.BASE_DIR,'staticfiles','portfolio.png')
    plt.savefig(fname, dpi=300)
