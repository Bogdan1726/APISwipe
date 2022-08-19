from users.models import Contact, Subscription


def create_sales_department(instance):
    Contact.objects.create(
        type='Отдел продаж',
        user=instance
    )


def create_agent(instance):
    Contact.objects.create(
        type='Контакты агента',
        user=instance
    )


def create_subscription(instance):
    Subscription.objects.create(
        is_active=False,
        is_auto_renewal=False,
        user=instance
    )
