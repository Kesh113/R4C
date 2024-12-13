import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from robots.forms import RobotForm


INVALID_JSON = 'Некорректный JSON.'
CREATE_SUCCESS = 'Робот успешно добавлен в базу данных.'
INVALID_METHOD = 'Запросы кроме POST запрещены.'


@csrf_exempt
def robot(request):
    '''Добавление робота в базу данных'''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {'value_error': INVALID_JSON},
                status=400
            )

        form = RobotForm(data)

        if not form.is_valid():
            return JsonResponse(form.errors, status=400)

        robot = form.save()

        return JsonResponse({
            'message': CREATE_SUCCESS,
            'serial': robot.serial
        }, status=201)

    return JsonResponse(
        {'method_error': INVALID_METHOD}, status=405
    )
