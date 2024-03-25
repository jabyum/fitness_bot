from django.contrib import admin
from django.urls import path
from telegram_bot.admin import my_admin_site as telegram_bot_admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("myadmin/", telegram_bot_admin.urls),
]
