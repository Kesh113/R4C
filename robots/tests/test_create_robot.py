from http import HTTPStatus
import json

from .fixtures import (
    BaseRobotTest, INVALID_JSON_DATA, CONTENT_TYPE_JSON, REQUIRED_FIELD
)
from robots.models import Robot


class CreateRobotTestCase(BaseRobotTest):
    def test_create_robot_success(self):
        """Сравниваем отправленные тестовые данные с полученными данными."""
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_data),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(response.json().get('serial'), self.valid_serial)
        self.assertIsNotNone(
            Robot.objects.get(serial=self.valid_serial)
        )

    def test_create_robot_invalid_json(self):
        """Сравниваем отправленный некорректный JSON с полученным ответом."""
        response = self.client.post(
            self.url,
            data=INVALID_JSON_DATA,
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn('value_error', response.json())

    def test_create_robot_missing_field(self):
        """Сравниваем недозаполненные обязательными полями данные
        с полученным ответом."""
        response = self.client.post(
            self.url,
            data=json.dumps(self.missing_fields_data),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        response_data = response.json()
        self.assertIn('version', response_data)
        self.assertEqual(response_data['version'], [REQUIRED_FIELD])
        self.assertIn('created', response_data)
        self.assertEqual(response_data['created'], [REQUIRED_FIELD])
