from housing.models import ResidentialComplex
from users.models import Contact, Subscription


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


def create_residential_complex(instance):
    ResidentialComplex.objects.create(
        name='Название',
        description='Описание',
        address='Адрес',
        map_lat=46.50218445984062,
        map_lon=30.738351206725632,
        distance=0,
        ceiling_height=2.5,
        user=instance
    )

