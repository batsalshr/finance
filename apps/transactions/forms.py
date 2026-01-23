from django import forms
from .models import Transaction
from apps.wallets.models import Account
from apps.categories.models import Category, SubCategory


class TransactionForm(forms.ModelForm):
    """Form for creating/editing transactions"""
    
    class Meta:
        model = Transaction
        fields = ['date', 'description', 'amount', 'transaction_type', 'account', 'category', 'subcategory', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Transaction description'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'account': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subcategory': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional notes'
            }),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter accounts by user (accounts are still user-specific)
        self.fields['account'].queryset = Account.objects.filter(user=user, is_active=True)
        # Categories are now global - show all active categories
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['subcategory'].queryset = SubCategory.objects.filter(is_active=True)
        
        # Make subcategory optional
        self.fields['subcategory'].required = False
        self.fields['category'].required = False
        self.fields['notes'].required = False


class BulkTransactionForm(forms.Form):
    """Form for bulk CSV import"""
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        help_text='Upload a CSV file with columns: date, description, amount, type (credit/debit), account, category'
    )
    
    def clean_csv_file(self):
        file = self.cleaned_data['csv_file']
        if not file.name.endswith('.csv'):
            raise forms.ValidationError('File must be a CSV file')
        return file


class TransactionFilterForm(forms.Form):
    """Form for filtering transactions"""
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    transaction_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All'), ('credit', 'Credit'), ('debit', 'Debit')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    account = forms.ModelChoiceField(
        required=False,
        queryset=Account.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='All Accounts'
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='All Categories'
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = Account.objects.filter(user=user, is_active=True)
        # Categories are global
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
