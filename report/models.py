from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Historical(models.Model):
    """ Store historical stock data """
    date_updated = models.DateTimeField(auto_now=True)
    stock = models.CharField(max_length=15)
    series_x = ArrayField(models.DateField())
    series_y = ArrayField(models.FloatField())
    buy_price = models.FloatField()
    buy_qty = models.IntegerField()
    current = models.FloatField()

    def update(self, series_x, series_y, current):
        """ Update the model with today's data """
        self.series_x = series_x
        self.series_y = series_y
        self.current = current
        self.save()
