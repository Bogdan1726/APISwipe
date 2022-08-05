# Generated by Django 3.2.14 on 2022-08-05 15:26

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0001_initial'),
        ('housing', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=600)),
                ('is_feedback', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Notary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=150, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=150, verbose_name='Фамилия')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None, verbose_name='Телефон')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('profile_image', models.ImageField(blank=True, upload_to='images/user/notary')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='favorites_announcement',
            field=models.ManyToManyField(blank=True, related_name='favorite_announcement', to='ads.Announcement'),
        ),
        migrations.AddField(
            model_name='user',
            name='favorites_residential_complex',
            field=models.ManyToManyField(blank=True, related_name='favorite_complex', to='housing.ResidentialComplex'),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_start', models.DateField(auto_now_add=True)),
                ('date_end', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_auto_renewal', models.BooleanField(default=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MessageFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='files/user/message')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_files', to='users.message')),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='recipient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_recipient', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_sender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_house', models.BooleanField(default=True, verbose_name='Статус дома')),
                ('district', models.CharField(max_length=150, verbose_name='Район')),
                ('microdistrict', models.CharField(max_length=150, verbose_name='Микрорайон')),
                ('rooms', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Количество комнат')),
                ('price_start', models.PositiveIntegerField()),
                ('price_end', models.PositiveIntegerField()),
                ('area_start', models.PositiveIntegerField()),
                ('area_end', models.PositiveIntegerField()),
                ('type_housing', models.CharField(max_length=20, verbose_name='Вид недвижимости')),
                ('purpose', models.CharField(choices=[('Апартаменты', 'Апартаменты'), ('Квартира', 'Квартира'), ('Коммерческие помещения', 'Коммерческие помещения'), ('Офисное помещение', 'Офисное помещение')], default='Квартира', max_length=26, verbose_name='Назначение')),
                ('payment_options', models.CharField(choices=[('Ипотека', 'Ипотека'), ('Мат.капитал', 'Мат.капитал'), ('Другое', 'Другое')], default='Другое', max_length=12, verbose_name='Условия покупки')),
                ('state', models.CharField(choices=[('Черновая', 'Черновая'), ('Ремонт от застройщика', 'Ремонт от застройщика'), ('В жилом состоянии', 'В жилом состоянии')], default='Черновая', max_length=21, verbose_name='Состояние')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filter', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=150, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=150, verbose_name='Фамилия')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None, verbose_name='Телефон')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('type', models.CharField(choices=[('Отдел продаж', 'Отдел продаж'), ('Контакты агента', 'Контакты агента')], max_length=15, verbose_name='Вид контакта')),
                ('residential_complex', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sales_department_contact', to='housing.residentialcomplex')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agent_contact', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
