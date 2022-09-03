from django.dispatch import receiver
from django.db.models.signals import post_save
from ads.models import Announcement
from ads.services.initial_data_for_ads import create_data_for_ads
from ads.services.update_data_for_ads import update_or_create_apartment


@receiver(post_save, sender=Announcement)
def post_save_announcement(created, **kwargs):
    instance = kwargs.get('instance')
    if created:
        create_data_for_ads(instance)
    else:
        update_or_create_apartment(instance)

