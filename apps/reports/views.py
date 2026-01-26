from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal

from .models import MonthlyReport


class MonthlyReportsView(LoginRequiredMixin, ListView):
    """View all monthly reports"""
    model = MonthlyReport
    template_name = 'reports/monthly_list.html'
    context_object_name = 'reports'
    
    def get_queryset(self):
        # Generate reports for all months first
        MonthlyReport.generate_all_for_user(self.request.user)
        return MonthlyReport.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Reports'
        
        user = self.request.user
        reports = list(self.get_queryset())
        
        # Calculate all-time totals directly from transactions for accuracy
        from apps.transactions.models import Transaction
        
        all_time_income = Transaction.objects.filter(
            user=user, transaction_type='credit'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        all_time_expenses = Transaction.objects.filter(
            user=user, transaction_type='debit'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        all_time_savings = all_time_income - all_time_expenses
        
        # Get current month report
        today = timezone.now().date()
        current_report = next((r for r in reports if r.year == today.year and r.month == today.month), None)
        
        # Calculate average monthly spending (only from months with activity)
        months_with_expenses = [r for r in reports if r.total_expenses > 0]
        if months_with_expenses:
            avg_monthly_spending = sum(r.total_expenses for r in months_with_expenses) / len(months_with_expenses)
        else:
            avg_monthly_spending = Decimal('0')
        
        # Get total transaction count
        total_transactions = Transaction.objects.filter(user=user).count()
        
        context.update({
            'all_time_income': all_time_income,
            'all_time_expenses': all_time_expenses,
            'all_time_savings': all_time_savings,
            'avg_monthly_spending': avg_monthly_spending,
            'current_report': current_report,
            'total_transactions': total_transactions,
            'total_months': len(reports),
            'currency_symbol': user.profile.currency_symbol,
            'current_month': today.strftime('%B'),
            'current_year': today.year,
        })
        
        return context


class MonthlyReportDetailView(LoginRequiredMixin, DetailView):
    """View detailed report for a specific month"""
    model = MonthlyReport
    template_name = 'reports/monthly_detail.html'
    context_object_name = 'report'
    
    def get_queryset(self):
        return MonthlyReport.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = self.object
        
        context['page_title'] = f'{report.month_name} {report.year}'
        context['currency_symbol'] = self.request.user.profile.currency_symbol
        
        # Get transactions for this month
        from apps.transactions.models import Transaction
        context['transactions'] = Transaction.objects.filter(
            user=self.request.user,
            date__year=report.year,
            date__month=report.month
        ).select_related('category', 'account')[:20]
        
        return context


class RefreshReportsView(LoginRequiredMixin, View):
    """Manually refresh all reports"""
    
    def post(self, request):
        reports = MonthlyReport.generate_all_for_user(request.user)
        return JsonResponse({
            'success': True,
            'count': len(reports)
        })
