from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Account(models.Model):
    """Bank accounts, wallets, cash holdings, credit cards"""
    
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
    savings_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        help_text="Amount you want to set aside as savings from this account"
    )
    # Credit Card specific fields
    credit_limit = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        help_text="Credit limit for credit cards"
    )
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
    def is_credit_card(self):
        """Check if this is a credit card account"""
        return self.account_type == 'credit'
    
    @property
    def current_balance(self):
        """
        Calculate current balance from transactions.
        For credit cards: positive = amount owed (debt)
        For other accounts: positive = money you have
        """
        from apps.transactions.models import Transaction
        
        credits = Transaction.objects.filter(
            account=self,
            transaction_type='credit'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        
        debits = Transaction.objects.filter(
            account=self,
            transaction_type='debit'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        
        if self.is_credit_card:
            # For credit cards: spending (debit) increases debt, payments (credit) decrease debt
            # initial_balance = starting debt (usually 0)
            return self.initial_balance + debits - credits
        else:
            return self.initial_balance + credits - debits
    
    @property
    def amount_owed(self):
        """For credit cards: how much you owe"""
        if self.is_credit_card:
            return self.current_balance
        return Decimal('0')
    
    @property
    def available_credit(self):
        """For credit cards: how much credit is still available"""
        if self.is_credit_card:
            return self.credit_limit - self.current_balance
        return Decimal('0')
    
    @property
    def credit_utilization(self):
        """For credit cards: percentage of credit limit used"""
        if self.is_credit_card and self.credit_limit > 0:
            return (self.current_balance / self.credit_limit) * 100
        return Decimal('0')
    
    @property
    def actual_balance(self):
        """
        Spendable balance.
        For regular accounts: Current Balance - Savings
        For credit cards: Available Credit (what you can still spend)
        """
        if self.is_credit_card:
            return self.available_credit
        return self.current_balance - self.savings_amount
    
    @property
    def display_balance(self):
        """
        Balance to show as the main number.
        For credit cards: negative of amount owed (shows as debt)
        For others: current balance
        """
        if self.is_credit_card:
            return -self.amount_owed  # Show as negative (debt)
        return self.current_balance
    
    @property
    def total_credits(self):
        """Total income/payments to this account"""
        from apps.transactions.models import Transaction
        return Transaction.objects.filter(
            account=self,
            transaction_type='credit'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
    
    @property
    def total_debits(self):
        """Total expenses/charges from this account"""
        from apps.transactions.models import Transaction
        return Transaction.objects.filter(
            account=self,
            transaction_type='debit'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
