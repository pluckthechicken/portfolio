"""Serves a single 'homepage' view showing portfolio overview.

Also shows an update view which updates static content and then redirects back
to the homepage.
"""

from django.shortcuts import render
from .models import Position


def home(request):
    """Show historical trend of stocks as graphs and tables."""
    Position.update_all()
    return render(request, 'report/index.html', {
        'stocks': Position.render_report(),
        'plotData': Position.fetch_plot_json(),
        }
    )
