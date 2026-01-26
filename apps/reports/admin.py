from django.contrib import admin
from .models import MonthlyReport


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'month_name', 'year', 'total_income', 'total_expenses', 'net_savings']
    list_filter = ['year', 'month', 'user']
    ordering = ['-year', '-month']
