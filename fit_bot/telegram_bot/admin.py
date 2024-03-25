from django.contrib import admin
from .models import UnpaidUser, PaidUser, BankCards, FinishedUser, SupportTicket, CourseDay, Meal
from .views import export_to_xlsx


def export_to_xlsx_action(modeladmin, request, queryset):
    model_class = modeladmin.model
    return export_to_xlsx(model_class)


export_to_xlsx_action.short_description = "Выгрузить выбранные объекты в xlsx"


class UnpaidUserAdmin(admin.ModelAdmin):
    actions = [export_to_xlsx_action]
    ordering = ['full_name']


class PaidUserAdmin(admin.ModelAdmin):
    actions = [export_to_xlsx_action]
    ordering = ['full_name']


class UserCaloriesAdmin(admin.ModelAdmin):
    actions = [export_to_xlsx_action]


class FinishedUserAdmin(admin.ModelAdmin):
    actions = [export_to_xlsx_action]


class SupportTicketAdmin(admin.ModelAdmin):
    actions = [export_to_xlsx_action]


class BankCardsAdmin(admin.ModelAdmin):
    actions = [export_to_xlsx_action]


class MyAdminSite(admin.AdminSite):
    site_header = "Админ панель 21FIT"


class CourseDayAdmin(admin.ModelAdmin):
    actions = [export_to_xlsx_action]
    list_display = ('user', 'day', 'total_calories', 'total_protein', 'total_fat', 'total_carbs')
    search_fields = ['user__username']


class MealAdmin(admin.ModelAdmin):
    actions = [export_to_xlsx_action]
    list_display = ('username', 'course_day', 'meal_type', 'calories', 'protein', 'fat', 'carbs')
    search_fields = ['course_day__user__username']

    def username(self, obj):
        return f"{obj.course_day.user.username} " \
               f"({obj.course_day.user.full_name}), Day {obj.course_day.day}"

    username.short_description = 'User'


my_admin_site = MyAdminSite(name='myadmin')
my_admin_site.register(CourseDay, CourseDayAdmin)
my_admin_site.register(Meal, MealAdmin)
my_admin_site.register(UnpaidUser, UnpaidUserAdmin)
my_admin_site.register(PaidUser, PaidUserAdmin)
my_admin_site.register(FinishedUser, FinishedUserAdmin)
my_admin_site.register(SupportTicket, SupportTicketAdmin)
my_admin_site.register(BankCards, BankCardsAdmin)