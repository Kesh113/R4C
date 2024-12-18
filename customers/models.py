from django.db import models


class Customer(models.Model):
    email = models.CharField(
        max_length=255, blank=False, null=False, unique=True
    )

    def __str__(self):
        return self.email[:21]

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
