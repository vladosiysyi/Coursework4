
venv\Scripts\activate 

pip freeze > requirements.txt

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

django-admin startproject config .

python manage.py startapp 

python manage.py createsuperuser

запуск виртокр
venv\Scripts\activate 
установка зависимостей
pip install -r requirements.txt
запуск сервера
python manage.py runserver
пример даты в создании рассылки
ГГГГ-ММ-ДДTЧЧ:ММ пример 2025-08-05T21:30

