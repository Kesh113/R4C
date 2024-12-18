from django.db import models

from .utils import get_created_date, get_serial


class LastWeekManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            created__gte=get_created_date(7)
        )


class Robot(models.Model):
    AVAILABLE_STATUS = [
        ('booked', 'Забронирован'),
        ('available', 'Доступен'),
    ]

    serial = models.CharField(max_length=5, blank=False, null=False)
    model = models.CharField(max_length=2, blank=False, null=False)
    version = models.CharField(max_length=2, blank=False, null=False)
    created = models.DateTimeField(blank=False, null=False)
    status = models.CharField(
        max_length=10, choices=AVAILABLE_STATUS, default='available'
    )

    objects = models.Manager()
    recent_objects = LastWeekManager()

    def save(self, *args, **kwargs):
        self.serial = get_serial(self.model, self.version)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Робот'
        verbose_name_plural = 'Роботы'
        ordering = 'serial',
        indexes = (models.Index(fields=['serial']),)

    def __str__(self):
        return f'{self.serial=}, {self.id=}'
