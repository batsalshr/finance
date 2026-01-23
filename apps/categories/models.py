from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """Transaction category (e.g., Food, Transport, Rent)"""
    
    COLOR_CHOICES = [
        ('#FF6384', 'Red'),
        ('#36A2EB', 'Blue'),
        ('#FFCE56', 'Yellow'),
        ('#4BC0C0', 'Teal'),
        ('#9966FF', 'Purple'),
        ('#FF9F40', 'Orange'),
        ('#7CB342', 'Green'),
        ('#E91E63', 'Pink'),
        ('#00BCD4', 'Cyan'),
        ('#795548', 'Brown'),
        ('#607D8B', 'Grey'),
        ('#3F51B5', 'Indigo'),
    ]
    
    ICON_CHOICES = [
        ('bi-cart', 'Shopping Cart'),
        ('bi-house', 'House'),
        ('bi-car-front', 'Car'),
        ('bi-cup-hot', 'Food/Drink'),
        ('bi-lightning', 'Utilities'),
        ('bi-film', 'Entertainment'),
        ('bi-heart-pulse', 'Health'),
        ('bi-mortarboard', 'Education'),
        ('bi-airplane', 'Travel'),
        ('bi-gift', 'Gifts'),
        ('bi-briefcase', 'Work'),
        ('bi-cash', 'Income'),
        ('bi-piggy-bank', 'Savings'),
        ('bi-three-dots', 'Other'),
    ]
    
    CATEGORY_TYPES = [
        ('expense', 'Expense'),
        ('income', 'Income'),
        ('both', 'Both'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, choices=COLOR_CHOICES, default='#36A2EB')
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='bi-three-dots')
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES, default='expense')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def total_spent(self):
        """Calculate total spent in this category"""
        from apps.transactions.models import Transaction
        return Transaction.objects.filter(
            category=self,
            transaction_type='debit'
        ).aggregate(total=models.Sum('amount'))['total'] or 0


class SubCategory(models.Model):
    """Sub-category for more detailed categorization"""
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Sub Category'
        verbose_name_plural = 'Sub Categories'
        ordering = ['name']
        unique_together = ['category', 'name']
    
    def __str__(self):
        return f"{self.category.name} → {self.name}"
