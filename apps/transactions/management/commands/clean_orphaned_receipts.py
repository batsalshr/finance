"""
Management command to clean up orphaned receipt records
(receipts where the actual image file no longer exists)
"""
from django.core.management.base import BaseCommand
from apps.transactions.models import TransactionReceipt


class Command(BaseCommand):
    help = 'Remove receipt records where the image file no longer exists'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        receipts = TransactionReceipt.objects.all()
        orphaned = []
        
        for receipt in receipts:
            if not receipt.file_exists:
                orphaned.append(receipt)
        
        if not orphaned:
            self.stdout.write(self.style.SUCCESS('No orphaned receipts found.'))
            return
        
        self.stdout.write(f'Found {len(orphaned)} orphaned receipt(s):')
        
        for receipt in orphaned:
            self.stdout.write(f'  - ID {receipt.id}: {receipt.image.name}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDry run - no records deleted.'))
        else:
            count = len(orphaned)
            for receipt in orphaned:
                receipt.delete()
            self.stdout.write(self.style.SUCCESS(f'\nDeleted {count} orphaned receipt record(s).'))
