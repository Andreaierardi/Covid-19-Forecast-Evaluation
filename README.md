# Covid-19-Forecast-Evaluation



Template used: https://github.com/app-generator/django-dashboard-corona-dark


## Run server locally
``` pyhon 
$ # Install modules - SQLite Storage
  
$ pip3 install -r requirements.txt

$

$ # Create tables

$ python manage.py makemigrations

$ python manage.py migrate

$

$ # Start the application (development mode)

$ python manage.py runserver # default port 8000

$

$ # Start the app - custom port

$ # python manage.py runserver 0.0.0.0:<your_port>

$

$ # Access the web app in browser: http://127.0.0.1:8000/

```
