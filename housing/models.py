from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

User = settings.AUTH_USER_MODEL

# region Residential Complex Choices


class ResidentialComplexStatus(models.TextChoices):
    APARTMENTS = 'Квартиры', _('Квартиры')
    OFFICES = 'Офисы', _('Офисы')
    COMMERCIAL = 'Торговые помещения', _('Торговые помещения')


class ResidentialComplexTypeHouse(models.TextChoices):
    MULTI_FAMILY = 'Многоквартирный', _('Многоквартирный')
    CLUB = 'Клубный', _('Клубный(Малоквартирный)')


class ResidentialComplexClassHouse(models.TextChoices):
    ELITE = 'Элитный', _('Элитный')
    AVERAGE = 'Средний', _('Средний')
    BUDGET = 'Бюджет', _('Бюджет')


class ResidentialComplexTechnology(models.TextChoices):
    MONOLITH = 'Монолитный каркас с керамзитно-блочным заполнением', \
               _('Монолитный каркас с керамзитно-блочным заполнением')
    FRAME = 'Каркасно-панельное', _('Каркасно-панельное строительство')
    MONOLITH_PANEL = 'Монолитно-панельное', _('Монолитно-панельное')


class ResidentialComplexTerritory(models.TextChoices):
    CLOSED_GUARDED = 'Закрытая охраняемая', _('Закрытая охраняемая')
    CLOSED = 'Закрытая', _('Закрытая')
    OPEN = 'Открытая', _('Открытая')


class ResidentialComplexCommunalPay(models.TextChoices):
    PAYMENT = 'Платежи', _('Платежи')
    PREPAYMENT = 'Предоплата', _('Предоплата')


class ResidentialComplexHeating(models.TextChoices):
    CENTRAL = 'Центральное', _('Центральное')
    AUTONOMOUS = 'Автономное', _('Автономное')
    ALTERNATIVE = 'Альтернативное', _('Альтернативное')


class ResidentialComplexSewerage(models.TextChoices):
    CENTRAL = 'Центральная', _('Центральная')
    ALTERNATIVE = 'Альтернативная', _('Альтернативная')


class ResidentialComplexWaterService(models.TextChoices):
    CENTRAL = 'Центральное', _('Центральное')
    ALTERNATIVE = 'Альтернативное', _('Альтернативное')


# endregion Residential Complex Choices


# region models for App
class ResidentialComplex(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(_('Описание'))
    commissioning_date = models.DateField(auto_now_add=True)
    is_commissioning = models.BooleanField(default=True)
    address = models.CharField(max_length=150)
    map_lat = models.DecimalField(max_digits=19, decimal_places=16)
    map_lon = models.DecimalField(max_digits=19, decimal_places=16)
    distance = models.PositiveIntegerField(_('Расстояние до моря'))
    ceiling_height = models.FloatField(
        validators=[MinValueValidator(2.0), MaxValueValidator(5.0)]
    )
    gas = models.BooleanField(_('Газ'))
    status = models.CharField(
        _('Статус ЖК'),
        max_length=18,
        choices=ResidentialComplexStatus.choices,
        default=ResidentialComplexStatus.APARTMENTS
    )
    type_house = models.CharField(
        _('Вид дома'),
        max_length=15,
        choices=ResidentialComplexTypeHouse.choices,
        default=ResidentialComplexTypeHouse.MULTI_FAMILY
    )
    class_house = models.CharField(
        _('Класс дома'),
        max_length=7,
        choices=ResidentialComplexClassHouse.choices,
        default=ResidentialComplexClassHouse.AVERAGE
    )
    technology = models.CharField(
        _('Технология строительства'),
        max_length=60,
        choices=ResidentialComplexTechnology.choices,
        default=ResidentialComplexTechnology.MONOLITH
    )
    territory = models.CharField(
        _('Территория'),
        max_length=19,
        choices=ResidentialComplexTerritory.choices,
        default=ResidentialComplexTerritory.OPEN
    )
    communal_payments = models.CharField(
        _('Коммунальные платежи'),
        max_length=10,
        choices=ResidentialComplexCommunalPay.choices,
        default=ResidentialComplexCommunalPay.PAYMENT
    )
    heating = models.CharField(
        _('Отопление'),
        max_length=14,
        choices=ResidentialComplexHeating.choices,
        default=ResidentialComplexHeating.CENTRAL
    )
    sewerage = models.CharField(
        _('Канализация'),
        max_length=14,
        choices=ResidentialComplexSewerage.choices,
        default=ResidentialComplexSewerage.CENTRAL
    )
    water_service = models.CharField(
        _('Водоснабжение'),
        max_length=14,
        choices=ResidentialComplexWaterService.choices,
        default=ResidentialComplexWaterService.CENTRAL
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_residential_complex')


class RegistrationAndPayment(models.Model):
    formalization = models.CharField(_('Оформление'), max_length=150)
    payment_options = models.CharField(_('Варианты расчета'), max_length=150)
    purpose = models.CharField(_('Назначение'), max_length=150)
    contract_sum = models.CharField(_('Сумма в договоре'), max_length=150)
    residential_complex = models.OneToOneField(
        ResidentialComplex, on_delete=models.CASCADE, related_name='registration_and_payment'
    )


class ResidentialComplexBenefits(models.Model):
    playground = models.BooleanField(default=False)
    sportsground = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    territory_protected = models.BooleanField(default=False)
    residential_complex = models.OneToOneField(
        ResidentialComplex, on_delete=models.CASCADE, related_name='benefits'
    )


class ResidentialComplexNews(models.Model):
    title = models.CharField(max_length=150)
    text = models.TextField()
    date_created = models.DateField(auto_now=True)
    residential_complex = models.ForeignKey(ResidentialComplex, on_delete=models.CASCADE, related_name='news')


class GalleryResidentialComplex(models.Model):
    image = models.ImageField(upload_to='images/housing/gallery/complex')
    order = models.PositiveIntegerField(null=True, blank=True)
    residential_complex = models.ForeignKey(
        ResidentialComplex, on_delete=models.CASCADE, related_name='gallery_residential_complex'
    )


class Document(models.Model):
    name = models.CharField(max_length=50)
    file = models.FileField(upload_to='files/housing/document')
    residential_complex = models.ForeignKey(ResidentialComplex, on_delete=models.CASCADE, related_name='document')


# region Apartment Choices

class ApartmentDecoration(models.TextChoices):
    ROUGH_FINISH = 'Черновая', _('Черновая')
    REPAIR_FROM_THE_DEVELOPER = 'Ремонт от застройщика', _('Ремонт от застройщика')
    RESIDENTIAL_CONDITION = 'В жилом состоянии', _('В жилом состоянии')


# endregion Apartment Choices


class Apartment(models.Model):
    plan = models.ImageField(upload_to='images/housing/apartment/plan', blank=True)
    plan_floor = models.ImageField(upload_to='images/housing/apartment/plan_floor', blank=True)
    number = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    room = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    area = models.DecimalField(max_digits=5, decimal_places=1, validators=[MinValueValidator(10.00)])
    price = models.PositiveIntegerField()
    price_to_meter = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    corpus = models.PositiveIntegerField(_('Корпус'))
    section = models.PositiveIntegerField(_('Секция'))
    floor = models.PositiveIntegerField(_('Этаж'))
    riser = models.PositiveIntegerField(_('Cтояк'))
    is_booked = models.BooleanField(default=False)
    decoration = models.CharField(
        max_length=21,
        choices=ApartmentDecoration.choices,
        default=ApartmentDecoration.ROUGH_FINISH
    )
    residential_complex = models.ForeignKey(
        ResidentialComplex, on_delete=models.SET_NULL, blank=True, null=True, related_name='apartment'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_apartment')

    def __str__(self):
        return f'{self.number}'

    def save(self, *args, **kwargs):
        self.price = round(self.price_to_meter * self.area)
        super(Apartment, self).save(*args, **kwargs)

# endregion models for App
