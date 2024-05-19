from django.contrib import admin
from django.forms import TextInput, Textarea
from clinic.models import AdminHOD, AmbulanceActivity, BankAccount, Category, Client, Company, CustomUser, DeductionOrganization, DiseaseRecode, Employee, EmployeeDeduction, Equipment, EquipmentMaintenance, Expense, ExpenseCategory, HospitalVehicle, InsuranceCompany, Invoice, MedicineUnitMeasure, PathodologyRecord, Payment, PaymentMethod, Payroll, Reagent, ReagentUsage, SalaryChangeRecord, SalaryPayment, Service, Staffs, Supplier
from django.db import models
from django.contrib.auth.admin import UserAdmin
# Register your models here.
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee_id', 'department', 'employment_type', 'start_date', 'end_date', 'salary')
    search_fields = ['name__name', 'employee_id', 'department']
    list_filter = ('department', 'employment_type', 'start_date', 'end_date')
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name',  'department', 'employment_type', 'start_date', 'end_date')
        }),
        ('Salary and Bank Details', {
            'fields': ('salary', 'bank_account', 'bank_account_number', 'account_holder_name')
        }),
        ('Organization-specific Identification Numbers', {
            'fields': ('tin_number', 'nssf_membership_number', 'nhif_number', 'wcf_number')
        }),
        ('Deduction Status', {
            'fields': ('tra_deduction_status', 'nssf_deduction_status', 'wcf_deduction_status', 'heslb_deduction_status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally, collapse this fieldset by default
        }),
    )

admin.site.register(Employee, EmployeeAdmin)


class DeductionOrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate', 'created_at', 'updated_at')
    search_fields = ['name']
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        ('Organization Information', {
            'fields': ('name', 'rate', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally, collapse this fieldset
        }),
    )

admin.site.register(DeductionOrganization, DeductionOrganizationAdmin)


class EmployeeDeductionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'payroll', 'organization', 'deducted_amount', 'created_at', 'updated_at')
    search_fields = ['employee__name', 'payroll__payroll_date', 'organization__name']
    list_filter = ('created_at', 'updated_at', 'organization')
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        ('Deduction Information', {
            'fields': ('employee', 'payroll', 'organization', 'deducted_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally, collapse this fieldset
        }),
    )

    def has_add_permission(self, request):
        return False  # Disable adding permission

    def has_change_permission(self, request, obj=None):
        return False  # Disable editing permission


admin.site.register(EmployeeDeduction, EmployeeDeductionAdmin)

class SalaryChangeRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'payroll', 'previous_salary', 'new_salary', 'change_date', 'created_at', 'updated_at')
    search_fields = ['employee__name', 'payroll__payroll_date']
    list_filter = ('change_date', 'created_at', 'updated_at')
    readonly_fields = ('change_date', 'created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        ('Salary Change Information', {
            'fields': ('employee', 'payroll', 'previous_salary', 'new_salary', 'change_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally, collapse this fieldset
        }),
    )
    def has_add_permission(self, request):
        return False  # Disable adding permission

    def has_change_permission(self, request, obj=None):
        return False  # Disable editing permission
admin.site.register(SalaryChangeRecord, SalaryChangeRecordAdmin)

class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ['name']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        ('Payment Method Information', {
            'fields': ('name', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally, collapse this fieldset
        }),
    )

admin.site.register(PaymentMethod, PaymentMethodAdmin)

class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ['name']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        ('Expense Category Information', {
            'fields': ('name', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally, collapse this fieldset
        }),
    )

admin.site.register(ExpenseCategory, ExpenseCategoryAdmin)

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'description', 'category', 'created_at', 'updated_at')
    search_fields = ['date', 'amount', 'description', 'category__name']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        ('Expense Information', {
            'fields': (('date', 'amount'), 'description', 'category',  'receipt')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally, collapse this fieldset
        }),
    )

admin.site.register(Expense, ExpenseAdmin)

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'due_date', 'amount', 'status', 'client', 'created_at', 'updated_at')
    search_fields = ['number', 'date', 'due_date', 'amount', 'status', 'client__name']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        ('Invoice Information', {
            'fields': (('number', 'status'), ('date', 'due_date'), 'amount', 'client')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally, collapse this fieldset
        }),
    )

admin.site.register(Invoice, InvoiceAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('date', 'amount', 'method', 'invoice', 'created_at', 'updated_at')
    search_fields = ['date', 'amount', 'description']
    list_filter = ('date', 'method', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        ('Payment Information', {
            'fields': (('date', 'amount'), 'method', 'invoice', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally, collapse this fieldset
        }),
    )

admin.site.register(Payment, PaymentAdmin)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'address', 'contact_person', 'created_at', 'updated_at')
    search_fields = ['name', 'email', 'phone_number', 'contact_person']
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        ('Client Information', {
            'fields': ('name', 'email', 'phone_number', 'address', 'contact_person')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally, collapse this fieldset
        }),
    )

admin.site.register(Client, ClientAdmin)


class PayrollAdmin(admin.ModelAdmin):
    list_display = ('payroll_date', 'total_salary', 'status', 'payment_method', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        ('Payroll Information', {
            'fields': ('payroll_date', 'total_salary', 'status', 'payment_method', 'details')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally, collapse this fieldset
        }),
    )

admin.site.register(Payroll, PayrollAdmin)

class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        ('Bank Account Information', {
            'fields': ('bank_name',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally, collapse this fieldset
        }),
    )

admin.site.register(BankAccount, BankAccountAdmin)


class SalaryPaymentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'payroll','payment_date', 'payment_status')
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        ('Payment Information', {
            'fields': ('employee', 'payroll',  'payment_date', 'payment_status', 'payment_details')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally, collapse this fieldset
        }),
    )

admin.site.register(SalaryPayment, SalaryPaymentAdmin)

class StaffsAdmin(admin.ModelAdmin):
    list_display = ['get_first_name', 'get_last_name', 'get_email', 'get_username', 'get_is_active', 'middle_name', 'gender', 'date_of_birth', 'phone_number', 'marital_status', 'profession', 'role', 'work_place', 'created_at', 'updated_at']
    search_fields = ['admin__first_name', 'admin__last_name', 'middle_name', 'phone_number']
    list_filter = ['gender', 'marital_status', 'profession', 'role']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only
    fieldsets = (
        (None, {
            'fields': (('admin', 'middle_name'), ('gender', 'date_of_birth'), 'phone_number')
        }),
        ('Additional Information', {
            'fields': ('marital_status', 'profession', 'role', 'work_place'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (('created_at', 'updated_at'),),
            'classes': ('collapse',)
        })
    )
    def get_first_name(self, obj):
        return obj.admin.first_name if obj.admin else None
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.admin.last_name if obj.admin else None
    get_last_name.short_description = 'Last Name'

    def get_email(self, obj):
        return obj.admin.email if obj.admin else None
    get_email.short_description = 'Email'
    
    def get_is_active(self, obj):
        return obj.admin.is_active if obj.admin else None
    get_is_active.short_description = 'is_active'

    def get_username(self, obj):
        return obj.admin.username if obj.admin else None
    get_username.short_description = 'Username'
    # Customize form layout
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '50'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 50})},
    }
    # Optionally, prepopulate the admin field with the user's first name and last name
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'admin':
            kwargs['initial'] = request.user.id
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Staffs, StaffsAdmin)

class InsuranceCompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'short_name', 'email', 'address', 'website', 'created_at', 'updated_at']
    search_fields = ['name', 'phone', 'short_name', 'email', 'address']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only
    fieldsets = (
        (None, {
            'fields': ('name', 'phone', 'short_name', 'email', 'address', 'website')
        }),
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally collapse this section
        })
    )

admin.site.register(InsuranceCompany, InsuranceCompanyAdmin)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'coverage', 'department', 'type_service', 'cash_cost', 'insurance_cost', 'nhif_cost', 'created_at', 'updated_at']
    search_fields = ['name', 'coverage', 'department', 'type_service', 'description']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only
    fieldsets = (
        (None, {
            'fields': ('name', 'coverage', 'department', 'type_service', 'description')
        }),
        ('Cost Information', {
            'fields': ('cash_cost', 'insurance_cost', 'nhif_cost'),
            'classes': ('collapse',)  # Optionally collapse this section
        }),
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally collapse this section
        })
    )

admin.site.register(Service, ServiceAdmin)

class MedicineUnitMeasureAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'application_user', 'created_at', 'updated_at']
    search_fields = ['name', 'short_name', 'application_user']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only
    fieldsets = (
        (None, {
            'fields': ('name', 'short_name', 'application_user')
        }),
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally collapse this section
        })
    )

admin.site.register(MedicineUnitMeasure, MedicineUnitMeasureAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally collapse this section
        })
    )

admin.site.register(Category, CategoryAdmin)

class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'contact_information', 'email', 'created_at', 'updated_at']
    search_fields = ['name', 'address', 'contact_information', 'email']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        (None, {
            'fields': ('name', 'address', 'contact_information', 'email')
        }),
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally collapse this section
        })
    )

admin.site.register(Supplier, SupplierAdmin)

class PathodologyRecordAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally collapse this section
        })
    )

admin.site.register(PathodologyRecord, PathodologyRecordAdmin)

class DiseaseRecodeAdmin(admin.ModelAdmin):
    list_display = ['disease_name', 'code', 'created_at', 'updated_at']
    search_fields = ['disease_name', 'code']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        (None, {
            'fields': ('disease_name', 'code')
        }),
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally collapse this section
        })
    )

admin.site.register(DiseaseRecode, DiseaseRecodeAdmin)

class HospitalVehicleAdmin(admin.ModelAdmin):
    list_display = ['number', 'plate_number', 'is_active', 'vehicle_type', 'created_at', 'updated_at']
    search_fields = ['number', 'plate_number', 'vehicle_type']
    list_filter = ['is_active', 'created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        (None, {
            'fields': ('number', 'plate_number', 'is_active', 'vehicle_type')
        }),
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally collapse this section
        })
    )

admin.site.register(HospitalVehicle, HospitalVehicleAdmin)

class AmbulanceActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost', 'profit', 'total', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ('total', 'created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        (None, {
            'fields': ('name', 'cost', 'profit', 'total')
        }),
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Optionally collapse this section
        })
    )

admin.site.register(AmbulanceActivity, AmbulanceActivityAdmin)

class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'manufacturer', 'serial_number', 'acquisition_date', 'warranty_expiry_date', 'is_active', 'created_at', 'updated_at']
    search_fields = ['name', 'manufacturer', 'serial_number', 'location']
    list_filter = ['is_active', 'acquisition_date', 'warranty_expiry_date', 'created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'manufacturer', 'serial_number', 'location', 'is_active')
        }),
        ('Dates', {
            'fields': ('acquisition_date', 'warranty_expiry_date'),
            'classes': ('collapse',)
        }),
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

admin.site.register(Equipment, EquipmentAdmin)

class EquipmentMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'maintenance_date', 'technician', 'cost', 'created_at', 'updated_at']
    search_fields = ['equipment__name', 'technician']
    list_filter = ['maintenance_date', 'created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        (None, {
            'fields': ('equipment', 'maintenance_date', 'technician', 'description', 'cost', 'notes')
        }),
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

admin.site.register(EquipmentMaintenance, EquipmentMaintenanceAdmin)

class ReagentAdmin(admin.ModelAdmin):
    list_display = ['name', 'expiration_date', 'manufacturer', 'lot_number', 'quantity_in_stock', 'price_per_unit', 'remaining_quantity', 'created_at', 'updated_at']
    search_fields = ['name', 'manufacturer', 'lot_number']
    list_filter = ['expiration_date', 'manufacturer', 'created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        (None, {
            'fields': ('name', 'expiration_date', 'manufacturer', 'lot_number', 'storage_conditions', 'quantity_in_stock', 'price_per_unit', 'remaining_quantity')
        }),
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

admin.site.register(Reagent, ReagentAdmin)

class ReagentUsageAdmin(admin.ModelAdmin):
    list_display = ['lab_technician', 'reagent', 'usage_date', 'quantity_used', 'observation', 'technician_notes', 'created_at', 'updated_at']
    search_fields = ['lab_technician__admin__first_name', 'lab_technician__admin__last_name', 'reagent__name', 'usage_date']
    list_filter = ['usage_date', 'created_at', 'updated_at']
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only

    fieldsets = (
        (None, {
            'fields': ('lab_technician', 'reagent', 'usage_date', 'quantity_used', 'observation', 'technician_notes')
        }),
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

admin.site.register(ReagentUsage, ReagentUsageAdmin)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'registration_number', 'city', 'state', 'country', 'phone_number', 'email', 'website', 'date_registered']
    search_fields = ['name', 'registration_number', 'city', 'state', 'country', 'phone_number', 'email', 'website']
    list_filter = ['country', 'date_registered']
    readonly_fields = ('date_registered',)  # Optionally, make certain fields read-only

    fieldsets = (
        (None, {
            'fields': ('name', 'registration_number', 'address', 'city', 'state', 'country', 'postal_code', 'phone_number', 'email', 'website', 'logo')
        }),
        ('Date Information', {
            'fields': ('date_registered',),
            'classes': ('collapse',)
        })
    )

admin.site.register(Company, CompanyAdmin)

class AdminHODAdmin(admin.ModelAdmin):
    list_display = ('get_first_name', 'get_last_name', 'get_email', 'get_username', 'get_is_active')
    readonly_fields = ('created_at', 'updated_at')  # Optionally, make certain fields read-only
    fieldsets = (
        (None, {
            'fields': ('admin',)
        }),
        ('Date Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # optional to collapse this section by default
        }),
    )
    def get_first_name(self, obj):
        return obj.admin.first_name if obj.admin else None
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.admin.last_name if obj.admin else None
    get_last_name.short_description = 'Last Name'

    def get_email(self, obj):
        return obj.admin.email if obj.admin else None
    get_email.short_description = 'Email'
    
    def get_is_active(self, obj):
        return obj.admin.is_active if obj.admin else None
    get_is_active.short_description = 'is_active'

    def get_username(self, obj):
        return obj.admin.username if obj.admin else None
    get_username.short_description = 'Username'

admin.site.register(AdminHOD, AdminHODAdmin)

