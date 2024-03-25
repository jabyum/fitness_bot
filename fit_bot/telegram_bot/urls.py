from django.urls import path
from . import views

app_name = 'telegram_bot'
urlpatterns = [
    path('export-data/', views.export_data, name='export_data'),
]
