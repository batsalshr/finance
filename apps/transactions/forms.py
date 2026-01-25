from django import forms
from django.forms.widgets import ClearableFileInput
from .models import Transaction, TransactionTemplate, TransactionReceipt
from apps.wallets.models import Account
from apps.categories.models import Category, SubCategory


class MultipleFileInput(forms.ClearableFileInput):
    """Custom widget that allows multiple file selection"""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Custom field for handling multiple files"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class ReceiptUploadForm(forms.Form):
    """Form for uploading receipt images"""
    images = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        })
    )


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


class TransactionTemplateForm(forms.ModelForm):
    """Form for creating/editing transaction templates"""
    
    class Meta:
        model = TransactionTemplate
        fields = ['name', 'description', 'account', 'category', 'subcategory', 'transaction_type', 'default_amount', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Monthly Rent, Salary, Netflix'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Transaction description that will appear'
            }),
            'account': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'subcategory': forms.Select(attrs={'class': 'form-select'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'default_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional - leave empty to enter each time',
                'step': '0.01',
                'min': '0'
            }),
            'icon': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={
                'class': 'form-control form-control-color',
                'type': 'color'
            }),
        }
    
    ICON_CHOICES = [
        ('bi-arrow-repeat', '🔄 Recurring'),
        ('bi-house', '🏠 Home/Rent'),
        ('bi-lightning', '⚡ Utilities'),
        ('bi-wifi', '📶 Internet'),
        ('bi-phone', '📱 Phone'),
        ('bi-tv', '📺 Streaming'),
        ('bi-car-front', '🚗 Car/Transport'),
        ('bi-fuel-pump', '⛽ Fuel'),
        ('bi-bag', '🛍️ Shopping'),
        ('bi-cart', '🛒 Groceries'),
        ('bi-cup-hot', '☕ Coffee'),
        ('bi-currency-dollar', '💰 Salary'),
        ('bi-briefcase', '💼 Business'),
        ('bi-heart', '❤️ Health'),
        ('bi-book', '📚 Education'),
        ('bi-gift', '🎁 Gift'),
        ('bi-controller', '🎮 Entertainment'),
        ('bi-music-note', '🎵 Music'),
        ('bi-film', '🎬 Movies'),
    ]
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = Account.objects.filter(user=user, is_active=True)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['subcategory'].queryset = SubCategory.objects.filter(is_active=True)
        
        self.fields['subcategory'].required = False
        self.fields['category'].required = False
        self.fields['default_amount'].required = False
        
        # Set icon choices
        self.fields['icon'] = forms.ChoiceField(
            choices=self.ICON_CHOICES,
            widget=forms.Select(attrs={'class': 'form-select'})
        )


class QuickTransactionForm(forms.Form):
    """Form for quickly adding transaction from template"""
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter amount',
            'step': '0.01',
            'min': '0',
            'autofocus': True
        })
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Optional notes'
        })
    )


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
