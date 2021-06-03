"""Functions to handle currency exchange."""

import requests
from django.conf import settings


class CurrencyRates:
    """Fetch current exchange rates for USD conversion."""

    ENDPOINT = "http://api.exchangeratesapi.io/v1/latest"

    def __init__(self):
        """Create request and fetch."""
        url = (
            f"{self.ENDPOINT}?access_key={settings.EXCHANGERATESAPI_KEY}"
            "&symbols=USD,GBP,AUD"
            "&format=1"
        )
        print(f"Request URL: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(
                "FX API request refused (https://api.exchangeratesapi.io)"
                f" (HTTP status {response.status_code})"
            )
        self.rates = response.json()['rates']

    def get_rate(self, currency):
        """Get conversion rate from USD to given currency."""
        usd = self.rates['USD']
        return self.rates[currency] / usd


def USD_to_USD(usd):
    """Blank function to return USD unaltered."""
    return round(usd, 2)


def GBX_to_USD(pence):
    """Convert GBP pence to USD."""
    c = CurrencyRates()
    rate = c.get_rate('GBP')
    return round((pence / 100) / rate, 2)


def GBP_to_USD(gbp):
    """Convert GBP to USD."""
    c = CurrencyRates()
    rate = c.get_rate('GBP')
    return round(gbp / rate, 2)


def AUD_to_USD(aud):
    """Convert AUD to USD."""
    c = CurrencyRates()
    rate = c.get_rate('AUD')
    return round(aud / rate, 2)


exchange = {
    "USD": USD_to_USD,
    "GBX": GBX_to_USD,
    "GBP": GBP_to_USD,
    "AUD": AUD_to_USD,
}
