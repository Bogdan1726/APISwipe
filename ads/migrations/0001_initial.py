# Generated by Django 3.2.14 on 2022-08-05 15:25

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('housing', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=250, verbose_name='Адрес')),
                ('description', models.TextField(verbose_name='Описание')),
                ('area', models.DecimalField(decimal_places=1, max_digits=5, validators=[django.core.validators.MinValueValidator(10.0)], verbose_name='Общая площадь')),
                ('area_kitchen', models.DecimalField(decimal_places=1, max_digits=5, validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Площадь кухни')),
                ('balcony_or_loggia', models.BooleanField(default=True, verbose_name='Балкон/лоджия')),
                ('price', models.PositiveIntegerField(verbose_name='Цена')),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_moderation_check', models.BooleanField(default=False)),
                ('count_view', models.PositiveIntegerField(default=0)),
                ('founding_document', models.CharField(choices=[('Собственность', 'Собственность'), ('Свидетельство о праве на наследство', 'Свидетельство о праве на наследство')], default='Собственность', max_length=36, verbose_name='Документ основания')),
                ('purpose', models.CharField(choices=[('Апартаменты', 'Апартаменты'), ('Квартира', 'Квартира'), ('Коммерческие помещения', 'Коммерческие помещения'), ('Офисное помещение', 'Офисное помещение')], default='Квартира', max_length=26, verbose_name='Назначение')),
                ('rooms', models.IntegerField(choices=[(1, '1 комнатная'), (2, '2 комнатная'), (3, '3 комнатная'), (4, '4 комнатная'), (5, '5 комнатная'), (6, '6 комнатная'), (7, '7 комнатная'), (8, '8 комнатная'), (9, '9 комнатная'), (10, '10 комнатная')], default=1, verbose_name='Количество комнат')),
                ('layout', models.CharField(choices=[('Студия, санузел', 'Студия, санузел'), ('Классическая', 'Классическая'), ('Европланировка', 'Европланировка'), ('Свободная', 'Свободная')], default='Классическая', max_length=20, verbose_name='Планировка')),
                ('condition', models.CharField(choices=[('Черновая', 'Черновая'), ('Ремонт от застройщика', 'Ремонт от застройщика'), ('В жилом состоянии', 'В жилом состоянии')], default='В жилом состоянии', max_length=21, verbose_name='Жилое состояние')),
                ('heating', models.CharField(choices=[('Центральное', 'Центральное'), ('Автономное', 'Автономное'), ('Альтернативное', 'Альтернативное')], default='Центральное', max_length=14, verbose_name='Тип отопления')),
                ('payment_options', models.CharField(choices=[('Ипотека', 'Ипотека'), ('Мат.капитал', 'Мат.капитал'), ('Другое', 'Другое')], default='Другое', max_length=12, verbose_name='Варианты расчета')),
                ('agent_commission', models.IntegerField(choices=[(10000, '10 000 ₴'), (15000, '15 000 ₴'), (30000, '30 000 ₴')], default=10000, verbose_name='Коммисия агенту')),
                ('communication', models.CharField(choices=[('Звонок + сообщение', 'Звонок + сообщение'), ('Звонок', 'Звонок'), ('Сообщение', 'Сообщение')], default='Звонок + сообщение', max_length=18, verbose_name='Способ связи')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_announcement', to=settings.AUTH_USER_MODEL)),
                ('residential_complex', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='residential_complex_announcement', to='housing.residentialcomplex')),
            ],
        ),
        migrations.CreateModel(
            name='GalleryAnnouncement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/ads/gallery/announcement')),
                ('announcement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery_announcement', to='ads.announcement')),
            ],
        ),
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('announcement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complaint', to='ads.announcement')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator_complaint', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Advertising',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_phrase', models.BooleanField(default=False, verbose_name='Добавить фразу')),
                ('add_color', models.BooleanField(default=False, verbose_name='Выделить цветом')),
                ('is_big', models.BooleanField(default=False, verbose_name='Большое объявление')),
                ('is_raise', models.BooleanField(default=False, verbose_name='Поднять объявление')),
                ('is_turbo', models.BooleanField(default=False, verbose_name='Турбо')),
                ('is_active', models.BooleanField(default=True)),
                ('date_start', models.DateField(auto_now_add=True)),
                ('date_end', models.DateField(blank=True, null=True)),
                ('phrase', models.CharField(choices=[('Подарок при покупке', 'Подарок при покупке'), ('Возможен торг', 'Возможен торг'), ('Квартира у моря', 'Квартира у моря'), ('В спальном районе', 'В спальном районе'), ('Вам повезло с ценой!', 'Вам повезло с ценой!'), ('Для большой семьи', 'Для большой семьи'), ('Семейное гнездышко', 'Семейное гнездышко'), ('Отдельная парковка', 'Отдельная парковка')], max_length=50)),
                ('color', models.CharField(choices=[('FDD7D7', 'FDD7D7'), ('CEF2D2', 'CEF2D2')], max_length=10)),
                ('announcement', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='advertising', to='ads.announcement')),
            ],
        ),
    ]
