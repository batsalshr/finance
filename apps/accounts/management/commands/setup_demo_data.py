"""
Management command to create demo user with sample data
Run with: python manage.py setup_demo_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile
from apps.wallets.models import Account
from apps.categories.models import Category, SubCategory
from apps.transactions.models import Transaction
from decimal import Decimal
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Creates a demo user with sample accounts, categories, and transactions'

    def handle(self, *args, **options):
        self.stdout.write('Setting up demo data...\n')
        
        # Create demo user
        user = self.create_demo_user()
        
        # Create categories
        categories = self.create_categories(user)
        
        # Create accounts
        accounts = self.create_accounts(user)
        
        # Create transactions
        self.create_transactions(user, accounts, categories)
        
        self.stdout.write(self.style.SUCCESS('\n✅ Demo data created successfully!'))
        self.stdout.write(self.style.SUCCESS('━' * 50))
        self.stdout.write(self.style.SUCCESS('Demo Login Credentials:'))
        self.stdout.write(self.style.SUCCESS('  Username: demo'))
        self.stdout.write(self.style.SUCCESS('  Password: demo1234'))
        self.stdout.write(self.style.SUCCESS('━' * 50))

    def create_demo_user(self):
        """Create or get demo user"""
        user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'Ganesh',
                'last_name': 'Kumar',
            }
        )
        
        if created:
            user.set_password('demo1234')
            user.save()
            self.stdout.write(self.style.SUCCESS('✓ Created demo user'))
        else:
            self.stdout.write('  Demo user already exists')
        
        # Update profile
        if hasattr(user, 'profile'):
            user.profile.currency = 'NPR'
            user.profile.save()
        
        return user

    def create_categories(self, user):
        """Create default categories with subcategories (global - shared by all users)"""
        
        categories_data = [
            # Expense Categories
            {
                'name': 'Food',
                'color': '#FF6384',
                'icon': 'bi-cup-hot',
                'category_type': 'expense',
                'subcategories': ['Groceries', 'Restaurants', 'Fast Food', 'Coffee & Tea', 'Snacks']
            },
            {
                'name': 'Transport',
                'color': '#36A2EB',
                'icon': 'bi-car-front',
                'category_type': 'expense',
                'subcategories': ['Fuel', 'Public Transport', 'Taxi/Uber', 'Parking', 'Vehicle Maintenance']
            },
            {
                'name': 'Rent',
                'color': '#9966FF',
                'icon': 'bi-house',
                'category_type': 'expense',
                'subcategories': ['House Rent', 'Office Rent']
            },
            {
                'name': 'Entertainment',
                'color': '#FF9F40',
                'icon': 'bi-film',
                'category_type': 'expense',
                'subcategories': ['Movies', 'Games', 'Concerts', 'Streaming Services', 'Hobbies']
            },
            {
                'name': 'Utilities',
                'color': '#4BC0C0',
                'icon': 'bi-lightning',
                'category_type': 'expense',
                'subcategories': ['Electricity', 'Water', 'Internet', 'Phone', 'Gas']
            },
            {
                'name': 'Shopping',
                'color': '#E91E63',
                'icon': 'bi-cart',
                'category_type': 'expense',
                'subcategories': ['Clothing', 'Electronics', 'Home & Garden', 'Personal Care', 'Gifts']
            },
            {
                'name': 'Health',
                'color': '#7CB342',
                'icon': 'bi-heart-pulse',
                'category_type': 'expense',
                'subcategories': ['Medicine', 'Doctor Visits', 'Gym', 'Insurance']
            },
            {
                'name': 'Education',
                'color': '#00BCD4',
                'icon': 'bi-mortarboard',
                'category_type': 'expense',
                'subcategories': ['Courses', 'Books', 'Tuition', 'Supplies']
            },
            {
                'name': 'Travel',
                'color': '#795548',
                'icon': 'bi-airplane',
                'category_type': 'expense',
                'subcategories': ['Flights', 'Hotels', 'Activities', 'Travel Insurance']
            },
            {
                'name': 'Personal',
                'color': '#607D8B',
                'icon': 'bi-person',
                'category_type': 'expense',
                'subcategories': ['Haircut', 'Spa', 'Subscriptions']
            },
            # Income Categories
            {
                'name': 'Salary',
                'color': '#28a745',
                'icon': 'bi-cash',
                'category_type': 'income',
                'subcategories': ['Monthly Salary', 'Bonus', 'Overtime']
            },
            {
                'name': 'Freelance',
                'color': '#17a2b8',
                'icon': 'bi-briefcase',
                'category_type': 'income',
                'subcategories': ['Projects', 'Consulting', 'Commissions']
            },
            {
                'name': 'Investments',
                'color': '#ffc107',
                'icon': 'bi-graph-up',
                'category_type': 'income',
                'subcategories': ['Dividends', 'Interest', 'Capital Gains']
            },
            {
                'name': 'Other Income',
                'color': '#6c757d',
                'icon': 'bi-three-dots',
                'category_type': 'income',
                'subcategories': ['Gifts Received', 'Refunds', 'Cashback']
            },
        ]
        
        categories = {}
        
        for cat_data in categories_data:
            # Categories are now global (no user field)
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'color': cat_data['color'],
                    'icon': cat_data['icon'],
                    'category_type': cat_data['category_type'],
                    'created_by': user,
                }
            )
            
            if created:
                self.stdout.write(f'  ✓ Created category: {cat_data["name"]}')
                
                # Create subcategories
                for sub_name in cat_data.get('subcategories', []):
                    SubCategory.objects.get_or_create(
                        category=category,
                        name=sub_name
                    )
            
            categories[cat_data['name']] = category
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(categories_data)} categories with subcategories (shared globally)'))
        return categories

    def create_accounts(self, user):
        """Create sample accounts"""
        
        accounts_data = [
            {
                'name': 'eSewa',
                'account_type': 'wallet',
                'initial_balance': Decimal('50000'),
                'icon': 'bi-phone',
                'color': '#28a745',
                'description': 'eSewa Digital Wallet'
            },
            {
                'name': 'Cash',
                'account_type': 'cash',
                'initial_balance': Decimal('15000'),
                'icon': 'bi-cash-stack',
                'color': '#ffc107',
                'description': 'Cash on hand'
            },
            {
                'name': 'Laxmi Bank',
                'account_type': 'bank',
                'initial_balance': Decimal('150000'),
                'icon': 'bi-bank',
                'color': '#dc3545',
                'description': 'Laxmi Sunrise Bank Savings Account'
            },
            {
                'name': 'Siddhartha Bank',
                'account_type': 'bank',
                'initial_balance': Decimal('80000'),
                'icon': 'bi-bank',
                'color': '#fd7e14',
                'description': 'Siddhartha Bank Current Account'
            },
            {
                'name': 'Savings',
                'account_type': 'savings',
                'initial_balance': Decimal('100000'),
                'icon': 'bi-piggy-bank',
                'color': '#6f42c1',
                'description': 'Emergency Fund Savings'
            },
            {
                'name': 'Khalti',
                'account_type': 'wallet',
                'initial_balance': Decimal('25000'),
                'icon': 'bi-wallet2',
                'color': '#5C2D91',
                'description': 'Khalti Digital Wallet'
            },
        ]
        
        accounts = {}
        
        for acc_data in accounts_data:
            account, created = Account.objects.get_or_create(
                user=user,
                name=acc_data['name'],
                defaults={
                    'account_type': acc_data['account_type'],
                    'initial_balance': acc_data['initial_balance'],
                    'icon': acc_data['icon'],
                    'color': acc_data['color'],
                    'description': acc_data['description'],
                }
            )
            
            if created:
                self.stdout.write(f'  ✓ Created account: {acc_data["name"]}')
            
            accounts[acc_data['name']] = account
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(accounts_data)} accounts'))
        return accounts

    def create_transactions(self, user, accounts, categories):
        """Create sample transactions for the last 6 months"""
        
        # Delete existing transactions for demo user (to avoid duplicates on re-run)
        Transaction.objects.filter(user=user).delete()
        
        today = date.today()
        transactions_created = 0
        
        # Sample transaction templates
        expense_templates = [
            ('Food', 'Grocery Shopping', 2000, 5000, 'Groceries'),
            ('Food', 'Restaurant Dinner', 800, 2500, 'Restaurants'),
            ('Food', 'Coffee Shop', 150, 400, 'Coffee & Tea'),
            ('Transport', 'Fuel', 1500, 3000, 'Fuel'),
            ('Transport', 'Uber Ride', 200, 800, 'Taxi/Uber'),
            ('Transport', 'Bus Fare', 50, 200, 'Public Transport'),
            ('Rent', 'House Rent', 20000, 20000, 'House Rent'),
            ('Entertainment', 'Movie Tickets', 500, 1500, 'Movies'),
            ('Entertainment', 'Netflix Subscription', 1500, 1500, 'Streaming Services'),
            ('Utilities', 'Electricity Bill', 800, 2500, 'Electricity'),
            ('Utilities', 'Internet Bill', 1200, 1500, 'Internet'),
            ('Utilities', 'Phone Recharge', 500, 1000, 'Phone'),
            ('Shopping', 'Clothing Purchase', 2000, 8000, 'Clothing'),
            ('Shopping', 'Electronics', 3000, 15000, 'Electronics'),
            ('Health', 'Medicine', 300, 1500, 'Medicine'),
            ('Health', 'Gym Membership', 2500, 2500, 'Gym'),
            ('Education', 'Online Course', 1500, 5000, 'Courses'),
            ('Personal', 'Haircut', 300, 800, 'Haircut'),
        ]
        
        income_templates = [
            ('Salary', 'Monthly Salary', 50000, 75000, 'Monthly Salary'),
            ('Freelance', 'Freelance Project', 10000, 30000, 'Projects'),
            ('Investments', 'Bank Interest', 500, 2000, 'Interest'),
            ('Other Income', 'Cashback Reward', 100, 500, 'Cashback'),
        ]
        
        account_list = list(accounts.values())
        
        # Generate transactions for last 6 months
        for month_offset in range(6):
            month_date = today - timedelta(days=30 * month_offset)
            
            # Add salary at the start of each month
            if 'Salary' in categories:
                salary_date = date(month_date.year, month_date.month, 1)
                if salary_date <= today:
                    Transaction.objects.create(
                        user=user,
                        account=accounts.get('Laxmi Bank', account_list[0]),
                        category=categories['Salary'],
                        date=salary_date,
                        description='Monthly Salary',
                        amount=Decimal(random.randint(50000, 75000)),
                        transaction_type='credit',
                        notes='Regular monthly salary'
                    )
                    transactions_created += 1
            
            # Add random expenses throughout the month
            for day in range(1, 29):
                trans_date = date(month_date.year, month_date.month, min(day, 28))
                if trans_date > today:
                    continue
                
                # 60% chance of having a transaction on any given day
                if random.random() < 0.6:
                    # Pick 1-3 random expenses for this day
                    num_expenses = random.randint(1, 3)
                    for _ in range(num_expenses):
                        template = random.choice(expense_templates)
                        cat_name, desc, min_amt, max_amt, subcat_name = template
                        
                        if cat_name in categories:
                            category = categories[cat_name]
                            subcategory = category.subcategories.filter(name=subcat_name).first()
                            
                            Transaction.objects.create(
                                user=user,
                                account=random.choice(account_list),
                                category=category,
                                subcategory=subcategory,
                                date=trans_date,
                                description=desc,
                                amount=Decimal(random.randint(min_amt, max_amt)),
                                transaction_type='debit',
                            )
                            transactions_created += 1
                
                # 10% chance of additional income
                if random.random() < 0.1:
                    template = random.choice(income_templates[1:])  # Exclude salary
                    cat_name, desc, min_amt, max_amt, subcat_name = template
                    
                    if cat_name in categories:
                        category = categories[cat_name]
                        
                        Transaction.objects.create(
                            user=user,
                            account=random.choice(account_list),
                            category=category,
                            date=trans_date,
                            description=desc,
                            amount=Decimal(random.randint(min_amt, max_amt)),
                            transaction_type='credit',
                        )
                        transactions_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created {transactions_created} transactions'))
