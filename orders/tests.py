from http import HTTPStatus
import json

from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

from .constants import (
    INVALID_JSON, REPEAT_ORDER, ROBOT_SOLD,
    SUBJECT, SUCCESS_BOOKED, NOT_SEND, REQUIRED_FIELD
)
from orders.models import Order
from robots.models import Robot


EMAIL = 'user@user.ru'
SERIAL = 'R2-D2'
CONTENT_TYPE_JSON = 'application/json'

INVALID_JSON_DATA = '{"email": "user@user.ru", "robot_serial":,'


class OrderProcessTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.robots_url = reverse('robots')
        cls.to_book_url = reverse('to-book-robot')

        cls.valid_order_data = {'email': EMAIL, 'robot_serial': SERIAL}
        cls.valid_robot_data = {
            'model': 'R2',
            'version': 'D2',
            'created': '2022-12-31 23:59:59'
        }

    def post_json(self, url, data):
        return self.client.post(
            url,
            data=json.dumps(data),
            content_type=CONTENT_TYPE_JSON
        )

    def assertOrderExists(self, email, serial, status):
        order = Order.objects.filter(
            customer__email=email,
            robot_serial=serial,
            status=status
        )
        self.assertEqual(order.count(), 1)

    def test_create_order_success(self):
        """Проверяем успешность создания заказа с и
        без бронирования робота."""
        test_cases = [
            {
                'description': 'without_robot',
                'robot': False,
                'expected_message': ROBOT_SOLD.format(SERIAL),
                'expected_order_status': 'waiting'
            },
            {
                'description': 'with_robot',
                'robot': True,
                'expected_message': SUCCESS_BOOKED.format(SERIAL),
                'expected_order_status': 'booked'
            },
        ]

        for case in test_cases:
            with self.subTest(case=case['description']):
                Order.objects.all().delete()

                if case['robot']:
                    self.post_json(self.robots_url, self.valid_robot_data)

                response = self.post_json(
                    self.to_book_url, self.valid_order_data
                )

                self.assertEqual(response.status_code, HTTPStatus.CREATED)
                self.assertEqual(
                    response.json().get('message'),
                    case['expected_message']
                )
                self.assertOrderExists(
                    EMAIL, SERIAL, case['expected_order_status']
                )

    def test_receive_email(self):
        """Проверяем корректность сообщения о появлении робота
        после его добавления."""
        self.post_json(self.to_book_url, self.valid_order_data)
        order = Order.objects.get(customer__email=EMAIL, robot_serial=SERIAL)

        response_robot = self.post_json(self.robots_url, self.valid_robot_data)
        self.assertEqual(response_robot.status_code, HTTPStatus.CREATED)

        self.assertEqual(len(mail.outbox), 1, NOT_SEND)

        sent_mail = mail.outbox[0]
        self.assertEqual(sent_mail.subject, SUBJECT)
        self.assertIn(self.valid_robot_data['model'], sent_mail.body)
        self.assertIn(self.valid_robot_data['version'], sent_mail.body)
        self.assertEqual(sent_mail.to, [EMAIL])

        # Проверяем обновление статусов
        order.refresh_from_db()
        self.assertEqual(order.status, 'booked')

        robot = Robot.objects.get(serial=SERIAL)
        self.assertEqual(robot.status, 'booked')

    def test_create_repeat_order_waiting(self):
        """Проверяем отсутствие возможности дублирования заявки
        в статусе ожидания."""
        self.post_json(self.to_book_url, self.valid_order_data)
        response = self.post_json(self.to_book_url, self.valid_order_data)

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json().get('email'), [REPEAT_ORDER])
        self.assertOrderExists(EMAIL, SERIAL, 'waiting')

    def test_create_order_invalid_json(self):
        """Проверяем ответ при некорректном JSON."""
        response = self.client.post(
            self.to_book_url,
            data=INVALID_JSON_DATA,
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        response_data = response.json()
        self.assertIn('value_error', response_data)
        self.assertEqual(response_data.get('value_error'), INVALID_JSON)

    def test_create_order_missing_field(self):
        """Проверяем наличие обязательных полей в запросе."""
        response = self.post_json(self.to_book_url, {})

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        response_data = response.json()
        for field in ['email', 'robot_serial']:
            self.assertIn(field, response_data)
            self.assertEqual(response_data[field], [REQUIRED_FIELD])
