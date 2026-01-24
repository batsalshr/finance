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
        
        # Get all user accounts
        accounts = Account.objects.filter(user=user, is_active=True)
        
        # Calculate totals
        # Total Balance = Sum of ALL account current balances (all money you have)
        total_balance = sum(acc.current_balance for acc in accounts)
        
        # Savings Balance = Sum of savings_amount from ALL accounts (money set aside)
        savings_balance = sum(acc.savings_amount for acc in accounts)
        
        # Current Balance = Total Balance - Savings (spendable money)
        current_balance = total_balance - savings_balance
        
        # Recent transactions
        recent_transactions = Transaction.objects.filter(user=user).select_related(
            'account', 'category'
        )[:10]
        
        # Monthly data for charts (last 6 months)
        chart_data = self.get_monthly_chart_data(user)
        
        # Category breakdown for current month
        category_data = self.get_category_breakdown(user)
        
        # Wallet balances
        wallet_balances = [
            {
                'name': acc.name,
                'balance': acc.current_balance,
                'icon': acc.icon,
                'color': acc.color,
                'type': acc.get_account_type_display()
            }
            for acc in accounts
        ]
        
        context.update({
            'total_balance': total_balance,
            'savings_balance': savings_balance,
            'current_balance': current_balance,
            'recent_transactions': recent_transactions,
            'accounts': accounts,
            'wallet_balances': wallet_balances,
            'chart_data': json.dumps(chart_data),
            'category_data': json.dumps(category_data),
            'currency_symbol': user.profile.currency_symbol,
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
