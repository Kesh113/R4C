from django.test import TestCase, Client
from django.urls import reverse

from robots.models import Robot
from robots.utils import get_created_date, get_serial


RECENT_ROBOTS = [
    {'model': 'R2', 'version': 'D2', 'created': get_created_date(1)},
    {'model': 'R2', 'version': 'D2', 'created': get_created_date(2)},
    {'model': 'R2', 'version': 'B1', 'created': get_created_date(2)},
    {'model': 'M5', 'version': 'C3', 'created': get_created_date(3)},
    {'model': 'C3', 'version': 'V6', 'created': get_created_date(2)},
    {'model': 'C3', 'version': 'V6', 'created': get_created_date(10)}
]

INVALID_JSON_DATA = ('{"model": "R2", "version":,"created": '
                     '"2022-12-31 23:59:59"}')

CONTENT_TYPE_XML = ('application/vnd.openxmlformats-officedocument'
                    '.spreadsheetml.sheet')
CONTENT_TYPE_JSON = 'application/json'

REQUIRED_FIELD = 'Обязательное поле.'


class BaseRobotTest(TestCase):
    """Базовый класс для тестов приложения Robot."""
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.url = reverse('robots')

        valid_robot = RECENT_ROBOTS[0]
        cls.valid_data = {
            'model': valid_robot['model'],
            'version': valid_robot['version'],
            'created': valid_robot['created']
        }
        cls.valid_serial = get_serial(
            cls.valid_data['model'], cls.valid_data['version']
        )

        cls.missing_fields_data = {'model': valid_robot['model']}

        # Создание роботов
        cls.recent_robots = Robot.objects.bulk_create(
            (Robot(**robot_data) for robot_data in RECENT_ROBOTS)
        )
