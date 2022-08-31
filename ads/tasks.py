from django.core.mail import send_mail
from .models import Advertising
from datetime import datetime
from swipe.celery import app


@app.task
def deactivate_announcement_advertising():
    """
    Deactivate announcement advertising after the end date
    """
    print('task "deactivate_announcement_advertising" send')
    advertising = Advertising.objects.filter(is_active=True, date_end__lt=datetime.now())
    send_mail('SWIPE',
              'Your advertising has expired',
              None,
              list(advertising.values_list('announcement__creator__email', flat=True)),
              fail_silently=False
              )
    print(list(advertising.values_list('announcement__creator__email', flat=True)))
    advertising.update(is_active=False)
    print('task "deactivate_announcement_advertising" complete')
