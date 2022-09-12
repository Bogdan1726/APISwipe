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
#

# management commands
generate_builder_users:
	$(MANAGE) generate_builder_users

generate_test_users:
	$(MANAGE) generate_test_users

generate_test_ads:
	$(MANAGE) generate_test_ads

create_superuser:
	$(MANAGE) create_superuser
#

# endregion local


# Docker

start_worker:
	celery -A $(PROJECT) worker -l info


start_beat:
	celery -A $(PROJECT) beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler


start_app:
	$(MANAGE) migrate --no-input
	$(MANAGE) collectstatic --no-input
	$(MANAGE) generate_test_users
	$(MANAGE) generate_builder_users
	$(MANAGE) generate_test_ads
	$(MANAGE) create_superuser
	gunicorn swipe.wsgi:application --bind 0.0.0.0:8000



#