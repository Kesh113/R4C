from django import forms

from .models import Order
from .constants import REPEAT_ORDER
from customers.models import Customer


class OrderForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Order
        fields = 'robot_serial', 'email'

    def clean(self):
        cleaned_data = super().clean()

        # Если оба поля присутствуют, проверяем на дублирование
        if Order.objects.filter(
            robot_serial=cleaned_data.get('robot_serial'),
            customer__email=cleaned_data.get('email'),
        ).exists():
            self.add_error('email', REPEAT_ORDER)

        return cleaned_data

    def save(self, commit=True):
        # Извлекаем email из очищенных данных
        email = self.cleaned_data['email']

        # Получаем или создаем клиента
        customer, _ = Customer.objects.get_or_create(email=email)

        # Присваиваем клиента заказу
        self.instance.customer = customer

        return super().save(commit=commit)
