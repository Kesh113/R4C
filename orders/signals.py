import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction

from .constants import MESSAGE, SUBJECT, UNSUCCESS_SEND_MAIL
from robots.models import Robot
from .models import Order


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
        send_email(customer, instance)
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


def send_email(customer, robot):
    """Отправка письма клиенту."""
    send_mail(
        subject=SUBJECT,
        message=MESSAGE.format(robot.model, robot.version),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[customer.email],
        fail_silently=False,
    )
