from django_filters import rest_framework as filters

from .models import Apartment


class ApartmentFilter(filters.FilterSet):
    price = filters.RangeFilter()
    price_to_meter = filters.RangeFilter()
    area = filters.RangeFilter()

    class Meta:
        model = Apartment
        fields = ['price', 'price_to_meter', 'area', 'decoration', 'residential_complex']

