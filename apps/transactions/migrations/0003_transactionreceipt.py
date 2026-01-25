# Generated migration for TransactionReceipt

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_transactiontemplate'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='receipts/')),
                ('original_filename', models.CharField(blank=True, max_length=255)),
                ('file_size', models.PositiveIntegerField(default=0, help_text='File size in bytes')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receipts', to='transactions.transaction')),
            ],
            options={
                'verbose_name': 'Transaction Receipt',
                'verbose_name_plural': 'Transaction Receipts',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
