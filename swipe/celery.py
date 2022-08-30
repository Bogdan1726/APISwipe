from celery.schedules import crontab
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swipe.settings')
app = Celery('swipe')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-every-day-in-00:00-for-activate': {
        'task': 'users.tasks.activate_user_subscription',
        'schedule': crontab(minute=0, hour=0),
    },

    'check-every-day-in-00:00-for-deactivate': {
        'task': 'users.tasks.deactivate_user_subscription',
        'schedule': crontab(minute=0, hour=0),
    },
    'check-every-day-in-00:00-for-deactivate_adv': {
        'task': 'ads.tasks.deactivate_announcement_advertising',
        'schedule': crontab(minute=0, hour=0),
    },
}
app.conf.timezone = 'Europe/Kiev'
