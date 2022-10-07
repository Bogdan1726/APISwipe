from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from housing.models import ResidentialComplex
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
        fields = [
            'id', 'add_phrase', 'add_color', 'is_big', 'is_raise',
            'is_turbo', 'is_active', 'phrase', 'color',
            'date_start', 'date_end'
        ]
        read_only_fields = ['date_start', 'is_active', 'date_end']

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
        if 'purpose' in data and data['purpose'] == 'Квартира':
            try:
                if data['residential_complex'] is None:
                    raise serializers.ValidationError(
                        {
                            'required_residential_complex': 'При выборе квартиры выбор ЖК обязателен'
                        }
                    )
            except KeyError:
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


class ApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = [
            'id', 'plan', 'plan_floor', 'number', 'price_to_meter',
            'corpus', 'section', 'floor', 'riser', 'is_booked',
            'announcement'
        ]
        read_only_fields = [
            'price_to_meter', 'announcement'
        ]
        extra_kwargs = {
            'corpus': {'required': True},
            'section': {'required': True},
            'floor': {'required': True},
            'riser': {'required': True},
        }

    def validate(self, data):
        errors = []
        residential_complex = self.instance.announcement.residential_complex
        number, corpus, section = data['number'], data['corpus'], data['section']
        floor, riser = data['floor'], data['riser']
        obj = Apartment.objects.filter(number=number, corpus=corpus, section=section, is_booked=True,
                                       announcement__residential_complex=residential_complex).first()
        if obj and self.instance.id != obj.id:
            errors.append({
                'unique_number': f"В {data['section']} секции данного ЖК есть квартира №{data['number']}"
            })
        if corpus > residential_complex.corpus:
            errors.append({'corpus_error': f"В жилом комплексе нет {corpus}-го корпуса"})
        if section > residential_complex.section:
            errors.append({'section_error': f"В жилом комплексе нет {section}-й секции"})
        if floor > residential_complex.floor:
            errors.append({'floor_error': f"В жилом комплексе нет {floor}-го этажа"})
        if riser > residential_complex.riser:
            errors.append({'riser_error': f"В жилом комплексе нет {riser}-го стояка"})
        if errors:
            raise serializers.ValidationError(errors)
        return data


class ApartmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = ['id', 'is_booked', 'floor']


class CreatorSerializers(serializers.ModelSerializer):
    profile_image = serializers.ImageField()

    class Meta:
        model = User
        fields = [
            'first_name', 'phone', 'profile_image'
        ]


class ResidentialComplexListSerializer(serializers.ModelSerializer):
    preview_image = serializers.ImageField()

    class Meta:
        model = ResidentialComplex
        fields = ['id', 'preview_image', 'name', 'address', 'favorite_complex']


class AnnouncementListSerializer(serializers.ModelSerializer):
    announcement_apartment = ApartmentListSerializer(read_only=True)
    advertising = AnnouncementAdvertisingSerializer(read_only=True)
    preview_image = serializers.ImageField()

    class Meta:
        model = Announcement
        fields = [
            'id', 'preview_image', 'address', 'area', 'price',
            'rooms', 'creator', 'advertising', 'announcement_apartment',
            'favorite_announcement', 'condition', 'payment_options',
            'residential_complex'
        ]


class AnnouncementRetrieveSerializer(AnnouncementListSerializer):
    creator = CreatorSerializers(read_only=True)
    gallery_announcement = GalleryAnnouncementSerializer(many=True, read_only=True)

    class Meta(AnnouncementListSerializer.Meta):
        model = Announcement
        fields = [
                     'payment_options', 'condition', 'residential_complex', 'condition',
                     'is_moderation_check', 'purpose', 'balcony_or_loggia', 'area_kitchen',
                     'description', 'heating', 'payment_options', 'agent_commission', 'layout',
                     'founding_document', 'communication', 'gallery_announcement'
                 ] + AnnouncementListSerializer.Meta.fields


class AnnouncementModerationSerializer(AnnouncementListSerializer):
    preview_image = serializers.ImageField(read_only=True)

    class Meta(AnnouncementListSerializer.Meta):
        model = Announcement
        fields = ['is_moderation_check', ] + AnnouncementListSerializer.Meta.fields
        read_only_fields = [
            'id', 'preview_image', 'address', 'area', 'price',
            'rooms', 'creator', 'advertising', 'announcement_apartment',
            'favorite_announcement'
        ]


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
        fields = ['id', 'announcement', 'date_created', 'creator']
        read_only_fields = ['date_created', 'creator']

    def create(self, validated_data):
        request_user = self.context.get('request').user
        if Complaint.objects.filter(
                announcement=validated_data.get('announcement').id, creator=request_user
        ).exists():
            raise serializers.ValidationError("Вы уже жаловались на это обьявление")
        instance = Complaint.objects.create(**validated_data, creator=request_user)
        return instance


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
