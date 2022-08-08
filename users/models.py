from django.contrib.auth.base_user import AbstractBaseUser
from django.core.validators import MinValueValidator, MaxValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from ads.models import Announcement, AnnouncementPurpose, AnnouncementPaymentOptions
from housing.models import ResidentialComplex, ApartmentDecoration
from users.managers import CustomUserManager
from django.core.mail import send_mail
from django.db import models


# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    class Notification(models.TextChoices):
        ME = 'Мне', _('Мне')
        ME_AND_AGENT = 'Мне и агенту', _('Мне и агенту')
        AGENT = 'Агенту', _('Агенту')
        DISABLE = 'Отключить', _('Отключить')

    first_name = models.CharField(_('Имя'), max_length=150)
    last_name = models.CharField(_('Фамилия'), max_length=150)
    phone = PhoneNumberField(_('Телефон'), blank=True)
    email = models.EmailField(_('Email'), unique=True)
    profile_image = models.ImageField(_('Изображение профиля'), upload_to='images/user/profile', blank=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    per_agent = models.BooleanField(
        _('Переключить звонки и сообщения на агента'),
        default=False,
        blank=True
    )
    is_blacklist = models.BooleanField(
        _('Черный список'),
        default=False,
        blank=True
    )
    is_developer = models.BooleanField(
        _('Застройщик'),
        default=False,
        blank=True
    )
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    notification = models.CharField(
        _('Уведомления'),
        max_length=12,
        choices=Notification.choices,
        default=Notification.ME
    )
    favorites_residential_complex = models.ManyToManyField(
        ResidentialComplex,
        related_name='favorite_complex',
        blank=True
    )
    favorites_announcement = models.ManyToManyField(
        Announcement,
        related_name='favorite_announcement',
        blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Subscription(models.Model):
    date_start = models.DateField(auto_now_add=True)
    date_end = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_auto_renewal = models.BooleanField(default=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='subscription', null=True, blank=True
    )


class Contact(models.Model):
    class TYPES(models.TextChoices):
        SALES_DEPARTMENT = 'Отдел продаж', _('Отдел продаж')
        AGENT_CONTACTS = 'Контакты агента', _('Контакты агента')

    first_name = models.CharField(_('Имя'), max_length=150)
    last_name = models.CharField(_('Фамилия'), max_length=150)
    phone = PhoneNumberField(_('Телефон'), blank=True)
    email = models.EmailField(_('Email'), unique=True)
    type = models.CharField(
        _('Вид контакта'),
        max_length=15,
        choices=TYPES.choices,
    )
    residential_complex = models.OneToOneField(
        ResidentialComplex, on_delete=models.CASCADE, related_name='sales_department_contact', null=True, blank=True
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='agent_contact', null=True, blank=True
    )


class Notary(models.Model):
    first_name = models.CharField(_('Имя'), max_length=150)
    last_name = models.CharField(_('Фамилия'), max_length=150)
    phone = PhoneNumberField(_('Телефон'))
    email = models.EmailField(_('Email'), unique=True)
    profile_image = models.ImageField(_('Изображение профиля'), upload_to='images/user/notary', blank=True)


class Message(models.Model):
    text = models.CharField(max_length=600)
    is_feedback = models.BooleanField(default=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_sender')
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='message_recipient', null=True, blank=True
    )


class MessageFile(models.Model):
    file = models.FileField(upload_to='files/user/message')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='message_files')


class Filter(models.Model):
    status_house = models.BooleanField(_('Статус дома'), default=True)
    district = models.CharField(_('Район'), max_length=150)
    microdistrict = models.CharField(_('Микрорайон'), max_length=150)
    rooms = models.PositiveIntegerField(
        _('Количество комнат'), validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    price_start = models.PositiveIntegerField()
    price_end = models.PositiveIntegerField()
    area_start = models.PositiveIntegerField()
    area_end = models.PositiveIntegerField()
    type_housing = models.CharField(_('Вид недвижимости'), max_length=20)
    purpose = models.CharField(
        _('Назначение'),
        max_length=26,
        choices=AnnouncementPurpose.choices,
        default=AnnouncementPurpose.FLAT
    )
    payment_options = models.CharField(
        _('Условия покупки'),
        max_length=12,
        choices=AnnouncementPaymentOptions.choices,
        default=AnnouncementPaymentOptions.OTHER
    )
    state = models.CharField(
        _('Состояние'),
        max_length=21,
        choices=ApartmentDecoration.choices,
        default=ApartmentDecoration.ROUGH_FINISH
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='filter'
    )
