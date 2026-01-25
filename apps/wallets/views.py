from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Account
from .forms import AccountForm


class AccountListView(LoginRequiredMixin, ListView):
    """List all user accounts"""
    model = Account
    template_name = 'wallets/list.html'
    context_object_name = 'accounts'
    
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user).order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        accounts = self.get_queryset()
        
        # Separate regular accounts and credit cards
        regular_accounts = [acc for acc in accounts if not acc.is_credit_card and acc.include_in_total]
        credit_cards = [acc for acc in accounts if acc.is_credit_card and acc.include_in_total]
        
        # Calculate totals
        total_balance = sum(acc.current_balance for acc in regular_accounts)
        total_credit_debt = sum(acc.amount_owed for acc in credit_cards)
        total_savings = sum(acc.savings_amount for acc in regular_accounts)
        
        # Spendable = Total Balance - Savings - Credit Debt
        spendable_balance = total_balance - total_savings - total_credit_debt
        
        context['total_balance'] = total_balance
        context['total_savings'] = total_savings
        context['spendable_balance'] = spendable_balance
        context['total_credit_debt'] = total_credit_debt
        context['currency_symbol'] = self.request.user.profile.currency_symbol
        context['page_title'] = 'Accounts'
        return context


class AccountDetailView(LoginRequiredMixin, DetailView):
    """View account details with transaction history"""
    model = Account
    template_name = 'wallets/detail.html'
    context_object_name = 'account'
    
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = self.object.transactions.all()[:20]
        context['currency_symbol'] = self.request.user.profile.currency_symbol
        context['page_title'] = self.object.name
        return context


class AccountCreateView(LoginRequiredMixin, CreateView):
    """Create new account"""
    model = Account
    form_class = AccountForm
    template_name = 'wallets/form.html'
    success_url = reverse_lazy('wallets:list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Account "{form.instance.name}" created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Account'
        context['button_text'] = 'Create Account'
        context['page_title'] = 'New Account'
        return context


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing account"""
    model = Account
    form_class = AccountForm
    template_name = 'wallets/form.html'
    success_url = reverse_lazy('wallets:list')
    
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, f'Account "{form.instance.name}" updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Account'
        context['button_text'] = 'Update Account'
        context['page_title'] = 'Edit Account'
        return context


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    """Delete account"""
    model = Account
    template_name = 'wallets/confirm_delete.html'
    success_url = reverse_lazy('wallets:list')
    
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, f'Account "{self.object.name}" deleted successfully!')
        return super().form_valid(form)
