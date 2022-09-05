from django.contrib.auth import get_user_model
from rest_framework import serializers

from housing.models import ResidentialComplex
from housing.serializers import GalleryResidentialComplexSerializer
from users.services.month_ahead import get_range_month
from .models import (
    Announcement, Advertising, GalleryAnnouncement, Complaint, Apartment
)

User = get_user_model()


class GalleryAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryAnnouncement
        fields = ['image']


class AnnouncementAdvertisingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertising
        fields = '__all__'
        read_only_fields = ['announcement', 'date_start', 'is_active', 'date_end']

    def update(self, instance, validated_data):
        if instance.is_active is True:
            raise serializers.ValidationError(
                {
                    'already_activated': 'Для вашего объявления уже используется продвижения!'
                }
            )
        instance.date_end = get_range_month().date()
        instance.is_active = True
        return super().update(instance, validated_data)


class ResidentialComplexListSerializer(serializers.ModelSerializer):
    gallery_residential_complex = GalleryResidentialComplexSerializer(
        read_only=True, many=True
    )

    class Meta:
        model = ResidentialComplex
        fields = ['name', 'address', 'gallery_residential_complex']


class AnnouncementListSerializer(serializers.ModelSerializer):
    gallery_announcement = GalleryAnnouncementSerializer(many=True, read_only=True)
    advertising = AnnouncementAdvertisingSerializer(read_only=True)

    class Meta:
        model = Announcement
        fields = [
            'id', 'date_created', 'address', 'area', 'price',
            'is_moderation_check', 'is_active', 'purpose', 'rooms',
            'gallery_announcement', 'advertising'
        ]


class ApartmentListSerializer(serializers.ModelSerializer):
    announcement = AnnouncementListSerializer(
        read_only=True
    )

    class Meta:
        model = Apartment
        fields = ['id', 'floor', 'announcement']


class AnnouncementSerializer(serializers.ModelSerializer):
    gallery_announcement = GalleryAnnouncementSerializer(many=True, read_only=True)
    advertising = AnnouncementAdvertisingSerializer(read_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(required=True), write_only=True, required=True
    )

    class Meta:
        model = Announcement
        fields = [
            'id', 'address', 'description', 'area', 'area_kitchen',
            'balcony_or_loggia', 'price', 'is_moderation_check',
            'is_active', 'count_view', 'founding_document',
            'purpose', 'rooms', 'layout', 'condition', 'heating',
            'payment_options', 'agent_commission', 'communication',
            'creator', 'residential_complex', 'images', 'gallery_announcement',
            'advertising'
        ]
        read_only_fields = ['count_view', 'is_moderation_check', 'creator', 'advertising', 'is_active']
        extra_kwargs = {
            'purpose': {'required': True},

        }

    def validate(self, data):
        if 'purpose' in data and data['purpose'] == 'Квартира' and data['residential_complex'] is None:
            raise serializers.ValidationError(
                {
                    'required_residential_complex': 'При выборе квартиры выбор ЖК обязателен'
                }
            )
        if data['area_kitchen'] >= data['area']:
            raise serializers.ValidationError(
                {
                    'error_area': 'Площадь кухни не может превышать общую площадь'
                }
            )
        return data

    def create(self, validated_data):
        images_validate = validated_data.pop('images')
        instance = Announcement.objects.create(
            **validated_data, creator=self.context.get('request').user
        )
        if images_validate:
            for image in images_validate:
                GalleryAnnouncement.objects.create(
                    image=image, announcement=instance
                )
        return instance


class AnnouncementUpdateSerializer(AnnouncementSerializer):
    images_delete = serializers.ListField(
        child=serializers.CharField(
            required=False, allow_null=True, allow_blank=True, default=0
        ), write_only=True, required=False, allow_empty=True
    )
    images = serializers.ListField(
        child=serializers.ImageField(
            allow_empty_file=True, write_only=True
        ), write_only=True, required=False, allow_empty=True, allow_null=True
    )

    class Meta(AnnouncementSerializer.Meta):
        model = Announcement
        fields = [*AnnouncementSerializer.Meta.fields, 'images_delete']
        read_only_fields = [*AnnouncementSerializer.Meta.read_only_fields, 'residential_complex', 'purpose']

    def update(self, instance, validated_data):
        images = validated_data.pop('images') if 'images' in validated_data else None
        images_delete_validate = validated_data.pop('images_delete') if 'images_delete' in validated_data else None
        if images_delete_validate:
            images_to_delete_list = [i for i in ",".join(images_delete_validate) if i.isdigit()]
            if len(images_to_delete_list) > 0:
                GalleryAnnouncement.objects.filter(id__in=images_to_delete_list).delete()
        if images:
            for image in images:
                GalleryAnnouncement.objects.create(
                    image=image, announcement=instance
                )
        return super().update(instance, validated_data)


class AnnouncementComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['announcement', 'date_created', 'creator']
        read_only_fields = ['date_created', 'creator']

    def create(self, validated_data):
        request_user = self.context.get('request').user
        if Complaint.objects.filter(
                announcement=validated_data.get('announcement').id, creator=request_user
        ).exists():
            raise serializers.ValidationError("Вы уже жаловались на это обьявление")
        instance = Complaint.objects.create(**validated_data, creator=request_user)
        return instance


class AnnouncementModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['is_moderation_check']


class FavoritesAnnouncementSerializer(serializers.ModelSerializer):
    gallery_announcement = GalleryAnnouncementSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Announcement
        fields = ['id', 'address', 'description', 'price', 'date_created', 'gallery_announcement']


class UserFavoritesAnnouncementSerializer(serializers.ModelSerializer):
    favorites_announcement = FavoritesAnnouncementSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = User
        fields = ['id', 'favorites_announcement']

    def create(self, validated_data):
        announcement_id = self.context.get('request').query_params.get('announcement_id')
        request_user = self.context.get('request').user
        if announcement_id:
            if not Announcement.objects.filter(id=announcement_id).exists():
                raise serializers.ValidationError(
                    {
                        'error_announcement': 'Нет такого объявления'
                    }
                )
            request_user.favorites_announcement.add(announcement_id)
        return request_user
