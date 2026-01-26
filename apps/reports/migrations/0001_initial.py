# Generated migration for MonthlyReport

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlyReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('total_income', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('total_expenses', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12)),
                ('category_breakdown', models.JSONField(blank=True, default=list)),
                ('income_breakdown', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='monthly_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Monthly Report',
                'verbose_name_plural': 'Monthly Reports',
                'ordering': ['-year', '-month'],
                'unique_together': {('user', 'year', 'month')},
            },
        ),
    ]
