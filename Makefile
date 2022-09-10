MANAGE = python manage.py
PROJECT = swipe

# region local
run:
	$(MANAGE) runserver

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

superuser:
	$(MANAGE) createsuperuser

test:
	$(MANAGE) test

# Celery
start_worker:
	celery -A $(PROJECT) worker -l info

start_beat:
	celery -A $(PROJECT) beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

# endregion local



# Docker

#start_worker:
#	celery -A myhause24 worker -l info
#
#start_app:
#	$(MANAGE) migrate --no-input
#	$(MANAGE) loaddata dump.json
#	$(MANAGE) collectstatic --no-input
#	gunicorn myhause24.wsgi:application --bind 0.0.0.0:8000

#shell:
#	docker exec -it container_cinema python manage.py shell
#
#dump_data:
#	docker exec -it container_cinema python manage.py loaddata db.json