from django.dispatch import receiver
from django.db.models.signals import post_save
from housing.models import ResidentialComplex
from housing.services.initial_data_for_complex import create_data_for_residential_complex


@receiver(post_save, sender=ResidentialComplex)
def post_save_residential_complex(created, **kwargs):
    instance = kwargs.get('instance')
    if created:
        create_data_for_residential_complex(instance)
