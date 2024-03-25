from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from telegram_bot.loader import bot
from telegram_bot.models import UnpaidUser


class Категории(models.Model):
    GENDER_CHOICES = [
        ('M', 'Мужчина'),
        ('F', 'Женщина'),
    ]

    GOAL_CHOICES = [
        ('G', 'Набрать вес'),
        ('L', 'Сбросить вес'),
    ]

    PLACE_CHOICES = [
        ('H', 'Дом'),
        ('G', 'Зал'),
    ]
    LEVEL_CHOICES = [
        ('P', 'Профессиональный'),
        ('N', 'Новичок'),
    ]

    название = models.CharField(max_length=100)
    пол = models.CharField(max_length=7, choices=GENDER_CHOICES, default='M')
    цель = models.CharField(max_length=12, choices=GOAL_CHOICES, default='G')
    место = models.CharField(max_length=3, choices=PLACE_CHOICES, default='H')
    уровень = models.CharField(max_length=16, choices=LEVEL_CHOICES, default='P')

    def __str__(self):
        return self.название


class Video(models.Model):
    name = models.CharField(max_length=300, blank=True, null=True)
    video_file_id = models.CharField(max_length=300, blank=True, null=True)


    def __str__(self):
        return self.name

class Content(models.Model):
    TYPE_CHOICES = [
        ('V', 'Video'),
        ('T', 'Text'),
        ('P', 'Photo'),
        ('G', 'GIF'),
    ]

    day = models.IntegerField(null=True)
    content_type = models.CharField(default='T', max_length=1, choices=TYPE_CHOICES)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    gif = models.FileField(upload_to='gifs/', validators=[FileExtensionValidator(allowed_extensions=['gif'])], blank=True, null=True)
    video_file_id = models.CharField(max_length=300, blank=True, null=True)
    photo_file_id = models.CharField(max_length=300, blank=True, null=True)
    gif_file_id = models.CharField(max_length=300, blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    sequence_number = models.PositiveIntegerField(null=True)

    def __str__(self):
        return f"День {self.day} - {self.get_content_type_display()}, для категории - {self.category.название}"

    class Meta:
        abstract = True
        ordering = ['sequence_number']


class DailyContent(Content):
    category = models.ForeignKey(Категории, on_delete=models.CASCADE, related_name='daily_contents')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, blank=True, null=True, related_name='+++++')


class Mailing(Content):
    category = models.ForeignKey(Категории, on_delete=models.CASCADE, related_name='Рассылка')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, blank=True, null=True, related_name='+')


class Training(Content):
    category = models.ForeignKey(Категории, on_delete=models.CASCADE, related_name='Тренировки')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, blank=True, null=True, related_name='++')


class UnpaidUserContent(Content):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, blank=True, null=True, related_name='+++')
    def __str__(self):
        return f"День {self.day} - {self.get_content_type_display()}, для неоплаченного пользователя - {self.unpaid_user.user_id}"

    class Meta:
        ordering = ['sequence_number']



@receiver(post_save, sender=DailyContent)
def upload_to_telegram(sender, instance=None, created=False, **kwargs):
    if created:

        if instance.photo:
            with open(instance.photo.path, 'rb') as photo_file:
                message = bot.send_photo(chat_id=305896408, photo=photo_file)
                instance.photo_file_id = message.photo[-1].file_id
                instance.photo.delete(save=False)

        if instance.gif:
            with open(instance.gif.path, 'rb') as gif_file:
                message = bot.send_document(chat_id=305896408, document=gif_file)
                instance.gif_file_id = message.document.file_id
                instance.gif.delete(save=False)

        instance.save()
