from rest_framework import serializers
from .models import (
    Announcement, Advertising, GalleryAnnouncement, Complaint
)


class AnnouncementAdvertisingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertising
        fields = '__all__'
        read_only_fields = ['announcement', 'date_start']


class GalleryAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryAnnouncement
        fields = ['image']


class GalleryAnnouncementDeleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = GalleryAnnouncement
        fields = ['id']


class AnnouncementSerializer(serializers.ModelSerializer):
    gallery_announcement = GalleryAnnouncementSerializer(many=True, read_only=True)
    advertising = AnnouncementAdvertisingSerializer(read_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
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

    def validate(self, data):
        if data['purpose'] == 'Квартира' and data['residential_complex'] is None:
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

    def update(self, instance, validated_data):
        images = validated_data.pop('images') if 'images' in validated_data else None
        images_to_delete = validated_data.pop('images_to_delete') if 'images_to_delete' in validated_data else None
        # images_to_delete_list = [*images_to_delete.values()]
        # if images:
        #     for image in images:
        #         GalleryAnnouncement.objects.create(
        #             image=image, announcement=instance
        #         )
        # if len(images_to_delete_list) > 0:
        #     GalleryAnnouncement.objects.filter(id__in=images_to_delete_list).delete()
        return super().update(instance, validated_data)


class AnnouncementUpdateSerializer(AnnouncementSerializer):
    images_to_delete = GalleryAnnouncementDeleteSerializer(
        many=True, write_only=True, required=False
    )

    class Meta(AnnouncementSerializer.Meta):
        model = Announcement
        fields = [*AnnouncementSerializer.Meta.fields, 'images_to_delete']


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
