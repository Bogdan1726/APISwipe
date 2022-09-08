from django_filters import rest_framework as filters

from .models import Announcement, Apartment


class AnnouncementFilter(filters.FilterSet):
    price = filters.RangeFilter()
    area = filters.RangeFilter()

    class Meta:
        model = Announcement
        fields = [
            'price', 'area',
            'residential_complex__is_commissioning',
            'purpose', 'rooms', 'condition', 'payment_options',
        ]


class ApartmentFilter(filters.FilterSet):
    announcement__price = filters.RangeFilter()
    price_to_meter = filters.RangeFilter()
    announcement__area = filters.RangeFilter()

    class Meta:
        model = Apartment
        fields = [
            'announcement__price', 'announcement__area', 'price_to_meter',
            'announcement__condition', 'corpus', 'section', 'is_booked',
            'announcement__residential_complex'
        ]
