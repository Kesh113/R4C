from http import HTTPStatus
import json

from robots.constants import INVALID_JSON

from .fixtures import (
    BaseRobotTest, INVALID_JSON_DATA, CONTENT_TYPE_JSON, REQUIRED_FIELD
)
from robots.models import Robot


class CreateRobotTestCase(BaseRobotTest):
    def post_json(self, url, data):
        return self.client.post(
            url,
            data=data,
            content_type=CONTENT_TYPE_JSON
        )

    def test_create_robot_success(self):
        """Проверяем успешность создания робота."""
        response = self.post_json(self.url, json.dumps(self.valid_data))

        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(response.json().get('serial'), self.valid_serial)
        robots = Robot.objects.all()
        self.assertEqual(robots.count(), 1)
        robot = robots.first()
        self.assertEqual(robot.serial, self.valid_serial)
        self.assertEqual(robot.model, self.valid_data['model'])
        self.assertEqual(robot.version, self.valid_data['version'])
        self.assertEqual(robot.created.isoformat(), self.valid_data['created'])
        self.assertEqual(robot.status, 'available')

    def test_create_robot_invalid_json(self):
        """Проверяем ответ при некорректном JSON."""
        response = self.post_json(self.url, INVALID_JSON_DATA)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn('value_error', response.json())
        self.assertEqual(response.json().get('value_error'), INVALID_JSON)

    def test_create_robot_missing_field(self):
        """Проверяем наличие обязательных полей в запросе."""
        response = self.post_json(self.url, json.dumps({}))
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        response_data = response.json()
        for field in ['model', 'version', 'created']:
            self.assertIn(field, response_data)
            self.assertEqual(response_data[field], [REQUIRED_FIELD])
