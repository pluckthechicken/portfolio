"""Check recent changes in share price.

Sends a notification if losses above threshold.
"""

import smtplib
import schedule
from time import sleep
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings

# Django init
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portfolio.settings")
django.setup()
from django.apps import apps
Position = apps.get_model('report', 'Position')


def send_email(toaddr, body):
    """Send an email notification."""
    fromaddr = 'porkmymonkey@gmail.com'
    msg = MIMEMultipart('alternative')
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'GBP/USD alert'
    msg.attach(MIMEText(body, 'text', 'UTF-8'))
    server = smtplib.SMTP('localhost')
    server.sendmail(fromaddr, toaddr, msg.as_string())
    server.quit()


def notify():
    """Check all open positions and notify if loss above threshold."""
    for p in Position.objects.exclude(series_y__isnull=False):
        if len(p.series_y) > 10:
            close = p.series_y[-10:]
        else:
            close = p.series_y

        for i, price in enumerate(close):
            days = settings.WATCH_DAYS - i
            PL = p.current / price
            if PL < (settings.LOSS_THRESHOLD / -100):   # > 2% loss
                address = 'pluckthechicken@hotmail.co.uk'
                msg = (' fell by %.2f%% in the last %s days.' %
                       (p.stock_code, PL, days))
                print("Sending email to %s:" % address)
                print(msg)
                send_email(address, msg)
                break


schedule.every().day.at("08:00").do(notify)

while True:
    schedule.run_pending()
    sleep(300)
