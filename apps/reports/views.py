from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse
from django.utils import timezone
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
        context['page_title'] = 'Monthly Reports'
        
        reports = self.get_queryset()
        
        # Calculate all-time totals
        total_income = sum(r.total_income for r in reports)
        total_expenses = sum(r.total_expenses for r in reports)
        total_savings = total_income - total_expenses
        
        # Get current month report
        today = timezone.now().date()
        current_report = reports.filter(year=today.year, month=today.month).first()
        
        # Calculate average monthly spending
        if reports.count() > 0:
            avg_monthly_spending = total_expenses / reports.count()
        else:
            avg_monthly_spending = Decimal('0')
        
        context.update({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'total_savings': total_savings,
            'avg_monthly_spending': avg_monthly_spending,
            'current_report': current_report,
            'currency_symbol': self.request.user.profile.currency_symbol,
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
