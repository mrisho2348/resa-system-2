from multiprocessing.connection import Client
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import BankAccount, Clients, Company, DeductionOrganization, Employee, EmployeeDeduction, Expense, ExpenseCategory, GovernmentProgram, Grant, Investment, Invoice, Payment, PaymentMethod, Payroll, SalaryChangeRecord, SalaryPayment
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BankAccountForm, ClientForm, DeductionOrganizationForm, EmployeeForm, ExpenseCategoryForm, ExpenseForm, GovernmentProgramForm, GrantForm, InvestmentForm, PaymentForm, PaymentMethodForm, PayrollForm, SalaryPaymentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

def bank_account_list(request):
    bank_accounts = BankAccount.objects.all()
    return render(request, 'hod_template/manage_bank_account_list.html', {'bank_accounts': bank_accounts})

def add_bank_account(request, bank_account_id=None):
    if bank_account_id:
        # If bank_account_id is provided, fetch the instance for editing
        bank_account_instance = get_object_or_404(BankAccount, pk=bank_account_id)
    else:
        bank_account_instance = None

    if request.method == 'POST':
        form = BankAccountForm(request.POST, instance=bank_account_instance)
        try:
            if form.is_valid():
                bank_account = form.save()
                messages.success(request, 'Bank account saved successfully!')

                if 'save_and_add_another' in request.POST:
                    return redirect('add_bank_account')
                else:
                    return redirect('bank_account_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    else:
        form = BankAccountForm(instance=bank_account_instance)

    context = {'form': form}
    return render(request, 'hod_template/add_bank_account.html', context)

def delete_bank_account(request, account_id):
    bank_account = get_object_or_404(BankAccount, id=account_id)
    if request.method == 'POST':
        try:
            bank_account.delete()
            messages.success(request, 'Bank account deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting bank account: {str(e)}')
        return redirect('bank_account_list')  # Redirect to the list of bank accounts
    else:
        # If the request method is not POST, render a confirmation page
        return render(request, 'delete_bank_confirmation.html', {'bank_account': bank_account})


def payroll_list(request):
    payrolls = Payroll.objects.all()
    return render(request, 'hod_template/manage_payroll_list.html', {'payrolls': payrolls})

def add_payroll(request, payroll_id=None):
    # If payroll_id is provided, fetch the instance for editing
    if payroll_id:
        payroll_instance = get_object_or_404(Payroll, pk=payroll_id)
    else:
        payroll_instance = None

    if request.method == 'POST':
        form = PayrollForm(request.POST, instance=payroll_instance)
        try:
            if form.is_valid():
                payroll = form.save()
                messages.success(request, 'Payroll saved successfully!')

                if 'save_and_add_another' in request.POST:
                    return redirect('add_payroll')
                else:
                    return redirect('payroll_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    else:
        form = PayrollForm(instance=payroll_instance)
    
    context = {'form': form}
    return render(request, 'hod_template/add_payroll.html', context)

def delete_payroll(request, payroll_id):
    # Retrieve the payroll instance
    payroll = get_object_or_404(Payroll, pk=payroll_id)

    if request.method == 'POST':
        try:
            # Delete the payroll instance
            payroll.delete()
            messages.success(request, 'Payroll deleted successfully!')
            return redirect('payroll_list')
        except Exception as e:
            messages.error(request, f'Error deleting payroll: {str(e)}')

    return render(request, 'hod_template/delete_payroll.html', {'payroll': payroll})

def payment_method_list(request):
    payment_methods = PaymentMethod.objects.all()
    return render(request, 'hod_template/manage_payment_method_list.html', {'payment_methods': payment_methods})

def add_payment_method(request, payment_method_id=None):
    if payment_method_id:
        # If payment_method_id is provided, fetch the instance for editing
        payment_method_instance = get_object_or_404(PaymentMethod, pk=payment_method_id)
    else:
        payment_method_instance = None

    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=payment_method_instance)
        try:
            if form.is_valid():
                payment_method = form.save()
                messages.success(request, 'Payment method saved successfully!')

                if 'save_and_add_another' in request.POST:
                    return redirect('add_payment_method')
                else:
                    return redirect('payment_method_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    else:
        form = PaymentMethodForm(instance=payment_method_instance)

    context = {'form': form}
    return render(request, 'hod_template/add_payment_method.html', context)

def delete_payment_method(request, payment_method_id):
    payment_method = get_object_or_404(PaymentMethod, pk=payment_method_id)
    if request.method == 'POST':
        try:
            payment_method.delete()
            messages.success(request, 'Payment method deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    return redirect('payment_method_list') 

def expense_category_list(request):
    expense_categories = ExpenseCategory.objects.all()
    return render(request, 'hod_template/manage_expense_category_list.html', {'expense_categories': expense_categories})

def add_expense_category(request, expense_category_id=None):
    if expense_category_id:
        # If an expense category ID is provided, fetch the instance for editing
        expense_category_instance = get_object_or_404(ExpenseCategory, pk=expense_category_id)
    else:
        expense_category_instance = None

    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST, instance=expense_category_instance)
        try:
            if form.is_valid():
                form.save()
                messages.success(request, 'Expense category saved successfully!')

                if 'save_and_add_another' in request.POST:
                    return redirect('add_expense_category')
                else:
                    return redirect('expense_category_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    else:
        form = ExpenseCategoryForm(instance=expense_category_instance)

    context = {'form': form}
    return render(request, 'hod_template/add_expense_category.html', context)


def delete_expense_category(request, expense_category_id):
    expense_category = get_object_or_404(ExpenseCategory, pk=expense_category_id)
    if request.method == 'POST':
        try:
            expense_category.delete()
            messages.success(request, 'Expense category deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

        return redirect('expense_category_list')

    return redirect('expense_category_list')

def expense_list(request):
    expenses = Expense.objects.all()
    return render(request, 'hod_template/manage_expense_list.html', {'expenses': expenses})

def add_expense(request, expense_id=None):
    if expense_id:
        expense = get_object_or_404(Expense, id=expense_id)
        action_message = 'updated'
    else:
        expense = None
        action_message = 'added'
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        try:
            if form.is_valid():
                form.save()
                messages.success(request, f'Expense {action_message} successfully!')

                if 'save_and_add_another' in request.POST:
                    return redirect('add_expense')  # Adjust this if you want to handle "save and add another" differently
                else:
                    return redirect('expense_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    else:
        form = ExpenseForm(instance=expense)

    context = {'form': form}
    return render(request, 'hod_template/add_expense.html', context)


def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    try:
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('expense_list')

def deduction_organization_list(request):
    deduction_organizations = DeductionOrganization.objects.all()
    return render(request, 'hod_template/manage_deduction_organization_list.html', {'deduction_organizations': deduction_organizations})

def add_deduction_organization(request, deduction_organization_id=None):
    if deduction_organization_id:
        # If deduction_organization_id is provided, fetch the instance for editing
        deduction_organization_instance = get_object_or_404(DeductionOrganization, pk=deduction_organization_id)
    else:
        deduction_organization_instance = None

    if request.method == 'POST':
        form = DeductionOrganizationForm(request.POST, instance=deduction_organization_instance)
        try:
            if form.is_valid():
                deduction_organization = form.save()
                messages.success(request, 'Deduction organization saved successfully!')

                if 'save_and_add_another' in request.POST:
                    return redirect('add_deduction_organization')
                else:
                    return redirect('deduction_organization_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    else:
        form = DeductionOrganizationForm(instance=deduction_organization_instance)

    context = {'form': form}
    return render(request, 'hod_template/add_deduction_organization.html', context)

def delete_deduction_organization(request, deduction_organization_id):
    deduction_organization = get_object_or_404(DeductionOrganization, pk=deduction_organization_id)
    if request.method == 'POST':
        try:
            deduction_organization.delete()
            messages.success(request, 'Deduction organization deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    # Redirect to the list view of deduction organizations
    return redirect('deduction_organization_list')

def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'hod_template/manage_employee_list.html', {'employees': employees})

def add_employee(request, employee_id=None):
    if employee_id:
        employee = get_object_or_404(Employee, id=employee_id)
        action_message = 'updated'
    else:
        employee = None
        action_message = 'added'
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        try:
            if form.is_valid():
                form.save()
                messages.success(request, f'Employee {action_message} successfully!')

                if 'save_and_add_another' in request.POST:
                    return redirect('add_employee')
                else:
                    return redirect('employee_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    else:
        form = EmployeeForm(instance=employee)

    context = {'form': form}
    return render(request, 'hod_template/add_employee.html', context)


def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    try:
        employee.delete()
        messages.success(request, 'employee deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('employee_list')



def salary_payment_list(request):
    salary_payments = SalaryPayment.objects.all()
    return render(request, 'hod_template/manage_salary_payment_list.html', {'salary_payments': salary_payments})

def add_salary_payment(request, payment_id=None):
    if payment_id:
        payment = get_object_or_404(SalaryPayment, id=payment_id)
        action_message = 'updated'
    else:
        payment = None
        action_message = 'added'

    if request.method == 'POST':
        form = SalaryPaymentForm(request.POST, instance=payment)
        try:
            if form.is_valid():
                form.save()
                messages.success(request, f'Salary payment {action_message} successfully!')

                if 'save_and_add_another' in request.POST:
                    return redirect('add_salary_payment')
                else:
                    return redirect('salary_payment_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    else:
        form = SalaryPaymentForm(instance=payment)

    context = {'form': form}
    return render(request, 'hod_template/add_salary_payment.html', context)

def delete_salary_payment(request, payment_id):
    payment = get_object_or_404(SalaryPayment, id=payment_id)
    try:
        payment.delete()
        messages.success(request, 'Salary payment deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('salary_payment_list')

def employee_deduction_list(request):
    employee_deductions = EmployeeDeduction.objects.all()
    return render(request, 'hod_template/manage_employee_deduction_list.html', {'employee_deductions': employee_deductions})

def delete_employee_deduction(request, deduction_id):
    deduction  = get_object_or_404(EmployeeDeduction, id=deduction_id)
    try:
        deduction.delete()
        messages.success(request, 'Employee deduction deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('employee_deduction_list')

def salary_change_record_list(request):
    salary_change_records = SalaryChangeRecord.objects.all()
    return render(request, 'hod_template/manage_salary_change_record_list.html', {'salary_change_records': salary_change_records})

def delete_salary_change_record(request, record_id):
    record   = get_object_or_404(SalaryChangeRecord, id=record_id)
    try:
        record .delete()
        messages.success(request, 'Salary change record deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('salary_change_record_list')

def payment_list(request):
    payments = Payment.objects.all()
    return render(request, 'hod_template/manage_payment_list.html', {'payments': payments})

def add_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        try:
            if form.is_valid():
                payment = form.save()
                messages.success(request, 'Payment added successfully!')
                
                if 'save_and_add_another' in request.POST:
                    return redirect('add_payment')
                else:
                    return redirect('payment_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    else:
        form = PaymentForm()
    
    context = {'form': form}
    return render(request, 'hod_template/add_payment.html', context)

def client_list(request):
    clients = Clients.objects.all()
    return render(request, 'hod_template/manage_client_list.html', {'clients': clients})

def add_client(request, client_id=None):
    # Check if client_id is provided in the URL
    if client_id:
        client = get_object_or_404(Clients, id=client_id)
        # If client_id is provided, it's an edit request, so get the instance of the client
        form = ClientForm(request.POST or None, instance=client)
    else:
        form = ClientForm(request.POST or None)

    if request.method == 'POST':
        try:
            if form.is_valid():
                form.save()
                if client_id:
                    messages.success(request, 'Client updated successfully!')
                else:
                    messages.success(request, 'Client added successfully!')
                
                if 'save_and_add_another' in request.POST:
                    return redirect('add_client')
                else:
                    return redirect('client_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    context = {'form': form}
    return render(request, 'hod_template/add_client.html', context)

def delete_client(request, client_id):
    record   = get_object_or_404(Clients, id=client_id)
    try:
        record .delete()
        messages.success(request, 'Client deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('client_list')

def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, 'hod_template/manage_invoice_list.html', {'invoices': invoices})


def investment_list(request):
    investments = Investment.objects.all()
    return render(request, 'hod_template/manage_investment_list.html', {'investments': investments})

def grant_list(request):
    grants = Grant.objects.all()
    return render(request, 'hod_template/manage_grant_list.html', {'grants': grants})

def government_program_list(request):
    government_programs = GovernmentProgram.objects.all()
    return render(request, 'hod_template/manage_government_program_list.html', {'government_programs': government_programs})

def add_investment(request, pk=None):
    if pk:
        investment = get_object_or_404(Investment, pk=pk)
    else:
        investment = None

    if request.method == 'POST':
        form = InvestmentForm(request.POST, instance=investment)
        try:
            if form.is_valid():
                form.save()
                if investment:
                    messages.success(request, 'Investment updated successfully!')
                else:
                    messages.success(request, 'Investment added successfully!')
                if 'save_and_add_another' in request.POST:
                    return redirect('add_investment')
                else:
                    return redirect('investment_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    else:
        form = InvestmentForm(instance=investment)
    
    return render(request, 'hod_template/add_investment.html', {'form': form, 'investment': investment})


def add_grant(request, pk=None):
    if pk:
        grant = get_object_or_404(Grant, pk=pk)
    else:
        grant = None

    if request.method == 'POST':
        form = GrantForm(request.POST, instance=grant)
        try:
            if form.is_valid():
                form.save()
                if grant:
                    messages.success(request, 'Grant updated successfully!')
                else:
                    messages.success(request, 'Grant added successfully!')
                if 'save_and_add_another' in request.POST:
                    return redirect('add_grant')
                else:
                    return redirect('grant_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    else:
        form = GrantForm(instance=grant)
    
    return render(request, 'hod_template/add_grant.html', {'form': form, 'grant': grant})


def add_government_program(request, pk=None):
    if pk:
        program = get_object_or_404(GovernmentProgram, pk=pk)
    else:
        program = None

    if request.method == 'POST':
        form = GovernmentProgramForm(request.POST, instance=program)
        try:
            if form.is_valid():
                form.save()
                if program:
                    messages.success(request, 'Government Program updated successfully!')
                else:
                    messages.success(request, 'Government Program added successfully!')
                if 'save_and_add_another' in request.POST:
                    return redirect('add_government_program')
                else:
                    return redirect('government_program_list')
            else:
                messages.error(request, 'Please correct the errors below.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    else:
        form = GovernmentProgramForm(instance=program)
    
    return render(request, 'hod_template/add_government_program.html', {'form': form, 'program': program})


def delete_grant(request, pk):
    grant = get_object_or_404(Grant, pk=pk)
    grant.delete()
    messages.success(request, 'Grant deleted successfully!')
    return redirect('grant_list')

def delete_government_program(request, pk):
    program = get_object_or_404(GovernmentProgram, pk=pk)
    program.delete()
    messages.success(request, 'Government Program deleted successfully!')
    return redirect('government_program_list')

def delete_investment(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    investment.delete()
    messages.success(request, 'Investment deleted successfully!')
    return redirect('investment_list')


@csrf_exempt
@login_required
def add_company(request):
    if request.method == 'POST':
        try:
            # Get data from the request
            company_id = request.POST.get('company_id')
            name = request.POST.get('Name').strip()
            industry = request.POST.get('industry', '')
            sector = request.POST.get('sector', '')
            headquarters = request.POST.get('headquarters', '')
            Founded = request.POST.get('Founded', '')
            Notes = request.POST.get('Notes', '')

            # Check if company_id is provided
            if company_id:
                # Fetch the existing company object
                company = Company.objects.get(pk=company_id)

                # Check if the new name already exists and it's not the same as the current name
                if Company.objects.filter(name=name).exclude(pk=company_id).exists():
                    return JsonResponse({'success': False, 'message': 'Company with the provided name already exists'})

                # Update company data
                company.name = name
                company.industry = industry
                company.sector = sector
                company.headquarters = headquarters
                company.Founded = Founded
                company.Notes = Notes
                company.save()

                return JsonResponse({'success': True, 'message': 'Company updated successfully'})
            else:
                # Check if a company with the given name already exists
                if Company.objects.filter(name=name).exists():
                    return JsonResponse({'success': False, 'message': 'Company already exists'})

                # Save new company data
                Company.objects.create(
                    name=name,
                    industry=industry,
                    sector=sector,
                    headquarters=headquarters,
                    Founded=Founded,
                    Notes=Notes,
                )

                return JsonResponse({'success': True, 'message': 'Company added successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    
@csrf_exempt
def delete_remotecompany(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        try:
            company = get_object_or_404(Company, id=company_id)
            company.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})    