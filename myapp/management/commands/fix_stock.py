# Create this file: myapp/management/commands/fix_stock.py
# 
# File structure:
# myapp/
#   management/
#     __init__.py  (create empty file)
#     commands/
#       __init__.py  (create empty file)
#       fix_stock.py  (this file)

from django.core.management.base import BaseCommand
from myapp.models import Part, PartStock


class Command(BaseCommand):
    help = 'Ensures all parts have PartStock entries'

    def handle(self, *args, **options):
        self.stdout.write('Checking all parts for stock entries...')
        
        parts = Part.objects.all()
        created_count = 0
        updated_count = 0
        total_parts = parts.count()
        
        for part in parts:
            try:
                stock = part.stock
                # Stock exists, check if it's valid
                if stock.quantity is None:
                    stock.quantity = 0
                    stock.save()
                    updated_count += 1
                    self.stdout.write(f'  ✓ Fixed stock for: {part.name}')
            except PartStock.DoesNotExist:
                # Create missing stock entry
                PartStock.objects.create(part=part, quantity=0)
                created_count += 1
                self.stdout.write(f'  + Created stock entry for: {part.name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Complete!'))
        self.stdout.write(f'Total parts: {total_parts}')
        self.stdout.write(f'Created stock entries: {created_count}')
        self.stdout.write(f'Updated stock entries: {updated_count}')
        
        if created_count > 0 or updated_count > 0:
            self.stdout.write(self.style.WARNING(f'\n⚠️  Please check admin to set correct quantities!'))