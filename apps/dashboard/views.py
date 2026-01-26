from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta

from apps.wallets.models import Account
from apps.transactions.models import Transaction
from apps.categories.models import Category
import json


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view with financial overview"""
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()
        
        # Get all user accounts
        all_accounts = Account.objects.filter(user=user, is_active=True)
        
        # Separate regular accounts and credit cards
        regular_accounts = [acc for acc in all_accounts if not acc.is_credit_card]
        credit_cards = [acc for acc in all_accounts if acc.is_credit_card]
        
        # Calculate totals (ONLY from regular accounts - credit cards excluded)
        total_balance = sum(acc.current_balance for acc in regular_accounts if acc.include_in_total)
        
        # Savings Balance = Sum of savings_amount from regular accounts
        savings_balance = sum(acc.savings_amount for acc in regular_accounts)
        
        # Available/Spendable = Total Balance - Savings (credit cards NOT factored in)
        current_balance = total_balance - savings_balance
        
        # This month's spending and income
        this_month_expenses = Transaction.objects.filter(
            user=user,
            transaction_type='debit',
            date__year=today.year,
            date__month=today.month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        this_month_income = Transaction.objects.filter(
            user=user,
            transaction_type='credit',
            date__year=today.year,
            date__month=today.month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Recent transactions
        recent_transactions = Transaction.objects.filter(user=user).select_related(
            'account', 'category'
        )[:10]
        
        # Monthly data for charts (last 6 months)
        chart_data = self.get_monthly_chart_data(user)
        
        # Category breakdown for current month
        category_data = self.get_category_breakdown(user)
        
        context.update({
            'page_title': 'Dashboard',
            'total_balance': total_balance,
            'savings_balance': savings_balance,
            'current_balance': current_balance,
            'this_month_expenses': this_month_expenses,
            'this_month_income': this_month_income,
            'recent_transactions': recent_transactions,
            'accounts': regular_accounts,  # Only regular accounts in accounts grid
            'credit_cards': credit_cards,  # Separate credit cards list
            'chart_data': json.dumps(chart_data),
            'category_data': json.dumps(category_data),
            'currency_symbol': user.profile.currency_symbol,
            'current_month': today.strftime('%B'),
        })
        
        return context
    
    def get_monthly_chart_data(self, user):
        """Get income vs expense data for the last 6 months"""
        today = timezone.now().date()
        six_months_ago = today - timedelta(days=180)
        
        # Get monthly aggregates
        transactions = Transaction.objects.filter(
            user=user,
            date__gte=six_months_ago
        ).annotate(
            month=TruncMonth('date')
        ).values('month', 'transaction_type').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        # Organize by month
        months_data = {}
        for t in transactions:
            month_key = t['month'].strftime('%b')
            if month_key not in months_data:
                months_data[month_key] = {'income': 0, 'expense': 0}
            
            if t['transaction_type'] == 'credit':
                months_data[month_key]['income'] = float(t['total'])
            else:
                months_data[month_key]['expense'] = float(t['total'])
        
        # Generate last 6 months labels
        labels = []
        income = []
        expenses = []
        
        for i in range(5, -1, -1):
            month_date = today - timedelta(days=30 * i)
            month_label = month_date.strftime('%b')
            labels.append(month_label)
            
            if month_label in months_data:
                income.append(months_data[month_label]['income'])
                expenses.append(months_data[month_label]['expense'])
            else:
                income.append(0)
                expenses.append(0)
        
        return {
            'labels': labels,
            'income': income,
            'expenses': expenses
        }
    
    def get_category_breakdown(self, user):
        """Get expense breakdown by category for current month"""
        today = timezone.now().date()
        
        breakdown = Transaction.objects.filter(
            user=user,
            transaction_type='debit',
            date__year=today.year,
            date__month=today.month
        ).values(
            'category__name', 'category__color'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        labels = []
        data = []
        colors = []
        
        for item in breakdown:
            if item['category__name']:
                labels.append(item['category__name'])
                data.append(float(item['total']))
                colors.append(item['category__color'] or '#36A2EB')
        
        # If no transactions, add placeholder
        if not labels:
            labels = ['No expenses']
            data = [0]
            colors = ['#E0E0E0']
        
        return {
            'labels': labels,
            'data': data,
            'colors': colors
        }
