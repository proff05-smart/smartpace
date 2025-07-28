echo "<<<<<<<<<<< COLLECTING STATIC FILES >>>>>>>>"
python manage.py collectstatic --noinput

echo "<<<<<<<<<<< STARTING PROJECT >>>>>>>>>>>>>>"
#gunicorn smartpace.wsgi
#daphne smartpace.asgi:application
#daphne smartpace.asgi:application
daphne -b 0.0.0.0 -p 8000 smartpace.asgi:application

