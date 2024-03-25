from django.contrib import admin
from .models import Категории, UnpaidUserContent, Mailing, Training, Video
from django.db.models import Count
from telegram_bot.admin import my_admin_site


class BaseContentAdmin(admin.ModelAdmin):
    list_display = ('day', 'content_type', 'category')
    list_filter = ('category',)
    search_fields = ('category__название',)
    ordering = ('day',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('day', 'category')
        }),
        ('Тип контента', {
            'fields': ('content_type', 'video', 'photo', 'gif', 'caption')
        }),
        ('Дополнительная информация', {
            'fields': ('sequence_number',)
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(category_count=Count('category'))
        return queryset


class MailingAdmin(BaseContentAdmin):
    ordering = ('category', 'day')


class TrainingAdmin(BaseContentAdmin):
    ordering = ('category', 'day')


class UnpaidUserContentAdmin(admin.ModelAdmin):
    list_display = ('day', 'content_type')
    ordering = ('day',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('day',)
        }),
        ('Тип контента', {
            'fields': ('content_type', 'video', 'photo', 'gif', 'caption')
        }),
        ('Дополнительная информация', {
            'fields': ('sequence_number',)
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset


my_admin_site.register(Категории)
my_admin_site.register(UnpaidUserContent, UnpaidUserContentAdmin)
my_admin_site.register(Mailing, MailingAdmin)
my_admin_site.register(Training, TrainingAdmin)
my_admin_site.register(Video)