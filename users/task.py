from django.core.mail import send_mail
from swipe.celery import app


@app.task
def send_invite_user():
    print('task send')
    send_mail('Приглашение в CRM 24', 'text',
              None,
              ['bogdan24ro@gmail.com'],
              fail_silently=False
              )
    print('Task completed')
