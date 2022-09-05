from django_filters import rest_framework as filters

from .models import Apartment


class ApartmentFilter(filters.FilterSet):
    announcement__price = filters.RangeFilter()
    announcement__area = filters.RangeFilter()

    class Meta:
        model = Apartment
        fields = [
            'announcement__price',
            'announcement__area',
            'announcement__residential_complex__is_commissioning',
            'announcement__purpose',
            'announcement__rooms'
        ]
