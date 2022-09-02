from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.generics import get_object_or_404

from ads.models import Announcement, Apartment
from ads.services.initial_data_for_ads import create_data_for_ads


@receiver(post_save, sender=Announcement)
def post_save_announcement(created, **kwargs):
    instance = kwargs.get('instance')
    if created:
        create_data_for_ads(instance)
    else:
        """
        Calling the save apartment method to update the price per meter
        """
        if instance.purpose == 'Квартира':
            obj = get_object_or_404(Apartment, announcement=instance)
            obj.save()
