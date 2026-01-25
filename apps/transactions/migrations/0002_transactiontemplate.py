# Generated migration for TransactionTemplate

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wallets', '0002_add_credit_limit'),
        ('categories', '0001_initial'),
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Template name (e.g., 'Monthly Rent')", max_length=100)),
                ('description', models.CharField(help_text='Transaction description', max_length=255)),
                ('transaction_type', models.CharField(choices=[('credit', 'Credit (Income)'), ('debit', 'Debit (Expense)')], default='debit', max_length=10)),
                ('default_amount', models.DecimalField(blank=True, decimal_places=2, help_text='Optional default amount', max_digits=12, null=True)),
                ('icon', models.CharField(default='bi-arrow-repeat', max_length=50)),
                ('color', models.CharField(default='#6366f1', max_length=7)),
                ('is_active', models.BooleanField(default=True)),
                ('use_count', models.PositiveIntegerField(default=0, help_text='How many times this template was used')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='templates', to='wallets.account')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='templates', to='categories.category')),
                ('subcategory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='templates', to='categories.subcategory')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction_templates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Transaction Template',
                'verbose_name_plural': 'Transaction Templates',
                'ordering': ['-use_count', 'name'],
            },
        ),
    ]
