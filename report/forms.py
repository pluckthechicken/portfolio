"""Forms for interacting with portfolio positions."""

from django import forms
from django.core.exceptions import ValidationError

from . import finance
from .models import Position


class CreatePositionForm(forms.Form):
    """Open a new position."""

    stock_code = forms.CharField(max_length=10)
    buy_date = forms.DateField()
    buy_price = forms.FloatField()
    buy_qty = forms.IntegerField()
    currency = forms.CharField()

    def clean(self):
        """Validate form data."""
        data = self.cleaned_data
        data['stock_code'] = data['stock_code'].upper()
        if not finance.confirm_stock_code(data['stock_code']):
            raise ValidationError({
                'stock_code': 'Stock code not recognised by YahooDailyReader'
            })

        return data

    def save(self):
        """Save form as Position instance."""
        Position.create(
            stock_code=self.cleaned_data['stock_code'],
            buy_date=self.cleaned_data['buy_date'],
            buy_price=self.cleaned_data['buy_price'],
            buy_qty=self.cleaned_data['buy_qty'],
            currency=self.cleaned_data['currency'],
        )
