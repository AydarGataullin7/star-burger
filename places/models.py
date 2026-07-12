from django.db import models


class Place(models.Model):
    address = models.CharField(
        max_length=255, unique=True, verbose_name='Адрес')
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Широта')
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Долгота')
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'

    def __str__(self):
        return self.address
