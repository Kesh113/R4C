import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from .constants import MESSAGE, SUBJECT, UNSUCCESS_SEND_MAIL
from .models import Order
from robots.models import Robot


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Robot)
def notify_client_on_robot_creation(sender, instance, created, **kwargs):
    """Оповещение клиента о создании ожидаемого робота."""
    if not created:
        return  # Только при добавлении роботов

    # Выбираем первый попавшийся заказ на робота "в ожидании"
    order = Order.objects.filter(
        robot_serial=instance.serial, status='waiting'
    ).first()

    if not order:
        return  # Заказов для робота нет

    customer = order.customer

    # Пытаемся отправить сообщение на email клиента
    try:
        send_email(customer.email, instance.model, instance.version)
    except Exception as error:
        # Логирование ошибки при отправке письма
        logger.error(
            UNSUCCESS_SEND_MAIL.format(customer.email, error), exc_info=True
        )
        return  # При ошибке отправки статусы заказа и робота не меняем

    with transaction.atomic():
        # Обновляем статусы на забронирован
        instance.status = 'booked'
        instance.save()

        order.status = 'booked'
        order.save()


def send_email(customer_email, robot_model, robot_version):
    """Асинхронная отправка письма клиенту."""
    send_mail(
        subject=SUBJECT,
        message=MESSAGE.format(robot_model, robot_version),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[customer_email],
        fail_silently=False,
    )
