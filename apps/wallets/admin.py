from django.contrib import admin
from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'account_type', 'initial_balance', 'current_balance', 'is_active']
    list_filter = ['account_type', 'is_active', 'user']
    search_fields = ['name', 'user__username']
    ordering = ['user', 'name']
    
    def current_balance(self, obj):
        return obj.current_balance
    current_balance.short_description = 'Current Balance'
