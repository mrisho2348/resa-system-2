# clinic/signals.py

from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver


from .models import AmbulanceOrder, Consultation, ConsultationNotification, ConsultationOrder, DeductionOrganization, EmployeeDeduction, ImagingRecord, InventoryItem, LaboratoryOrder, MedicationPayment, MedicineInventory, Order, Prescription, Procedure, Reagent, ReagentUsage, RemotePrescription, SalaryChangeRecord, SalaryPayment, UsageHistory
from django.db.models import F
from django.db import models

@receiver(post_save, sender=MedicationPayment)
def update_inventory(sender, instance, **kwargs):
    if kwargs.get('created', False) or kwargs.get('update_fields', None):
        # Use F() expression to perform the update in the database
        MedicineInventory.objects.filter(medicine=instance.medicine).update(remain_quantity=F('remain_quantity') - instance.quantity)
        


@receiver(post_save, sender=Consultation)
def create_consultation_notification(sender, instance, created, **kwargs):
    if created:
        # Create a ConsultationNotification object for the newly created Consultation
        ConsultationNotification.objects.create(
            consultation=instance,
            doctor=instance.doctor,
            is_read=False  # Default to unread
        )
@receiver(post_save, sender=MedicineInventory)
def update_total_payment(sender, instance, created, **kwargs):
    if created:
        # Calculate total payment for the inventory
        total_payment = instance.quantity * instance.medicine.unit_price
        
        # Update the total_payment field of the MedicineInventory instance
        instance.total_payment = total_payment
        instance.save(update_fields=['total_payment'])  
              

               
@receiver(post_save, sender=RemotePrescription)
def update_total_payment_prescription(sender, instance, created, **kwargs):
    if created:
        # Calculate total payment for the inventory
        total_price = instance.quantity_used * instance.medicine.unit_cost
        
        # Update the total_payment field of the MedicineInventory instance
        instance.total_price = total_price
        instance.save(update_fields=['total_price'])        
        
@receiver(post_save, sender=ReagentUsage)
def update_reagent_usage(sender, instance, **kwargs):
    if kwargs.get('created', False) or kwargs.get('update_fields', None):
        # Use F() expression to perform the update in the database
        Reagent.objects.filter(id=instance.reagent_id).update(remaining_quantity=F('remaining_quantity') - instance.quantity_used)
        

@receiver(post_save, sender=UsageHistory)
def update_quantity_from_usage_history(sender, instance, **kwargs):
    # Calculate the total quantity used based on associated UsageHistory entries
    total_used = UsageHistory.objects.filter(inventory_item=instance.inventory_item).aggregate(models.Sum('quantity_used'))['quantity_used__sum']
    
    # Update the remaining quantity using an f expression
    InventoryItem.objects.filter(pk=instance.inventory_item.pk).update(remain_quantity=F('quantity') - total_used)
    
@receiver(post_save, sender=Prescription)
def update_medicine_inventory_per_prescription(sender, instance, created, **kwargs):
    if created:
        # Deduct quantity from MedicineInventory when a new Prescription is created
        try:
            medicine_inventory = MedicineInventory.objects.get(medicine=instance.medicine)
            medicine_inventory.remain_quantity -= instance.quantity_used
            medicine_inventory.save()
        except MedicineInventory.DoesNotExist:
            # Handle if medicine inventory does not exist
            pass    
 
    
    
@receiver(post_save, sender=ImagingRecord)
def create_imaging_order(sender, instance, created, **kwargs):
    if created:
        Order.objects.create(
            order_date=instance.order_date,
            order_type=instance.imaging.name,
            patient=instance.patient,
            doctor=instance.doctor,
            visit=instance.visit,
            added_by=instance.data_recorder,
            cost=instance.cost,
            type_of_order="Imaging",
        )

@receiver(post_save, sender=ConsultationOrder)
def create_consultation_order(sender, instance, created, **kwargs):
    if created:
        Order.objects.create(
            order_date=instance.order_date,
            order_type=instance.consultation.name,
            patient=instance.patient,
            doctor=instance.doctor,
            visit=instance.visit,
            added_by=instance.data_recorder,
            cost=instance.cost,
            type_of_order="Consultation",
        )

@receiver(post_save, sender=Procedure)
def create_procedure_order(sender, instance, created, **kwargs):
    if created:
        Order.objects.create(
            order_date=instance.order_date,
            order_type=instance.name.name,
            patient=instance.patient,
            doctor=instance.doctor,
            visit=instance.visit,
            added_by=instance.data_recorder,
            cost=instance.cost,
            type_of_order="Procedure",
        )

@receiver(post_save, sender=LaboratoryOrder)
def create_laboratory_order(sender, instance, created, **kwargs):
    if created:
        Order.objects.create(
            order_date=instance.order_date,
            order_type=instance.name.name,
            patient=instance.patient,
            doctor=instance.doctor,
             visit=instance.visit,
            added_by=instance.data_recorder,
            cost=instance.cost,
            type_of_order="Laboratory",
        )

@receiver(post_save, sender=AmbulanceOrder)
def create_ambulance_order(sender, instance, created, **kwargs):
    if created:
        Order.objects.create(
            order_date=instance.order_date,
            order_type='Ambulance',
            patient=instance.patient,
            visit=instance.visit,
            added_by=instance.data_recorder,
            cost=instance.cost,
            type_of_order="Ambulance",
        )
    
    
@receiver(post_save, sender=SalaryPayment)
def calculate_employee_deductions(sender, instance, created, **kwargs):
    """
    Calculate employee deductions for each deduction organization after a salary payment is created or updated.
    """
    salary_payment = instance
    employee = salary_payment.employee
    payroll = salary_payment.payroll

    # Check if the salary payment is being created or updated
    if created or salary_payment.payment_status == 'pending':
        original_salary = employee.salary  # Store the original salary
        original_salary_deducting = employee.salary  # Store the original salary

        # Iterate over all deduction status fields in the Employee model
        deduction_fields = ['tra_deduction_status', 'nssf_deduction_status', 'wcf_deduction_status', 'heslb_deduction_status']
        for field in deduction_fields:
            deduction_status = getattr(employee, field)
                
            # If deduction status is True, calculate deduction amount and update salary
            if deduction_status:
                organization_name = field.split('_')[0].upper()  # Extract organization name from field name
                deduction_rate = get_deduction_rate(organization_name)  # Function to get deduction rate based on organization

                # Fetch the DeductionOrganization instance
                organization_instance = DeductionOrganization.objects.get(name=organization_name)
                    
                deducted_amount = employee.salary * (deduction_rate / 100)  # Calculate deducted amount
                print(deducted_amount)
                original_salary_deducting -= deducted_amount  # Deduct the amount from the salary

                # Create EmployeeDeduction object
                EmployeeDeduction.objects.create(
                    employee=employee,
                    payroll=payroll,
                    organization=organization_instance,  # Assign the DeductionOrganization instance
                    deducted_amount=deducted_amount
                )

        # Save the updated salary
        employee.save()

        # Create a record for the new salary if it has changed
        if original_salary != original_salary_deducting:
            SalaryChangeRecord.objects.create(
                employee=employee,
                payroll=payroll,
                previous_salary=original_salary,
                new_salary=original_salary_deducting
            )

def get_deduction_rate(organization_name):
    try:
        deduction_org = DeductionOrganization.objects.get(name=organization_name)
        return deduction_org.rate
    except DeductionOrganization.DoesNotExist:
        return 0.0  # Default to 0 if organization is not recognized