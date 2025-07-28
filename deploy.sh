echo "<<<<<<<<<<< COLLECTING STATIC FILES >>>>>>>>"
python manage.py collectstatic --noinput

echo "<<<<<<<<<<< STARTING PROJECT >>>>>>>>>>>>>>"
gunicorn smartpace.wsgi
#daphne smartpace.asgi:application