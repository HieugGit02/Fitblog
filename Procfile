web: gunicorn fitblog_config.wsgi
release: python manage.py migrate --noinput; python manage.py collectstatic --clear --noinput
