"""Functions to handle currency exchange."""

from forex_python.converter import CurrencyRates


def USD_to_USD(usd):
    """Blank function to return USD unaltered."""
    return round(usd, 2)


def GBX_to_USD(pence):
    """Convert GBP pence to USD."""
    c = CurrencyRates()
    rate = c.get_rate('GBP', 'USD')
    return round((pence / 100) / rate, 2)


def GBP_to_USD(gbp):
    """Convert GBP to USD."""
    c = CurrencyRates()
    rate = c.get_rate('GBP', 'USD')
    return round(gbp / rate, 2)


def AUD_to_USD(aud):
    """Convert AUD to USD."""
    c = CurrencyRates()
    rate = c.get_rate('AUD', 'USD')
    return round(aud / rate, 2)


exchange = {
    "USD": USD_to_USD,
    "GBX": GBX_to_USD,
    "GBP": GBP_to_USD,
    "AUD": AUD_to_USD,
}
