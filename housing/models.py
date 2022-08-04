from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


# Create your models here.

# region TextChoices


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

# endregion TextChoices


class ResidentialComplex(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(_('Описание'))
    commissioning_date = models.DateField(auto_now_add=True)
    is_commissioning = models.BooleanField(default=True)
    district = models.CharField(max_length=150)
    microdistrict = models.CharField(max_length=150, blank=True)
    street = models.CharField(max_length=150)
    map_lat = models.DecimalField(max_digits=12, decimal_places=8)
    map_lon = models.DecimalField(max_digits=12, decimal_places=8)
    distance = models.PositiveIntegerField(_('Высота потолков'))
    ceiling_height = models.FloatField()
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
