# R4C - Robots for consumers

## Небольшая предыстория.
Давным-давно, в далёкой-далёкой галактике, была компания производящая различных 
роботов. 

Каждый робот(**Robot**) имел определенную модель выраженную двух-символьной 
последовательностью(например R2). Одновременно с этим, модель имела различные 
версии(например D2). Напоминает популярный телефон различных моделей(11,12,13...) и его версии
(X,XS,Pro...). Вне компании роботов чаще всего называли по серийному номеру, объединяя модель и версию(например R2-D2).

Также у компании были покупатели(**Customer**) которые периодически заказывали того или иного робота. 

Когда роботов не было в наличии - заказы покупателей(**Order**) попадали в список ожидания.

---
## Что делает данный код?
Это заготовка для сервиса, который ведет учет произведенных роботов,а также 
выполняет некие операции связанные с этим процессом.

Сервис нацелен на удовлетворение потребностей трёх категорий пользователей:
- Технические специалисты компании. Они будут присылать информацию
- Менеджмент компании. Они будут запрашивать информацию
- Клиенты. Им будут отправляться информация
___

## Как с этим работать?
- Создать для этого проекта репозиторий на GitHub
- Открыть данный проект в редакторе/среде разработки которую вы используете
- Ознакомиться с задачами в файле tasks.md
- Написать понятный и поддерживаемый код для каждой задачи 
- Сделать по 1 отдельному PR с решением для каждой задачи
- Прислать ссылку на своё решение

## Установка

### Требования

- *Python* версии 3.12

### Шаги установки

1. *Клонирование репозитория*

```bash
git clone git@github.com:Kesh113/R4C.git
cd R4C
```

2. *Создание и активация виртуального окружения*

```bash
python -m venv venv
source venv/Scripts/activate
```

3. *Установка зависимостей*

```bash
pip install -r requirements.txt
```

4. *Миграции базы данных*

```bash
python manage.py migrate
```

5. *Запуск сервера*

```bash
python manage.py runserver
```

Сервер будет доступен по адресу `http://127.0.0.1:8000/`

6. *Добавление обязательных переменных окружения*

```bash
echo "EMAIL_HOST='your_SMTP'" > .env
echo "EMAIL_HOST_USER='your_email'" >> .env
echo "EMAIL_HOST_PASSWORD='your_email_pswrd'" >> .env
```

Все переменные необходимо заполнить личными данными

7. *Запуск тестов*

```bash
python manage.py test
```

## Примеры запросов к API

### Добавление робота в БД

*Запрос:*

```http
POST api/v1/robots/
Content-Type: application/json
```

```json
{
  "model": "R2",
  "version": "D2",
  "created": "2022-12-31 23:59:59"
}
```

*Ответ:*

```json
{
  "message": "Робот успешно добавлен в базу данных.",
  "serial": "R2-D2"
}
```

---
### Получение отчета об изготовлении роботов за последнюю неделю

*Запрос:*

```http
GET api/v1/robots/
Content-Type: application/json
```

*Ответ:*

Excel файл - 'Показатели производства {текущая дата}.xlsx'

---
### Создание заказа от клиента при наличии необходимого робота

*Запрос:*

```http
POST api/v1/to-book-robot/
Content-Type: application/json
```

```json
{
  "email": "user@user.ru",
  "robot_serial": "R2-D2"
}
```

*Ответ:*

```json
{
  "message": "Бронирование робота R2-D2 успешно. Ожидайте звонка от нашего менеджера в ближайшее время"
}
```

---
### Создание заказа от клиента при отсутствии необходимого робота

*Запрос:*

```http
POST api/v1/to-book-robot/
Content-Type: application/json
```

```json
{
  "email": "user@user.ru",
  "robot_serial": "R2-D2"
}
```

*Ответ:*

```json
{
  "message": "К сожалению робота R2-D2 в наличии нет. Вы получите уведомление на email, когда он появится."
}
```