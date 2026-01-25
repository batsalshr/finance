from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
import csv
from io import TextIOWrapper
from datetime import datetime

from .models import Transaction, TransactionTemplate, TransactionReceipt
from .forms import TransactionForm, BulkTransactionForm, TransactionFilterForm, TransactionTemplateForm, QuickTransactionForm, ReceiptUploadForm
from apps.wallets.models import Account
from apps.categories.models import Category


class TransactionListView(LoginRequiredMixin, ListView):
    """List all transactions with filtering"""
    model = Transaction
    template_name = 'transactions/list.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Transaction.objects.filter(
            user=self.request.user
        ).select_related('account', 'category', 'subcategory')
        
        # Apply filters
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        transaction_type = self.request.GET.get('transaction_type')
        account = self.request.GET.get('account')
        category = self.request.GET.get('category')
        search = self.request.GET.get('search')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        if account:
            queryset = queryset.filter(account_id=account)
        if category:
            queryset = queryset.filter(category_id=category)
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) | 
                Q(notes__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TransactionFilterForm(
            user=self.request.user,
            data=self.request.GET
        )
        context['currency_symbol'] = self.request.user.profile.currency_symbol
        context['page_title'] = 'Transactions'
        return context


class TransactionDetailView(LoginRequiredMixin, DetailView):
    """View transaction details"""
    model = Transaction
    template_name = 'transactions/detail.html'
    context_object_name = 'transaction'
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).prefetch_related('receipts')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['currency_symbol'] = self.request.user.profile.currency_symbol
        context['page_title'] = 'Transaction Details'
        context['receipts'] = self.object.receipts.all()
        context['upload_form'] = ReceiptUploadForm()
        return context


class ReceiptUploadView(LoginRequiredMixin, View):
    """Handle receipt image uploads"""
    
    def post(self, request, transaction_id):
        transaction = get_object_or_404(Transaction, pk=transaction_id, user=request.user)
        
        files = request.FILES.getlist('images')
        
        if not files:
            messages.error(request, 'No images selected')
            return redirect('transactions:detail', pk=transaction_id)
        
        uploaded_count = 0
        for f in files:
            # Validate file type
            if not f.content_type.startswith('image/'):
                messages.warning(request, f'Skipped {f.name} - not an image')
                continue
            
            # Create receipt
            receipt = TransactionReceipt(
                transaction=transaction,
                image=f
            )
            receipt.save()
            uploaded_count += 1
        
        if uploaded_count > 0:
            messages.success(request, f'Uploaded {uploaded_count} receipt(s)')
        
        return redirect('transactions:detail', pk=transaction_id)


class ReceiptDeleteView(LoginRequiredMixin, View):
    """Delete a receipt image"""
    
    def post(self, request, pk):
        receipt = get_object_or_404(TransactionReceipt, pk=pk, transaction__user=request.user)
        transaction_id = receipt.transaction_id
        
        # Delete the file
        if receipt.image:
            receipt.image.delete(save=False)
        receipt.delete()
        
        messages.success(request, 'Receipt deleted')
        return redirect('transactions:detail', pk=transaction_id)


class TransactionCreateView(LoginRequiredMixin, CreateView):
    """Create new transaction"""
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/form.html'
    success_url = reverse_lazy('transactions:list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # Handle receipt uploads
        files = self.request.FILES.getlist('receipts')
        for f in files:
            if f.content_type.startswith('image/'):
                TransactionReceipt.objects.create(
                    transaction=self.object,
                    image=f
                )
        
        receipt_count = len(files)
        if receipt_count > 0:
            messages.success(self.request, f'Transaction added with {receipt_count} receipt(s)!')
        else:
            messages.success(self.request, 'Transaction added successfully!')
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Transaction'
        context['button_text'] = 'Add Transaction'
        context['page_title'] = 'New Transaction'
        return context


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing transaction"""
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/form.html'
    success_url = reverse_lazy('transactions:list')
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Handle receipt uploads
        files = self.request.FILES.getlist('receipts')
        for f in files:
            if f.content_type.startswith('image/'):
                TransactionReceipt.objects.create(
                    transaction=self.object,
                    image=f
                )
        
        receipt_count = len(files)
        if receipt_count > 0:
            messages.success(self.request, f'Transaction updated with {receipt_count} new receipt(s)!')
        else:
            messages.success(self.request, 'Transaction updated successfully!')
        
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Transaction'
        context['button_text'] = 'Update Transaction'
        context['page_title'] = 'Edit Transaction'
        context['existing_receipts'] = self.object.receipts.all()
        return context


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    """Delete transaction"""
    model = Transaction
    template_name = 'transactions/confirm_delete.html'
    success_url = reverse_lazy('transactions:list')
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Transaction deleted successfully!')
        return super().form_valid(form)


class BulkImportView(LoginRequiredMixin, FormView):
    """Bulk import transactions from CSV"""
    template_name = 'transactions/bulk_import.html'
    form_class = BulkTransactionForm
    success_url = reverse_lazy('transactions:list')
    
    def form_valid(self, form):
        csv_file = form.cleaned_data['csv_file']
        user = self.request.user
        
        try:
            # Read CSV file
            csv_file_wrapper = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.DictReader(csv_file_wrapper)
            
            created_count = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Parse date
                    date_str = row.get('date', '').strip()
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except ValueError:
                        date = datetime.strptime(date_str, '%d/%m/%Y').date()
                    
                    # Get or create account
                    account_name = row.get('account', '').strip()
                    account = Account.objects.filter(user=user, name__iexact=account_name).first()
                    
                    if not account:
                        account = Account.objects.create(
                            user=user,
                            name=account_name,
                            account_type='bank'
                        )
                    
                    # Get category if provided
                    category_name = row.get('category', '').strip()
                    category = None
                    if category_name:
                        category = Category.objects.filter(user=user, name__iexact=category_name).first()
                        if not category:
                            category = Category.objects.create(user=user, name=category_name)
                    
                    # Create transaction
                    Transaction.objects.create(
                        user=user,
                        date=date,
                        description=row.get('description', '').strip(),
                        amount=float(row.get('amount', 0)),
                        transaction_type=row.get('type', 'debit').strip().lower(),
                        account=account,
                        category=category,
                        notes=row.get('notes', '').strip()
                    )
                    created_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            if created_count > 0:
                messages.success(self.request, f'Successfully imported {created_count} transactions!')
            
            if errors:
                messages.warning(self.request, f'Some rows had errors: {"; ".join(errors[:5])}')
                
        except Exception as e:
            messages.error(self.request, f'Error processing file: {str(e)}')
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sample_csv'] = "date,description,amount,type,account,category,notes\n2024-01-15,Grocery Shopping,3000,debit,Cash,Food,Weekly groceries"
        context['page_title'] = 'Import Transactions'
        return context


# ============ Transaction Templates ============

class TemplateListView(LoginRequiredMixin, ListView):
    """List all transaction templates"""
    model = TransactionTemplate
    template_name = 'transactions/templates/list.html'
    context_object_name = 'templates'
    
    def get_queryset(self):
        return TransactionTemplate.objects.filter(user=self.request.user, is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Quick Add'
        context['currency_symbol'] = self.request.user.profile.currency_symbol
        return context


class TemplateCreateView(LoginRequiredMixin, CreateView):
    """Create new transaction template"""
    model = TransactionTemplate
    form_class = TransactionTemplateForm
    template_name = 'transactions/templates/form.html'
    success_url = reverse_lazy('transactions:template_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Template "{form.instance.name}" created!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Template'
        context['button_text'] = 'Create Template'
        context['page_title'] = 'New Template'
        return context


class TemplateUpdateView(LoginRequiredMixin, UpdateView):
    """Update transaction template"""
    model = TransactionTemplate
    form_class = TransactionTemplateForm
    template_name = 'transactions/templates/form.html'
    success_url = reverse_lazy('transactions:template_list')
    
    def get_queryset(self):
        return TransactionTemplate.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, f'Template "{form.instance.name}" updated!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Template'
        context['button_text'] = 'Update Template'
        context['page_title'] = 'Edit Template'
        return context


class TemplateDeleteView(LoginRequiredMixin, DeleteView):
    """Delete transaction template"""
    model = TransactionTemplate
    template_name = 'transactions/templates/confirm_delete.html'
    success_url = reverse_lazy('transactions:template_list')
    
    def get_queryset(self):
        return TransactionTemplate.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Template deleted!')
        return super().form_valid(form)


class QuickAddView(LoginRequiredMixin, View):
    """Quick add transaction from template"""
    template_name = 'transactions/templates/quick_add.html'
    
    def get(self, request, pk):
        template = get_object_or_404(TransactionTemplate, pk=pk, user=request.user)
        form = QuickTransactionForm(initial={
            'amount': template.default_amount,
            'date': timezone.now().date()
        })
        return render(request, self.template_name, {
            'template': template,
            'form': form,
            'page_title': f'Add {template.name}',
            'currency_symbol': request.user.profile.currency_symbol
        })
    
    def post(self, request, pk):
        template = get_object_or_404(TransactionTemplate, pk=pk, user=request.user)
        form = QuickTransactionForm(request.POST)
        
        if form.is_valid():
            # Create transaction from template
            Transaction.objects.create(
                user=request.user,
                account=template.account,
                category=template.category,
                subcategory=template.subcategory,
                date=form.cleaned_data['date'],
                description=template.description,
                amount=form.cleaned_data['amount'],
                transaction_type=template.transaction_type,
                notes=form.cleaned_data.get('notes', '')
            )
            
            # Increment use count
            template.increment_use_count()
            
            messages.success(request, f'Added {template.name}: {request.user.profile.currency_symbol}{form.cleaned_data["amount"]}')
            return redirect('transactions:template_list')
        
        return render(request, self.template_name, {
            'template': template,
            'form': form,
            'page_title': f'Add {template.name}',
            'currency_symbol': request.user.profile.currency_symbol
        })
