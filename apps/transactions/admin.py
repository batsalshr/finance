from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'description', 'amount', 'transaction_type', 'account', 'category', 'user']
    list_filter = ['transaction_type', 'account', 'category', 'date', 'user']
    search_fields = ['description', 'notes', 'user__username']
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'date', 'description', 'amount', 'transaction_type')
        }),
        ('Classification', {
            'fields': ('account', 'category', 'subcategory')
        }),
        ('Additional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
