from django import forms
from django.utils import timezone
from .models import Account, CreditCardPayment


class AccountForm(forms.ModelForm):
    """Form for creating/editing accounts"""
    
    class Meta:
        model = Account
        fields = ['name', 'account_type', 'initial_balance', 'credit_limit', 'billing_due_date', 'minimum_payment', 'savings_amount', 'icon', 'color', 'description', 'is_active', 'include_in_total']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Account name (e.g., eSewa, Laxmi Bank)'
            }),
            'account_type': forms.Select(attrs={'class': 'form-select'}),
            'initial_balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'credit_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'billing_due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'minimum_payment': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'savings_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'icon': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional description'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_in_total': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CreditCardPaymentForm(forms.ModelForm):
    """Form for making credit card payments"""
    
    class Meta:
        model = CreditCardPayment
        fields = ['source_account', 'amount', 'payment_type', 'payment_date', 'next_due_date', 'notes']
        widgets = {
            'source_account': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'payment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'next_due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional notes'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.credit_card = kwargs.pop('credit_card', None)
        super().__init__(*args, **kwargs)
        
        # Filter source accounts to only show user's non-credit accounts
        if self.user:
            self.fields['source_account'].queryset = Account.objects.filter(
                user=self.user,
                is_active=True
            ).exclude(account_type='credit')
        
        # Set default payment date to today
        self.fields['payment_date'].initial = timezone.now().date()
        
        # Set default next due date if credit card has one
        if self.credit_card and self.credit_card.billing_due_date:
            # Suggest next month's due date (same day next month)
            current_due = self.credit_card.billing_due_date
            if current_due.month == 12:
                next_due = current_due.replace(year=current_due.year + 1, month=1)
            else:
                try:
                    next_due = current_due.replace(month=current_due.month + 1)
                except ValueError:
                    # Handle months with different day counts
                    import calendar
                    last_day = calendar.monthrange(current_due.year, current_due.month + 1)[1]
                    next_due = current_due.replace(month=current_due.month + 1, day=min(current_due.day, last_day))
            self.fields['next_due_date'].initial = next_due
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        source_account = self.cleaned_data.get('source_account')
        
        if amount <= 0:
            raise forms.ValidationError('Payment amount must be greater than 0')
        
        # Check if source account has enough balance
        if source_account and amount > source_account.current_balance:
            raise forms.ValidationError(
                f'Insufficient balance in {source_account.name}. Available: {source_account.current_balance}'
            )
        
        return amount
