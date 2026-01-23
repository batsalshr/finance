from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Account(models.Model):
    """Bank accounts, wallets, cash holdings"""
    
    ACCOUNT_TYPES = [
        ('bank', 'Bank Account'),
        ('wallet', 'Digital Wallet'),
        ('cash', 'Cash'),
        ('savings', 'Savings'),
        ('credit', 'Credit Card'),
    ]
    
    ICON_CHOICES = [
        ('bi-bank', 'Bank'),
        ('bi-wallet2', 'Wallet'),
        ('bi-cash-stack', 'Cash'),
        ('bi-piggy-bank', 'Savings'),
        ('bi-credit-card', 'Credit Card'),
        ('bi-phone', 'Mobile Wallet'),
    ]
    
    COLOR_CHOICES = [
        ('#28a745', 'Green'),
        ('#007bff', 'Blue'),
        ('#ffc107', 'Yellow'),
        ('#dc3545', 'Red'),
        ('#6f42c1', 'Purple'),
        ('#fd7e14', 'Orange'),
        ('#20c997', 'Teal'),
        ('#e83e8c', 'Pink'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='bank')
    initial_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='bi-wallet2')
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default='#28a745')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    include_in_total = models.BooleanField(default=True, help_text="Include in total balance calculation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        ordering = ['name']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"
    
    @property
    def current_balance(self):
        """Calculate current balance from transactions"""
        from apps.transactions.models import Transaction
        
        credits = Transaction.objects.filter(
            account=self,
            transaction_type='credit'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        
        debits = Transaction.objects.filter(
            account=self,
            transaction_type='debit'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        
        return self.initial_balance + credits - debits
    
    @property
    def total_credits(self):
        """Total income to this account"""
        from apps.transactions.models import Transaction
        return Transaction.objects.filter(
            account=self,
            transaction_type='credit'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
    
    @property
    def total_debits(self):
        """Total expenses from this account"""
        from apps.transactions.models import Transaction
        return Transaction.objects.filter(
            account=self,
            transaction_type='debit'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
