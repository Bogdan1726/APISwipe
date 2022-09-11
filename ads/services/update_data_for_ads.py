from ads.models import Apartment


def update_or_create_apartment(instance):
    if instance.purpose == 'Квартира' and instance.is_moderation_check is True:
        Apartment.objects.update_or_create(
            announcement=instance,
        )
