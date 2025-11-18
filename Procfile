web: gunicorn fitblog_config.wsgi
release: python manage.py migrate --noinput || true && python manage.py collectstatic --clear --noinput
