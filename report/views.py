"""Serves a single 'homepage' view showing portfolio overview.

Also shows an update view which updates static content and then redirects back
to the homepage.
"""

from datetime import datetime

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from .models import Position
from .forms import CreatePositionForm


def home(request):
    """Show stock/shares portfolio status as graphs and tables."""
    if request.method == "POST":
        form = CreatePositionForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'report/index.html', {
                'stocks': Position.render_report(),
                'plotData': Position.fetch_plot_json(),
                'form': form,
                }
            )

    return render(request, 'report/index.html', {
        'stocks': Position.render_report(),
        'plotData': Position.fetch_plot_json(),
        'form': CreatePositionForm(),
        }
    )


def close_position(request):
    """Handle request to close a position."""
    try:
        p = Position.objects.get(id=request.POST['position_id'])
    except ObjectDoesNotExist:
        return HttpResponse(status=404)

    close_date = datetime.strptime(
        request.POST['close_date'], '%Y-%m-%d').date()
    p.close(
        float(request.POST['close_price']),
        close_date,
    )
    return redirect('/')
