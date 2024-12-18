from http import HTTPStatus
import json

from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseNotAllowed

from .constants import (
    INVALID_JSON, ROBOT_SOLD, ORDER_PROCESS_ERROR, SUCCESS_BOOKED
)
from orders.forms import OrderForm
from robots.models import Robot


@csrf_exempt
def order_process(request):
    """Процесс бронирования робота."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    # Десериализуем полученные данные в словарь
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {'value_error': INVALID_JSON},
            status=HTTPStatus.BAD_REQUEST
        )

    form = OrderForm(data)

    if not form.is_valid():
        return JsonResponse(form.errors, status=HTTPStatus.BAD_REQUEST)

    order = form.save(commit=False)

    robot_serial = form.cleaned_data.get('robot_serial')

    try:
        with transaction.atomic():
            # Попытка получить робота со статусом "доступен"
            robot = Robot.objects.select_for_update().filter(
                serial=robot_serial, status='available'
            ).first()

            if not robot:
                raise Robot.DoesNotExist

            # Обновляем статусы на забронирован
            order.status = 'booked'
            order.save()

            robot.status = 'booked'
            robot.save()

    except Robot.DoesNotExist:
        # Нет доступного для бронирования робота
        order.save()
        return JsonResponse(
            {'message': ROBOT_SOLD.format(robot_serial)},
            status=HTTPStatus.CREATED
        )
    except Exception:
        return JsonResponse(
            {'error': ORDER_PROCESS_ERROR},
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )

    return JsonResponse(
        {'message': SUCCESS_BOOKED.format(robot_serial)},
        status=HTTPStatus.CREATED
    )
