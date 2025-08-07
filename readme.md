venv\Scripts\activate 

pip freeze > requirements.txt

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

django-admin startproject config .

python manage.py startapp 

python manage.py createsuperuser

python manage.py runserver
EXAMPLE
ГГГГ-ММ-ДДTЧЧ:ММ пример 2025-08-05T21:30

кастомная команда отправки рассылок
python manage.py send_mailings

Создаёт группу Менеджеры с правами отключать рассылки и блокировать пользователей
python manage.py create_managers_group