# Generated migration for credit card payment system

from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0002_add_credit_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='billing_due_date',
            field=models.DateField(blank=True, help_text='Next payment due date for credit cards', null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='minimum_payment',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Minimum payment due for credit cards', max_digits=12),
        ),
        migrations.CreateModel(
            name='CreditCardPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('payment_type', models.CharField(choices=[('full', 'Full Payment'), ('minimum', 'Minimum Payment'), ('partial', 'Partial Payment')], default='partial', max_length=20)),
                ('payment_date', models.DateField()),
                ('balance_before_payment', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('next_due_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('credit_card', models.ForeignKey(limit_choices_to={'account_type': 'credit'}, on_delete=django.db.models.deletion.CASCADE, related_name='cc_payments', to='wallets.account')),
                ('source_account', models.ForeignKey(help_text='Account used to make the payment', on_delete=django.db.models.deletion.CASCADE, related_name='cc_payments_made', to='wallets.account')),
            ],
            options={
                'verbose_name': 'Credit Card Payment',
                'verbose_name_plural': 'Credit Card Payments',
                'ordering': ['-payment_date', '-created_at'],
            },
        ),
    ]
