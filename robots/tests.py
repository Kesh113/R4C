from http import HTTPStatus
import json

from django.test import TestCase, Client
from django.urls import reverse

from .models import Robot


MODEL = 'R2'
VERSION = 'D2'
CREATED = '2022-12-31 23:59:59'


class CreateRobotTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('robots')

        self.data = {
            'model': MODEL,
            'version': VERSION,
            'created': CREATED
        }
        self.serial = f'{MODEL}-{VERSION}'

        self.invalid_data = '{"model": "R2", "version":,'
        '"created": "2022-12-31 23:59:59"}'

        self.missing_data = {'model': MODEL}

        self.content_type = 'application/json'

    def test_create_robot_success(self):
        response = self.client.post(
            self.url,
            data=json.dumps(self.data),
            content_type=self.content_type
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(response.json()['serial'], self.serial)
        self.assertTrue(Robot.objects.filter(serial=self.serial).exists())

    def test_create_robot_invalid_json(self):
        response = self.client.post(
            self.url,
            data=self.invalid_data,
            content_type=self.content_type
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn('value_error', response.json())

    def test_create_robot_missing_field(self):
        response = self.client.post(
            self.url,
            data=json.dumps(self.missing_data),
            content_type=self.content_type
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn('version', response.json())
        self.assertIn('created', response.json())
