from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UnpaidUser(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    has_paid = models.BooleanField(default=False)
    username = models.CharField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} - {self.username} (id - {self.user_id})"

    class Meta:
        app_label = 'telegram_bot'


class PaidUser(models.Model):
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
    LEVEL = [
        ('P', 'Профессиональный'),
        ('N', 'Новичок'),
    ]

    user = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    paid_day = models.DateField(blank=True, null=True)
    calories = models.FloatField(blank=True, null=True)
    proteins = models.FloatField(blank=True, null=True)
    timezone = models.CharField(max_length=100)
    пол = models.CharField(max_length=7, choices=GENDER_CHOICES, default='M')
    цель = models.CharField(max_length=12, choices=GOAL_CHOICES, default='G')
    место = models.CharField(max_length=3, choices=PLACE_CHOICES, default='H')
    уровень = models.CharField(max_length=16, choices=LEVEL, default='N')

    def __str__(self):
        return f"{self.full_name} - {self.username} ({self.user})"

    class Meta:
        app_label = 'telegram_bot'


class CourseDay(models.Model):
    user = models.ForeignKey(PaidUser, on_delete=models.CASCADE)
    day = models.IntegerField()
    has_requested = models.BooleanField(default=False)
    total_calories = models.FloatField(default=0)
    total_protein = models.FloatField(default=0)
    total_fat = models.FloatField(default=0)
    total_carbs = models.FloatField(default=0)

    class Meta:
        app_label = 'telegram_bot'


class Meal(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
        ('dinner', 'Ужин'),
        ('snack', 'Перекус'),
    ]
    course_day = models.ForeignKey(CourseDay, on_delete=models.CASCADE)
    meal_type = models.CharField(choices=MEAL_TYPES, max_length=10)
    calories = models.FloatField(default=0)
    protein = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    carbs = models.FloatField(default=0)

    def __str__(self):
        return f"{self.course_day.user.username} " \
               f"({self.course_day.user.full_name}), Day {self.course_day.day}, " \
               f"{self.get_meal_type_display()}"

    class Meta:
        app_label = 'telegram_bot'


class BankCards(models.Model):
    bank_name = models.CharField(max_length=15, blank=True, null=True)
    card_number = models.CharField(max_length=25, blank=True, null=True)
    number_of_activations = models.IntegerField(blank=True, null=True, default=0)

    def __str__(self):
        return f"Карта банка {self.bank_name}"


class FinishedUser(models.Model):
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
    LEVEL = [
        ('P', 'Профессиональный'),
        ('N', 'Новичок'),
    ]

    user = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    paid_day = models.DateField(blank=True, null=True)
    calories = models.IntegerField(blank=True, null=True)
    proteins = models.IntegerField(blank=True, null=True)
    timezone = models.CharField(max_length=100)
    пол = models.CharField(max_length=7, choices=GENDER_CHOICES, default='M')
    цель = models.CharField(max_length=12, choices=GOAL_CHOICES, default='G')
    место = models.CharField(max_length=3, choices=PLACE_CHOICES, default='H')
    уровень = models.CharField(max_length=16, choices=LEVEL, default='P')

    def __str__(self):
        return f"{self.username} ({self.user})"

    class Meta:
        app_label = 'telegram_bot'


class SupportTicket(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    question = models.CharField(max_length=3000, blank=True, null=True)
    answer = models.CharField(max_length=3000, blank=True, null=True)



