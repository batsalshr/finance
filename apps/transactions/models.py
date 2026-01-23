from django.db import models
from django.contrib.auth.models import User
from apps.wallets.models import Account
from apps.categories.models import Category, SubCategory
from decimal import Decimal


class Transaction(models.Model):
    """Financial transaction record"""
    
    TRANSACTION_TYPES = [
        ('credit', 'Credit (Income)'),
        ('debit', 'Debit (Expense)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    
    date = models.DateField()
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='debit')
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        type_symbol = '+' if self.transaction_type == 'credit' else '-'
        return f"{self.date} | {type_symbol}{self.amount} | {self.description}"
    
    @property
    def is_credit(self):
        return self.transaction_type == 'credit'
    
    @property
    def is_debit(self):
        return self.transaction_type == 'debit'
    
    @classmethod
    def get_monthly_summary(cls, user, year, month):
        """Get income and expense summary for a month"""
        from django.db.models import Sum
        from django.db.models.functions import TruncMonth
        
        transactions = cls.objects.filter(
            user=user,
            date__year=year,
            date__month=month
        )
        
        income = transactions.filter(transaction_type='credit').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        expense = transactions.filter(transaction_type='debit').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        return {
            'income': income,
            'expense': expense,
            'net': income - expense
        }
    
    @classmethod
    def get_category_breakdown(cls, user, year=None, month=None):
        """Get spending breakdown by category"""
        from django.db.models import Sum
        
        queryset = cls.objects.filter(user=user, transaction_type='debit')
        
        if year:
            queryset = queryset.filter(date__year=year)
        if month:
            queryset = queryset.filter(date__month=month)
        
        return queryset.values(
            'category__name', 'category__color'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total')
