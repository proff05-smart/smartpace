echo "<<<<<<<<<<< COLLECTING STATIC FILES >>>>>>>>"
python manage.py collectstatic --noinput

echo "<<<<<<<<<<< STARTING PROJECT >>>>>>>>>>>>>>"
#gunicorn smartpace.wsgi
daphne -p 8000 smartpace.asgi:application