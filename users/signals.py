from users.services.initial_data_for_user import create_agent, create_subscription, create_residential_complex
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save

User = get_user_model()


@receiver(post_save, sender=User)
def post_save_user(created, **kwargs):
    instance = kwargs.get('instance')
    if created:
        if instance.is_developer:
            create_residential_complex(instance)
        else:
            if instance.is_developer is False:
                create_agent(instance)
                create_subscription(instance)
