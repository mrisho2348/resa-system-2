# clinic/signals.py

from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from .models import AmbulanceOrder,   ConsultationOrder, DeductionOrganization, EmployeeDeduction, ImagingRecord, LaboratoryOrder, Order, Procedure, Reagent, SalaryChangeRecord, SalaryPayment
from django.db.models import F
from django.db import models




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
            order_type=instance.lab_test.name,
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