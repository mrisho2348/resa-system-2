# views.py
import logging
from django.shortcuts import redirect, render
from django.contrib import messages
from django.db import IntegrityError
from clinic.models import Category, HealthRecord, ConsultationNotes, Country, Diagnosis, DiseaseRecode, Equipment, EquipmentMaintenance, HealthIssue, InsuranceCompany, InventoryItem, Medicine, PathodologyRecord, PatientVital, Patients, Prescription, Procedure, Reagent, Referral, RemoteCompany, RemoteMedicine, RemotePatient, RemoteService,Service, Staffs, Supplier
from clinic.resources import CategoryResource, CompanyResource, ConsultationNotesResource, CountryResource, DiagnosisResource, DiseaseRecodeResource, EquipmentMaintenanceResource, EquipmentResource, HealthIssueResource, HealthRecordResource, InsuranceCompanyResource, InventoryItemResource, MedicineResource, PathologyRecordResource, PatientVitalResource, PatientsResource, PrescriptionResource, ProcedureResource, ReagentResource, ReferralResource, RemoteMedicineResource, RemotePatientResource, RemoteServiceResource, ServiceResource, SupplierResource
from clinic.forms import ImportCategoryForm, ImportCompanyForm, ImportConsultationNotesForm, ImportCountryForm, ImportDiagnosisForm, ImportDiseaseForm, ImportEquipmentForm, ImportEquipmentMaintenanceForm, ImportHealthIssueForm, ImportHealthRecordForm, ImportInsuranceCompanyForm, ImportInventoryItemForm, ImportMedicineForm, ImportPathologyRecordForm, ImportPatientVitalForm, ImportPatientsForm, ImportPrescriptionForm, ImportProcedureForm, ImportReagentForm, ImportReferralForm, ImportRemoteMedicineForm, ImportRemotePatientForm, ImportRemoteServiceForm, ImportServiceForm, ImportSupplierForm
from tablib import Dataset
from django.contrib.auth.decorators import login_required
logger = logging.getLogger(__name__)

@login_required
def import_disease_recode(request):
    if request.method == 'POST':
        form = ImportDiseaseForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                disease_recode_resource = DiseaseRecodeResource()
                new_disease_recodes = request.FILES['disease_recode_file']
                
                # Use tablib to load the imported data
                dataset = Dataset()
                imported_data = dataset.load(new_disease_recodes.read(), format='xlsx')  # Adjust format accordingly

                for data in imported_data:
                    disease_recode = DiseaseRecode(
                        disease_name=data[0],
                        code=data[1],
                        # Add other fields accordingly
                    )
                    disease_recode.save()

                return redirect('manage_disease') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')
        else:
            messages.error(request, 'Form is not valid. Please check the file and try again.')
    else:
        form = ImportDiseaseForm()

    return render(request, 'kahama_template/import_disease_recode.html', {'form': form})

@login_required
def import_insurance_companies(request):
    if request.method == 'POST':
        form = ImportInsuranceCompanyForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = InsuranceCompanyResource()
                new_companies = request.FILES['insurance_company_file']
                
                # Use tablib to load the imported data
                dataset = Dataset()
                imported_data = dataset.load(new_companies.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     insurance_recode = InsuranceCompany(
                        name=data[0],
                        phone=data[1],
                        short_name=data[2],
                        email=data[3],
                        address=data[4],
                        # Add other fields accordingly
                    )
                     insurance_recode.save()

                return redirect('manage_insurance') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportInsuranceCompanyForm()

    return render(request, 'kahama_template/import_insurance_companies.html', {'form': form})

@login_required
def import_category(request):
    if request.method == 'POST':
        form = ImportCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = CategoryResource()
                new_category = request.FILES['category_records_file']
                
                # Use tablib to load the imported data
                dataset = Dataset()
                imported_data = dataset.load(new_category.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     category_recode = Category(
                        name=data[0],
                      
                    )
                     category_recode.save()

                return redirect('category_list') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportCategoryForm()

    return render(request, 'kahama_template/import_category.html', {'form': form})




@login_required
def import_equipment(request):
    if request.method == 'POST':
        form = ImportEquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = EquipmentResource()
                new_equipment = request.FILES['equipment_records_file']
                
                # Use tablib to load the imported data
                dataset = Dataset()
                imported_data = dataset.load(new_equipment.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     equipment_record = Equipment(
                        name=data[0],
                        description=data[1],
                        manufacturer=data[2],
                        serial_number=data[3],
                        acquisition_date=data[4],
                        warranty_expiry_date=data[5],
                        location=data[6],
                      
                    )
                     equipment_record.save()

                return redirect('equipment_list') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportEquipmentForm()

    return render(request, 'kahama_template/import_equipment.html', {'form': form})

@login_required
def import_maintenance(request):
    if request.method == 'POST':
        form = ImportEquipmentMaintenanceForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = EquipmentMaintenanceResource()
                new_maintenance = request.FILES['maintenance_records_file']
                
                # Use tablib to load the imported data
                dataset = Dataset()
                imported_data = dataset.load(new_maintenance.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     maintenance_record = EquipmentMaintenance(
                        equipment= Equipment.objects.get(id=data[0]),
                        maintenance_date=data[1],
                        technician=data[2],
                        description=data[3],
                        cost=data[4],
                        notes=data[5],
                  
                      
                    )
                     maintenance_record.save()

                return redirect('equipment_maintenance_list') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportEquipmentMaintenanceForm()

    return render(request, 'kahama_template/import_maintenance.html', {'form': form})

@login_required
def import_reagent(request):
    if request.method == 'POST':
        form = ImportReagentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = ReagentResource()
                new_reagent = request.FILES['reagent_records_file']
                
                # Use tablib to load the imported data
                dataset = Dataset()
                imported_data = dataset.load(new_reagent.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     reagent_record = Reagent(
                        name=data[0],
                        expiration_date=data[1],
                        manufacturer=data[2],
                        lot_number=data[3],
                        storage_conditions=data[4],
                        quantity_in_stock=data[5],
                        price_per_unit=data[6],
                        remaining_quantity=data[5],
                       
                  
                      
                    )
                     reagent_record.save()

                return redirect('reagent_list') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportReagentForm()

    return render(request, 'kahama_template/import_reagent.html', {'form': form})

@login_required
def import_health_issue(request):
    if request.method == 'POST':
        form = ImportHealthIssueForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = HealthIssueResource()
                new_health = request.FILES['health_records_file']
                
                # Use tablib to load the imported data
                dataset = Dataset()
                imported_data = dataset.load(new_health.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     health_record = HealthIssue(
                        name=data[0],
                        description=data[1],
                        is_disease=data[2],
                        severity=data[3],
                        treatment_plan=data[4],
                        onset_date=data[5],
                        resolution_date=data[6],
                      
                       
                  
                      
                    )
                     health_record.save()

                return redirect('health_issue_list') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportHealthIssueForm()

    return render(request, 'kahama_template/import_health.html', {'form': form})

@login_required
def import_companies(request):
    if request.method == 'POST':
        form = ImportCompanyForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = CompanyResource()
                new_companies = request.FILES['company_file']
                
                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_companies.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                      company_recode = RemoteCompany(
                        name=data[0],
                        industry=data[1],
                        sector=data[2],
                        headquarters=data[3],
                        Founded=data[4],
                        Notes=data[5],
                      
                        # Add other fields accordingly
                    )
                      company_recode.save()

                return redirect('kahamahmis:manage_company') 
            except Exception as e:
                logger.error(f"Error adding company: {str(e)}")
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportCompanyForm()

    return render(request, 'kahama_template/import_companies.html', {'form': form})


@login_required
def import_pathology_records(request):
    if request.method == 'POST':
        form = ImportPathologyRecordForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = PathologyRecordResource()
                new_records = request.FILES['pathology_records_file']
                
                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     pathodology_recode = PathodologyRecord(
                        name=data[0],
                        description=data[1],                    
                      
                        # Add other fields accordingly
                    )
                     pathodology_recode.save()

                return redirect('kahamahmis:manage_pathodology') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportPathologyRecordForm()

    return render(request, 'kahama_template/import_pathology_records.html', {'form': form})


@login_required
def import_ImportInventoryItemForm_records(request):
    if request.method == 'POST':
        form = ImportInventoryItemForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = InventoryItemResource()
                new_records = request.FILES['InventoryItem_records_file']
                
                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     pathodology_recode = InventoryItem(
                        name=data[0],
                        quantity=data[1],                     
                        category=Category.objects.get(id=data[2]),                    
                        description=data[3],                     
                        supplier=Supplier.objects.get(id=data[4]),                     
                        purchase_date=data[5],                     
                        purchase_price=data[6],                     
                        expiry_date=data[7],                     
                        location_in_storage=data[8],                     
                        min_stock_level=data[9],                     
                        condition=data[10],                     
                        remain_quantity=data[1],                     
                      
                        # Add other fields accordingly
                    )
                     pathodology_recode.save()

                return redirect('kahamahmis:inventory_list') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportInventoryItemForm()

    return render(request, 'kahama_template/import_InventoryItem.html', {'form': form})

@login_required
def import_prescription_records(request):
    if request.method == 'POST':
        form = ImportPrescriptionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = PrescriptionResource()
                new_records = request.FILES['prescription_records_file']
                
                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     prescription_record = Prescription(
                        route=data[2],
                        quantity_used=data[6],                     
                        patient=Patients.objects.get(id=data[0]),                    
                        dose=data[3],                     
                        medicine=Medicine.objects.get(id=data[1]),                     
                        frequency=data[4],                     
                        duration=data[5],                     
                                         
                       )
                     prescription_record.save()

                return redirect('kahamahmis:prescription_list') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportPrescriptionForm()

    return render(request, 'kahama_template/import_prescription.html', {'form': form})

@login_required
def import_patient_vital_records(request):
    if request.method == 'POST':
        form = ImportPatientVitalForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = PatientVitalResource()
                new_records = request.FILES['vital_records_file']
                
                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     patient_vital_record = PatientVital(
                        patient=Patients.objects.get(id=data[0]),
                        respiratory_rate=data[1],                     
                        pulse_rate=data[2],                    
                        blood_pressure=data[3],                     
                        spo2=data[4],                     
                        temperature=data[5],                     
                        gcs=data[6],                     
                        avpu=data[7],                     
                                         
                       )
                     patient_vital_record.save()

                return redirect('kahamahmis:patient_vital_all_list') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportPatientVitalForm()

    return render(request, 'kahama_template/import_patient_vital.html', {'form': form})

@login_required
def import_patient(request):
    if request.method == 'POST':
        form = ImportRemotePatientForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = RemotePatientResource()
                new_records = request.FILES['patient_records_file']
                
                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     patient_record = RemotePatient(
                        first_name=data[0],
                        middle_name=data[1],                     
                        last_name=data[2],                    
                        gender=data[3],                     
                        age=data[4],                     
                        marital_status=data[5],                     
                        nationality=data[6],                     
                        tribe=data[7],                     
                        patient_type=data[8],                     
                        company=data[9],                     
                        occupation=data[10],                     
                        phone=data[11],                     
                        employee_number=data[12],                     
                        date_of_first_employment=data[13],                     
                        longtime_illness=data[14],                     
                        longtime_medication=data[15],                     
                        date_of_osha_certification=data[16],                     
                        insurance=data[18],                     
                        insurance_company=data[19],                     
                        insurance_number=data[20],                     
                        emergency_contact_name=data[21],                     
                        emergency_contact_relation=data[22],                     
                        emergency_contact_phone=data[23],                     
                        emergency_contact_mobile=data[24],                     
                        life_style=data[25],                     
                                         
                       )
                     patient_record.save()

                return redirect('kahamahmis:patient_vital_all_list') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportRemotePatientForm()

    return render(request, 'kahama_template/import_patient.html', {'form': form})

@login_required
def import_remoteservice_records(request):
    if request.method == 'POST':
        form = ImportRemoteServiceForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = RemoteServiceResource()
                new_records = request.FILES['service_records_file']
                
                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     service_record = RemoteService(
                        name=data[0],                                        
                        description=data[1],                    
                        category=data[2],                  
                                                             
                       )
                     service_record.save()

                return redirect('kahamahmis:remoteservice_list') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')
    else:
        form = ImportRemoteServiceForm()
    return render(request, 'kahama_template/import_remoteservice.html', {'form': form})


@login_required
def import_consultation_notes_records(request):
    if request.method == 'POST':
        form = ImportConsultationNotesForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = ConsultationNotesResource()
                new_records = request.FILES['consultation_records_file']
                
                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     consultation_notes_record = ConsultationNotes(
                        doctor=Staffs.objects.get(id=data[0]),
                        patient=Patients.objects.get(id=data[1]),
                        chief_complaints=data[2],                     
                        history_of_presenting_illness=data[3],                    
                        consultation_number=data[4],                     
                        physical_examination=data[5],                     
                        allergy_to_medications=data[6],                     
                        provisional_diagnosis=Diagnosis.objects.get(id=data[7]),                    
                        final_diagnosis=Diagnosis.objects.get(id=data[8]),                    
                        pathology=PathodologyRecord.objects.get(id=data[9]),                     
                        doctor_plan=data[10],                     
                                         
                       )
                     consultation_notes_record.save()

                return redirect('kahamahmis:consultation_notes') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportConsultationNotesForm()

    return render(request, 'kahama_template/import_consultation_notes.html', {'form': form})

@login_required
def import_diagnosis_records(request):
    if request.method == 'POST':
        form = ImportDiagnosisForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = DiagnosisResource()
                new_records = request.FILES['diagnosis_records_file']
                
                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly

                for data in imported_data:
                     diagnosis_record = Diagnosis(
                 
                        diagnosis_name=data[0],                     
                                          
                                         
                       )
                     diagnosis_record.save()

                return redirect('kahamahmis:diagnosis_list') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportDiagnosisForm()

    return render(request, 'kahama_template/import_diagnosis.html', {'form': form})


@login_required
def import_medicine_drug_records(request):
    if request.method == 'POST':
        form = ImportRemoteMedicineForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = RemoteMedicineResource()
                new_records = request.FILES['records_file']

                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly
                
                for data in imported_data:
                    try:
                        drug_record = RemoteMedicine.objects.create(
                            drug_name=data[0],
                            drug_type=data[1],                     
                            formulation_unit=data[2],                     
                            manufacturer=data[3],                    
                            quantity=data[4],                     
                            dividable=data[5],                     
                            batch_number=data[6],                     
                            expiration_date=data[7],                     
                            unit_cost=data[8], 
                            buying_price=data[9],                      
                            remain_quantity=data[4],                      
                        )
                    except IntegrityError:
                        messages.warning(request, f'Duplicate entry found for {data[0]}. Skipping this record.')
                        continue

                return redirect('kahamahmis:remotemedicine_list') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportRemoteMedicineForm()

    return render(request, 'kahama_template/import_medicine_drug_records.html', {'form': form})

@login_required
def import_service_records(request):
    if request.method == 'POST':
        form = ImportServiceForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = ServiceResource()
                new_records = request.FILES['service_records_file']

                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly
                
                for data in imported_data:
                    try:
                        service_record = Service.objects.create(
                            department=data[1],
                            type_service=data[0],                     
                            name=data[2],                     
                            description=data[3],                     
                            cost=data[4],                     
                                              
                        )
                    except IntegrityError:
                        messages.warning(request, f'Duplicate entry found for {data[0]}. Skipping this record.')
                        continue

                return redirect('kahamahmis:manage_service') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportServiceForm()

    return render(request, 'kahama_template/import_service.html', {'form': form})

@login_required
def import_country_records(request):
    if request.method == 'POST':
        form = ImportCountryForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = CountryResource()
                new_records = request.FILES['country_records_file']

                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly
                
                for data in imported_data:
                    try:
                        country_record = Country.objects.create(
                            name=data[0],                                        
                                              
                        )
                    except IntegrityError:
                        messages.warning(request, f'Duplicate entry found for {data[0]}. Skipping this record.')
                        continue

                return redirect('kahamahmis:manage_country') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportCountryForm()

    return render(request, 'kahama_template/import_country.html', {'form': form})

@login_required
def import_health_records(request):
    if request.method == 'POST':
        form = ImportHealthRecordForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = HealthRecordResource()
                new_records = request.FILES['health_records_file']

                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly
                
                for data in imported_data:
                    try:
                        health_record = HealthRecord.objects.create(
                            name=data[0],                                        
                                              
                        )
                    except IntegrityError:
                        messages.warning(request, f'Duplicate entry found for {data[0]}. Skipping this record.')
                        continue

                return redirect('kahamahmis:health_record_list') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportHealthRecordForm()

    return render(request, 'kahama_template/import_health_record.html', {'form': form})

@login_required
def import_referral_records(request):
    if request.method == 'POST':
        form = ImportReferralForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = ReferralResource()
                new_records = request.FILES['referral_records_file']

                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly
                
                for data in imported_data:
                    try:
                        referral_record =Referral.objects.create(
                            patient=Patients.objects.get(mrn=data[0]),
                            source_location=data[1],                     
                            destination_location=data[2],                     
                            reason=data[3],                     
                            notes=data[4],                     
                                           
                        )
                    except IntegrityError:
                        messages.warning(request, f'Duplicate entry found for {data[0]}. Skipping this record.')
                        continue

                return redirect('kahamahmis:manage_referral') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportReferralForm()

    return render(request, 'kahama_template/import_referral.html', {'form': form})

@login_required
def import_procedure_records(request):
    if request.method == 'POST':
        form = ImportProcedureForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = ProcedureResource()
                new_records = request.FILES['procedure_records_file']

                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly
                
                for data in imported_data:
                    try:
                        procedure_record = Procedure.objects.create(
                            patient=Patients.objects.get(mrn=data[0]),
                            name=data[1],                     
                            description=data[2],                     
                            duration_time=data[3],                     
                            equipments_used=data[4],                     
                            cost=data[5],                     
                          )
                    except IntegrityError:
                        messages.warning(request, f'Duplicate entry found for {data[0]}. Skipping this record.')
                        continue

                return redirect('kahamahmis:patient_procedure_view') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportProcedureForm()

    return render(request, 'kahama_template/import_procedure.html', {'form': form})

@login_required
def import_medicine_records(request):
    if request.method == 'POST':
        form = ImportMedicineForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resource = MedicineResource()
                new_records = request.FILES['medicine_records_file']

                # Use tablib to load the imported data
                dataset = resource.export()
                imported_data = dataset.load(new_records.read(), format='xlsx')  # Assuming you are using xlsx, adjust accordingly
                
                for data in imported_data:
                    try:
                        medicine_record = Medicine.objects.create(
                            name=data[0],
                            medicine_type=data[1],                     
                            side_effect=data[2],                     
                            dosage=data[3],                     
                            storage_condition=data[4],                     
                            manufacturer=data[5],                     
                            description=data[6],                     
                            expiration_date=data[7],                     
                            unit_price=data[8],                    
                                        
                        )
                    except IntegrityError:
                        messages.warning(request, f'Duplicate entry found for {data[0]}. Skipping this record.')
                        continue

                return redirect('kahamahmis:medicine_list') 
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')

    else:
        form = ImportMedicineForm()

    return render(request, 'kahama_template/import_medicine_records.html', {'form': form})


def generate_mrn():
    # Retrieve the last patient's MRN from the database
    last_patient = Patients.objects.last()

    # Extract the numeric part from the last MRN, or start from 0 if there are no patients yet
    last_mrn_number = int(last_patient.mrn.split('-')[-1]) if last_patient else 0

    # Increment the numeric part for the new patient
    new_mrn_number = last_mrn_number + 1

    # Format the MRN with leading zeros and concatenate with the prefix "PAT-"
    new_mrn = f"PAT-{new_mrn_number:05d}"

    return new_mrn