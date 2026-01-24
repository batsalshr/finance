from django import forms
from .models import Account


class AccountForm(forms.ModelForm):
    """Form for creating/editing accounts"""
    
    class Meta:
        model = Account
        fields = ['name', 'account_type', 'initial_balance', 'savings_amount', 'icon', 'color', 'description', 'is_active', 'include_in_total']
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
