from django.db import models
from django.contrib.auth.models import User
from apps.wallets.models import Account
from apps.categories.models import Category, SubCategory
from decimal import Decimal
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import os


def receipt_upload_path(instance, filename):
    """Generate upload path for receipts: receipts/user_id/transaction_id/filename"""
    ext = filename.split('.')[-1]
    new_filename = f"receipt_{instance.id or 'new'}_{instance.transaction_id}.{ext}"
    return f"receipts/{instance.transaction.user_id}/{new_filename}"


class TransactionTemplate(models.Model):
    """Recurring transaction template - saves description, category, account for quick entry"""
    
    TRANSACTION_TYPES = [
        ('credit', 'Credit (Income)'),
        ('debit', 'Debit (Expense)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transaction_templates')
    name = models.CharField(max_length=100, help_text="Template name (e.g., 'Monthly Rent')")
    description = models.CharField(max_length=255, help_text="Transaction description")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='templates')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='templates')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='templates')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='debit')
    default_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Optional default amount")
    icon = models.CharField(max_length=50, default='bi-arrow-repeat')
    color = models.CharField(max_length=7, default='#6366f1')
    
    is_active = models.BooleanField(default=True)
    use_count = models.PositiveIntegerField(default=0, help_text="How many times this template was used")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Transaction Template'
        verbose_name_plural = 'Transaction Templates'
        ordering = ['-use_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_transaction_type_display()})"
    
    def increment_use_count(self):
        self.use_count += 1
        self.save(update_fields=['use_count'])


class Transaction(models.Model):
    """Financial transaction record"""
    
    TRANSACTION_TYPES = [
        ('credit', 'Credit (Income)'),
        ('debit', 'Debit (Expense)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    
    date = models.DateField()
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default='debit')
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        type_symbol = '+' if self.transaction_type == 'credit' else '-'
        return f"{self.date} | {type_symbol}{self.amount} | {self.description}"
    
    @property
    def is_credit(self):
        return self.transaction_type == 'credit'
    
    @property
    def is_debit(self):
        return self.transaction_type == 'debit'
    
    @classmethod
    def get_monthly_summary(cls, user, year, month):
        """Get income and expense summary for a month"""
        from django.db.models import Sum
        from django.db.models.functions import TruncMonth
        
        transactions = cls.objects.filter(
            user=user,
            date__year=year,
            date__month=month
        )
        
        income = transactions.filter(transaction_type='credit').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        expense = transactions.filter(transaction_type='debit').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        return {
            'income': income,
            'expense': expense,
            'net': income - expense
        }
    
    @classmethod
    def get_category_breakdown(cls, user, year=None, month=None):
        """Get spending breakdown by category"""
        from django.db.models import Sum
        
        queryset = cls.objects.filter(user=user, transaction_type='debit')
        
        if year:
            queryset = queryset.filter(date__year=year)
        if month:
            queryset = queryset.filter(date__month=month)
        
        return queryset.values(
            'category__name', 'category__color'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total')


class TransactionReceipt(models.Model):
    """Receipt/screenshot images for transactions"""
    
    transaction = models.ForeignKey(
        Transaction, 
        on_delete=models.CASCADE, 
        related_name='receipts'
    )
    image = models.ImageField(upload_to='receipts/')
    original_filename = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(default=0, help_text="File size in bytes")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Transaction Receipt'
        verbose_name_plural = 'Transaction Receipts'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Receipt for {self.transaction.description} ({self.uploaded_at.strftime('%Y-%m-%d')})"
    
    def save(self, *args, **kwargs):
        # Compress image before saving
        if self.image and hasattr(self.image, 'file'):
            self.image = self.compress_image(self.image)
        super().save(*args, **kwargs)
    
    def compress_image(self, uploaded_image):
        """Compress and resize image to ~200KB"""
        try:
            # Open image
            img = Image.open(uploaded_image)
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large (max 1200px width)
            max_width = 1200
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save to buffer with compression
            buffer = BytesIO()
            
            # Start with quality 85, reduce if file too large
            quality = 85
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            
            # If still too large (>250KB), reduce quality
            while buffer.tell() > 250000 and quality > 40:
                buffer.seek(0)
                buffer.truncate()
                quality -= 10
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
            
            buffer.seek(0)
            
            # Store file size
            self.file_size = buffer.tell()
            
            # Generate new filename
            name = uploaded_image.name.rsplit('.', 1)[0]
            new_name = f"{name}.jpg"
            
            # Store original filename
            self.original_filename = uploaded_image.name
            
            # Return new file
            return InMemoryUploadedFile(
                buffer,
                'ImageField',
                new_name,
                'image/jpeg',
                buffer.tell(),
                None
            )
        except Exception as e:
            # If compression fails, return original
            print(f"Image compression failed: {e}")
            return uploaded_image
    
    @property
    def file_size_display(self):
        """Human readable file size"""
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
