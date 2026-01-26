from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
import json
import calendar


class MonthlyReport(models.Model):
    """Monthly financial report with category breakdown"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monthly_reports')
    year = models.IntegerField()
    month = models.IntegerField()  # 1-12
    
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Store category breakdown as JSON
    # Format: [{"category_id": 1, "name": "Food", "color": "#ef4444", "icon": "bi-basket", "amount": 5000}, ...]
    category_breakdown = models.JSONField(default=list, blank=True)
    
    # Store income sources as JSON
    income_breakdown = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['user', 'year', 'month']
        verbose_name = 'Monthly Report'
        verbose_name_plural = 'Monthly Reports'
    
    def __str__(self):
        return f"{self.user.username} - {self.month_name} {self.year}"
    
    @property
    def net_savings(self):
        """Net savings (Income - Expenses)"""
        return self.total_income - self.total_expenses
    
    @property
    def month_name(self):
        """Full month name"""
        return calendar.month_name[self.month]
    
    @property
    def short_month_name(self):
        """Abbreviated month name"""
        return calendar.month_abbr[self.month]
    
    @property
    def savings_rate(self):
        """Percentage of income saved"""
        if self.total_income > 0:
            return round((self.net_savings / self.total_income) * 100, 1)
        return 0
    
    @classmethod
    def generate_for_month(cls, user, year, month):
        """Generate or update monthly report for given month"""
        from apps.transactions.models import Transaction
        from django.db.models import Sum
        
        # Get all transactions for this month
        transactions = Transaction.objects.filter(
            user=user,
            date__year=year,
            date__month=month
        )
        
        # Calculate totals
        total_income = transactions.filter(
            transaction_type='credit'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        total_expenses = transactions.filter(
            transaction_type='debit'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Get expense breakdown by category
        expense_breakdown = transactions.filter(
            transaction_type='debit'
        ).values(
            'category__id', 'category__name', 'category__color', 'category__icon'
        ).annotate(
            amount=Sum('amount')
        ).order_by('-amount')
        
        category_breakdown = []
        for item in expense_breakdown:
            category_breakdown.append({
                'category_id': item['category__id'],
                'name': item['category__name'] or 'Uncategorized',
                'color': item['category__color'] or '#6b7280',
                'icon': item['category__icon'] or 'bi-tag',
                'amount': float(item['amount'])
            })
        
        # Get income breakdown by category
        income_by_category = transactions.filter(
            transaction_type='credit'
        ).values(
            'category__id', 'category__name', 'category__color', 'category__icon'
        ).annotate(
            amount=Sum('amount')
        ).order_by('-amount')
        
        income_breakdown = []
        for item in income_by_category:
            income_breakdown.append({
                'category_id': item['category__id'],
                'name': item['category__name'] or 'Other Income',
                'color': item['category__color'] or '#10b981',
                'icon': item['category__icon'] or 'bi-cash',
                'amount': float(item['amount'])
            })
        
        # Update or create report
        report, created = cls.objects.update_or_create(
            user=user,
            year=year,
            month=month,
            defaults={
                'total_income': total_income,
                'total_expenses': total_expenses,
                'category_breakdown': category_breakdown,
                'income_breakdown': income_breakdown,
            }
        )
        
        return report
    
    @classmethod
    def generate_all_for_user(cls, user):
        """Generate reports for all months that have transactions"""
        from apps.transactions.models import Transaction
        from django.db.models.functions import TruncMonth
        
        # Get all unique months with transactions
        months = Transaction.objects.filter(user=user).annotate(
            month_date=TruncMonth('date')
        ).values('month_date').distinct()
        
        reports = []
        for item in months:
            if item['month_date']:
                report = cls.generate_for_month(
                    user,
                    item['month_date'].year,
                    item['month_date'].month
                )
                reports.append(report)
        
        return reports
