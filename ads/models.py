from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from housing.models import ResidentialComplexHeating, ResidentialComplex
from django.core.validators import MinValueValidator

User = settings.AUTH_USER_MODEL


# region Announcement Choices
class AnnouncementDocument(models.TextChoices):
    OWN = 'Собственность', _('Собственность')
    INHERITANCE = 'Свидетельство о праве на наследство', _('Свидетельство о праве на наследство')


class AnnouncementPurpose(models.TextChoices):
    APARTMENTS = 'Дом', _('Дом')
    FLAT = 'Квартира', _('Квартира')
    COMMERCIAL = 'Коммерческие помещения', _('Коммерческие помещения')
    OFFICE = 'Офисное помещение', _('Офисное помещение')


class AnnouncementRooms(models.IntegerChoices):
    ONE = 1, _('1 комнатная')
    TWO = 2, _('2 комнатная')
    THREE = 3, _('3 комнатная')
    FOUR = 4, _('4 комнатная')
    FIVE = 5, _('5 комнатная')
    SIX = 6, _('6 комнатная')
    SEVEN = 7, _('7 комнатная')
    EIGHT = 8, _('8 комнатная')
    NINE = 9, _('9 комнатная')
    TEN = 10, _('10 комнатная')


class AnnouncementLayout(models.TextChoices):
    STUDIO = 'Студия, санузел', _('Студия, санузел')
    CLASSIC = 'Классическая', _('Классическая')
    EURO = 'Европланировка', _('Европланировка')
    FREE = 'Свободная', _('Свободная')


class AnnouncementPaymentOptions(models.TextChoices):
    MORTGAGE = 'Ипотека', _('Ипотека')
    MATHEMATICAL_CAPITAL = 'Мат.капитал', _('Мат.капитал')
    OTHER = 'Другое', _('Другое')


class AnnouncementAgentCommission(models.IntegerChoices):
    SMALL = 10000, _('10 000 ₴')
    MEDIUM = 15000, _('15 000 ₴')
    BIG = 30000, _('30 000 ₴')


class AnnouncementCommunication(models.TextChoices):
    CALL_MESSAGE = 'Звонок + сообщение', _('Звонок + сообщение')
    CALL = 'Звонок', _('Звонок')
    MESSAGE = 'Сообщение', _('Сообщение')


class AnnouncementDecoration(models.TextChoices):
    ROUGH_FINISH = 'Черновая', _('Черновая')
    REPAIR_FROM_THE_DEVELOPER = 'Ремонт от застройщика', _('Ремонт от застройщика')
    RESIDENTIAL_CONDITION = 'В жилом состоянии', _('В жилом состоянии')


# endregion Announcement Choices


# region models for App

class Announcement(models.Model):
    address = models.CharField(_('Адрес'), max_length=250)
    description = models.TextField(_('Описание'))
    area = models.DecimalField(
        _('Общая площадь'), max_digits=5, decimal_places=1, validators=[MinValueValidator(10.0)]
    )
    area_kitchen = models.DecimalField(
        _('Площадь кухни'), max_digits=5, decimal_places=1, validators=[MinValueValidator(0.0)]
    )
    balcony_or_loggia = models.BooleanField(_('Балкон/лоджия'), default=False)
    price = models.PositiveIntegerField(_('Цена'))
    date_created = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_moderation_check = models.BooleanField(default=False)
    count_view = models.PositiveIntegerField(default=1)
    founding_document = models.CharField(
        _('Документ основания'),
        max_length=36,
        choices=AnnouncementDocument.choices,
        default=AnnouncementDocument.OWN
    )
    purpose = models.CharField(
        _('Назначение'),
        max_length=26,
        choices=AnnouncementPurpose.choices,
        default=AnnouncementPurpose.FLAT
    )
    rooms = models.IntegerField(
        _('Количество комнат'),
        choices=AnnouncementRooms.choices,
        default=AnnouncementRooms.ONE
    )
    layout = models.CharField(
        _('Планировка'),
        max_length=20,
        choices=AnnouncementLayout.choices,
        default=AnnouncementLayout.CLASSIC
    )
    condition = models.CharField(
        _('Жилое состояние'),
        max_length=21,
        choices=AnnouncementDecoration.choices,
        default=AnnouncementDecoration.RESIDENTIAL_CONDITION
    )
    heating = models.CharField(
        _('Тип отопления'),
        max_length=14,
        choices=ResidentialComplexHeating.choices,
        default=ResidentialComplexHeating.CENTRAL
    )
    payment_options = models.CharField(
        _('Варианты расчета'),
        max_length=12,
        choices=AnnouncementPaymentOptions.choices,
        default=AnnouncementPaymentOptions.OTHER
    )
    agent_commission = models.IntegerField(
        _('Коммисия агенту'),
        choices=AnnouncementAgentCommission.choices,
        default=AnnouncementAgentCommission.SMALL
    )
    communication = models.CharField(
        _('Способ связи'),
        max_length=18,
        choices=AnnouncementCommunication.choices,
        default=AnnouncementCommunication.CALL_MESSAGE
    )
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_announcement')
    residential_complex = models.ForeignKey(
        ResidentialComplex, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='residential_complex_announcement'
    )

    class Meta:
        ordering = ('id',)

    @property
    def preview_image(self):
        obj = self.gallery_announcement.first()
        if obj:
            return obj.image


class Apartment(models.Model):
    plan = models.ImageField(upload_to='images/housing/apartment/plan', blank=True)
    plan_floor = models.ImageField(upload_to='images/housing/apartment/plan_floor', blank=True)
    number = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price_to_meter = models.PositiveIntegerField()
    corpus = models.PositiveIntegerField(_('Корпус'), default=1, validators=[MinValueValidator(1)])
    section = models.PositiveIntegerField(_('Секция'), default=1, validators=[MinValueValidator(1)])
    floor = models.PositiveIntegerField(_('Этаж'), default=1, validators=[MinValueValidator(1)])
    riser = models.PositiveIntegerField(_('Cтояк'), default=1, validators=[MinValueValidator(1)])
    is_booked = models.BooleanField(default=False)
    announcement = models.OneToOneField(Announcement, on_delete=models.CASCADE, related_name='announcement_apartment')

    def __str__(self):
        return f'{self.number}'

    def save(self, *args, **kwargs):
        self.price_to_meter = round(self.announcement.price / self.announcement.area)
        super(Apartment, self).save(*args, **kwargs)


class Advertising(models.Model):
    class AdvertisingPhrase(models.TextChoices):
        PHRASE1 = 'Подарок при покупке', _('Подарок при покупке')
        PHRASE2 = 'Возможен торг', _('Возможен торг')
        PHRASE3 = 'Квартира у моря', _('Квартира у моря')
        PHRASE4 = 'В спальном районе', _('В спальном районе')
        PHRASE5 = 'Вам повезло с ценой!', _('Вам повезло с ценой!')
        PHRASE6 = 'Для большой семьи', _('Для большой семьи')
        PHRASE7 = 'Семейное гнездышко', _('Семейное гнездышко')
        PHRASE8 = 'Отдельная парковка', _('Отдельная парковка')

    class AdvertisingColor(models.TextChoices):
        PINK = 'FDD7D7', _('FDD7D7')
        GREEN = 'CEF2D2', _('CEF2D2')

    add_phrase = models.BooleanField(_('Добавить фразу'), default=False)
    add_color = models.BooleanField(_('Выделить цветом'), default=False)
    is_big = models.BooleanField(_('Большое объявление'), default=False)
    is_raise = models.BooleanField(_('Поднять объявление'), default=False)
    is_turbo = models.BooleanField(_('Турбо'), default=False)
    is_active = models.BooleanField(default=False)
    date_start = models.DateField(auto_now=True)
    date_end = models.DateField(null=True, blank=True)
    phrase = models.CharField(
        max_length=50,
        choices=AdvertisingPhrase.choices
    )
    color = models.CharField(
        max_length=10,
        choices=AdvertisingColor.choices
    )
    announcement = models.OneToOneField(Announcement, on_delete=models.CASCADE, related_name='advertising')


class GalleryAnnouncement(models.Model):
    image = models.ImageField(upload_to='images/ads/gallery/announcements')
    announcement = models.ForeignKey(
        Announcement, on_delete=models.CASCADE, related_name='gallery_announcement'
    )

    class Meta:
        ordering = ('id',)


class Complaint(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='complaint')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creator_complaint')

# endregion models for App
