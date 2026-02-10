from django.contrib import admin
from .models import Account, CreditCardPayment


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'account_type', 'initial_balance', 'current_balance', 'billing_due_date', 'is_active']
    list_filter = ['account_type', 'is_active', 'user']
    search_fields = ['name', 'user__username']
    ordering = ['user', 'name']
    
    def current_balance(self, obj):
        return obj.current_balance
    current_balance.short_description = 'Current Balance'


@admin.register(CreditCardPayment)
class CreditCardPaymentAdmin(admin.ModelAdmin):
    list_display = ['credit_card', 'source_account', 'amount', 'payment_type', 'payment_date']
    list_filter = ['payment_type', 'payment_date', 'credit_card']
    search_fields = ['credit_card__name', 'source_account__name']
    ordering = ['-payment_date']
