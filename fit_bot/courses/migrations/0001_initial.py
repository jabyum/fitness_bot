# Generated by Django 4.1.7 on 2023-07-27 18:22

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=300, null=True)),
                ('video_file_id', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Категории',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('название', models.CharField(max_length=100)),
                ('пол', models.CharField(choices=[('M', 'Мужчина'), ('F', 'Женщина')], default='M', max_length=7)),
                ('цель', models.CharField(choices=[('G', 'Набрать вес'), ('L', 'Сбросить вес')], default='G', max_length=12)),
                ('место', models.CharField(choices=[('H', 'Дом'), ('G', 'Зал')], default='H', max_length=3)),
                ('уровень', models.CharField(choices=[('P', 'Профессиональный'), ('N', 'Новичок')], default='P', max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='UnpaidUserContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(null=True)),
                ('content_type', models.CharField(choices=[('V', 'Video'), ('T', 'Text'), ('P', 'Photo'), ('G', 'GIF')], default='T', max_length=1)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='photos/')),
                ('gif', models.FileField(blank=True, null=True, upload_to='gifs/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['gif'])])),
                ('video_file_id', models.CharField(blank=True, max_length=300, null=True)),
                ('photo_file_id', models.CharField(blank=True, max_length=300, null=True)),
                ('gif_file_id', models.CharField(blank=True, max_length=300, null=True)),
                ('caption', models.TextField(blank=True, null=True)),
                ('sequence_number', models.PositiveIntegerField(null=True)),
                ('video', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+++', to='courses.video')),
            ],
            options={
                'ordering': ['sequence_number'],
            },
        ),
        migrations.CreateModel(
            name='Training',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(null=True)),
                ('content_type', models.CharField(choices=[('V', 'Video'), ('T', 'Text'), ('P', 'Photo'), ('G', 'GIF')], default='T', max_length=1)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='photos/')),
                ('gif', models.FileField(blank=True, null=True, upload_to='gifs/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['gif'])])),
                ('video_file_id', models.CharField(blank=True, max_length=300, null=True)),
                ('photo_file_id', models.CharField(blank=True, max_length=300, null=True)),
                ('gif_file_id', models.CharField(blank=True, max_length=300, null=True)),
                ('caption', models.TextField(blank=True, null=True)),
                ('sequence_number', models.PositiveIntegerField(null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Тренировки', to='courses.категории')),
                ('video', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='++', to='courses.video')),
            ],
            options={
                'ordering': ['sequence_number'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Mailing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(null=True)),
                ('content_type', models.CharField(choices=[('V', 'Video'), ('T', 'Text'), ('P', 'Photo'), ('G', 'GIF')], default='T', max_length=1)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='photos/')),
                ('gif', models.FileField(blank=True, null=True, upload_to='gifs/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['gif'])])),
                ('video_file_id', models.CharField(blank=True, max_length=300, null=True)),
                ('photo_file_id', models.CharField(blank=True, max_length=300, null=True)),
                ('gif_file_id', models.CharField(blank=True, max_length=300, null=True)),
                ('caption', models.TextField(blank=True, null=True)),
                ('sequence_number', models.PositiveIntegerField(null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Рассылка', to='courses.категории')),
                ('video', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='courses.video')),
            ],
            options={
                'ordering': ['sequence_number'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DailyContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(null=True)),
                ('content_type', models.CharField(choices=[('V', 'Video'), ('T', 'Text'), ('P', 'Photo'), ('G', 'GIF')], default='T', max_length=1)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='photos/')),
                ('gif', models.FileField(blank=True, null=True, upload_to='gifs/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['gif'])])),
                ('video_file_id', models.CharField(blank=True, max_length=300, null=True)),
                ('photo_file_id', models.CharField(blank=True, max_length=300, null=True)),
                ('gif_file_id', models.CharField(blank=True, max_length=300, null=True)),
                ('caption', models.TextField(blank=True, null=True)),
                ('sequence_number', models.PositiveIntegerField(null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_contents', to='courses.категории')),
                ('video', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+++++', to='courses.video')),
            ],
            options={
                'ordering': ['sequence_number'],
                'abstract': False,
            },
        ),
    ]