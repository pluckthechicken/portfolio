#!/usr/bin/env python3

import smtplib
import pandas_datareader as pdr
from datetime import date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(toaddr, body):
    fromaddr = 'porkmymonkey@gmail.com'
    msg = MIMEMultipart('alternative')
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'GBP/USD alert'
    msg.attach(MIMEText(body, 'text', 'UTF-8'))
    server = smtplib.SMTP('localhost')
    server.sendmail(fromaddr, toaddr, msg.as_string())
    server.quit()


WATCH_DAYS = 10     # Check change over last X days
LOSS_THRESHOLD = 2  # Report losses over X%

qcln = pdr.get_data_yahoo(
    "QCLN",
    start=date.today() - timedelta(days=WATCH_DAYS),
    end=date.today()
)
close = qcln['Close']
current = close[-1]

for i, price in enumerate(close):
    days = WATCH_DAYS - i
    PL = current / price
    if PL < (LOSS_THRESHOLD / -100):   # over 2% loss
        address = 'pluckthechicken@hotmail.co.uk'
        msg = 'QCLN fell by %.2f%% in the past %s days.' % (PL, days)
        print("Sending email to %s:" % address)
        print(msg)
        send_email(address, msg)
        break
