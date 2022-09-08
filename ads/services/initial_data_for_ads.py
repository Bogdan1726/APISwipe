from ads.models import Advertising, Apartment


def create_data_for_ads(instance):
    Advertising.objects.create(
        announcement=instance
    )
    if instance.purpose == 'Квартира' and instance.is_moderation_check is True:
        Apartment.objects.create(
            announcement=instance, number=instance.id
        )
