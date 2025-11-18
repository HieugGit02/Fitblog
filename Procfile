web: gunicorn fitblog_config.wsgi
release: python manage.py migrate && python manage.py collectstatic --noinput
