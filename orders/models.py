from django.db import models

from customers.models import Customer


class Order(models.Model):
    AVAILABLE_STATUS = [
        ('waiting', 'Ожидание'),
        ('booked', 'Забронирован'),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='orders'
    )
    robot_serial = models.CharField(max_length=5, blank=False, null=False)
    status = models.CharField(
        max_length=10, choices=AVAILABLE_STATUS, default='waiting'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'Order {self.id} - {self.robot_serial} for {self.customer.email}'
        )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = '-status', 'created_at'
        indexes = (models.Index(fields=['status', 'created_at']),)
        unique_together = ('customer', 'robot_serial')
