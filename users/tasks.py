from datetime import datetime, timedelta
from django.core.mail import send_mail
from .models import Subscription
from swipe.celery import app
import calendar

from .services.month_ahead import get_range_month


@app.task
def activate_user_subscription():
    """
    Renewing a user's subscription (is_auto_renewal=True)
    """
    print('task "activate_user_subscription" send')
    subscription = Subscription.objects.filter(is_auto_renewal=True, date_end__lt=datetime.now())
    subscription.update(date_end=get_range_month().date())
    print('task "activate_user_subscription" complete')


@app.task
def deactivate_user_subscription():
    """
    Deactivate the user's subscription after the end of the end date and send mail (is_auto_renewal=False)
    """
    print('task "deactivate_user_subscription" send')
    subscription = Subscription.objects.filter(is_auto_renewal=False, is_active=True, date_end__lt=datetime.now())
    send_mail('SWIPE',
              'Your subscription has expired',
              None,
              list(subscription.values_list('user__email', flat=True)),
              fail_silently=False
              )
    subscription.update(is_active=False)
    print('task "deactivate_user_subscription" complete')
