from collections import defaultdict
from http import HTTPStatus
import json

from django.db.models import Count
from django.http import FileResponse, HttpResponseNotAllowed, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .constants import INVALID_JSON, CREATE_SUCCESS, FILE_NAME
from .forms import RobotForm
from .models import Robot
from .utils import create_xls_analytics


def generate_file_name() -> str:
    """Генерирует имя файла с текущей датой."""
    return FILE_NAME.format(timezone.now().strftime("%d.%m.%Y"))


@csrf_exempt
def robots_view(request):
    """Запрос показателей производства и добавление робота в БД."""
    if request.method == 'GET':
        # Запрашиваем роботов, созданных за последнюю неделю,
        # агрегируем по модели и версии
        last_week_robots = (
            Robot.recent_objects
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
            create_xls_analytics(data),
            as_attachment=True,
            filename=generate_file_name()
        )

    elif request.method == 'POST':
        # Десериализуем полученные данные в словарь
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {'value_error': INVALID_JSON},
                status=HTTPStatus.BAD_REQUEST
            )

        # Проводим валидацию входных данных
        form = RobotForm(data)
        if not form.is_valid():
            return JsonResponse(form.errors, status=HTTPStatus.BAD_REQUEST)

        robot = form.save()

        return JsonResponse({
            'message': CREATE_SUCCESS,
            'serial': robot.serial
        }, status=HTTPStatus.CREATED)

    return HttpResponseNotAllowed(['get', 'post'])
