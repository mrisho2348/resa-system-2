# app_name/management/commands/update_inventories.py

from django.core.management.base import BaseCommand
from django.db.models.signals import post_save
from django.dispatch import receiver
from clinic.models import MedicineInventory  # Update with your actual model import

class Command(BaseCommand):
    help = 'Manually triggers the signal handler function for existing MedicineInventory instances'

    def handle(self, *args, **kwargs):
        # Define the signal handler function
        @receiver(post_save, sender=MedicineInventory)
        def update_total_payment(sender, instance, created, **kwargs):
            if created or not hasattr(instance, 'total_payment'):
                # Calculate total payment for the inventory
                total_payment = instance.quantity * instance.medicine.unit_price

                # Update the total_payment field of the MedicineInventory instance
                instance.total_payment = total_payment
                instance.save(update_fields=['total_payment'])

        # Manually trigger the signal handler function for existing MedicineInventory instances
        existing_inventories = MedicineInventory.objects.all()
        for inventory in existing_inventories:
            update_total_payment(sender=MedicineInventory, instance=inventory, created=False)
        
        self.stdout.write(self.style.SUCCESS('Successfully updated inventories.'))
