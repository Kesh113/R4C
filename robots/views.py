from collections import defaultdict
from datetime import timedelta
from http import HTTPStatus
import json

from django.db.models import Count
from django.http import FileResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .forms import RobotForm
from .models import Robot
from .utils import create_xls_analytics


INVALID_JSON = 'Некорректный JSON.'
CREATE_SUCCESS = 'Робот успешно добавлен в базу данных.'
INVALID_METHOD = 'Запросы кроме GET и POST запрещены.'


HEADER_FORMAT_DATA = {'bold': True, 'bg_color': '#D3D3D3', 'border': 1}
FILE_HEADERS = ['Модель', 'Версия', 'Количество за неделю']
FILE_NAME = ('Показатели производства {}.xlsx')


def generate_file_name() -> str:
    """Генерирует имя файла с текущей датой."""
    return FILE_NAME.format(timezone.now().strftime("%d.%m.%Y.%M"))


@csrf_exempt
def robots_view(request):
    """Запрос показателей производства и добавление робота в БД"""
    if request.method == 'GET':
        # Запрашиваем роботов, созданных за последнюю неделю,
        # агрегируем по модели и версии
        last_week_robots = (
            Robot.objects
            .filter(created__gte=timezone.now() - timedelta(weeks=1))
            .values('model', 'version')
            .annotate(count=Count('id'))
            .order_by('model', 'version')
        )

        # Организуем данные в формате
        # {model: [{'version': version, 'count': count}]}
        data = defaultdict(list)
        for robot in last_week_robots:
            data[robot['model']].append({
                'version': robot['version'],
                'count': robot['count']
            })

        return FileResponse(
            create_xls_analytics(data, HEADER_FORMAT_DATA, FILE_HEADERS),
            as_attachment=True,
            filename=generate_file_name()
        )

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {'value_error': INVALID_JSON},
                status=HTTPStatus.BAD_REQUEST
            )

        form = RobotForm(data)

        if not form.is_valid():
            return JsonResponse(form.errors, status=HTTPStatus.BAD_REQUEST)

        robot = form.save()

        return JsonResponse({
            'message': CREATE_SUCCESS,
            'serial': robot.serial
        }, status=HTTPStatus.CREATED)

    return JsonResponse(
        {'method_error': INVALID_METHOD}, status=HTTPStatus.METHOD_NOT_ALLOWED
    )
