from import_export import resources
from .models import AmbulanceActivity, AmbulanceRoute, HealthRecord, MedicineRoute, MedicineUnitMeasure, PrescriptionFrequency, Country, Diagnosis, DiseaseRecode, Equipment,   Medicine, PathodologyRecord, Patients, Procedure, Reagent, Referral, RemoteCompany, RemoteMedicine, RemotePatient, RemoteService,Service

class DiseaseRecodeResource(resources.ModelResource):
    class Meta:
        model = DiseaseRecode
        
       
        
class CompanyResource(resources.ModelResource):
    class Meta:
        model = RemoteCompany        

class PathologyRecordResource(resources.ModelResource):
    class Meta:
        model = PathodologyRecord        

class PatientsResource(resources.ModelResource):
    class Meta:
        model = Patients 
class MedicineResource(resources.ModelResource):
    class Meta:
        model = Medicine 
class ProcedureResource(resources.ModelResource):
    class Meta:
        model = Procedure 
class ReferralResource(resources.ModelResource):
    class Meta:
        model = Referral
class ServiceResource(resources.ModelResource):
    class Meta:
        model = Service



class EquipmentResource(resources.ModelResource):
    class Meta:
        model = Equipment

class ReagentResource(resources.ModelResource):
    class Meta:
        model = Reagent

class DiagnosisResource(resources.ModelResource):
    class Meta:
        model = Diagnosis

class RemoteServiceResource(resources.ModelResource):
    class Meta:
        model = RemoteService
class RemotePatientResource(resources.ModelResource):
    class Meta:
        model = RemotePatient
        
class CountryResource(resources.ModelResource):
    class Meta:
        model = Country
class HealthRecordResource(resources.ModelResource):
    class Meta:
        model = HealthRecord
class PrescriptionFrequencyResource(resources.ModelResource):
    class Meta:
        model = PrescriptionFrequency
class AmbulanceRouteResource(resources.ModelResource):
    class Meta:
        model = AmbulanceRoute
class AmbulanceActivityResource(resources.ModelResource):
    class Meta:
        model = AmbulanceActivity
class MedicineRouteResource(resources.ModelResource):
    class Meta:
        model = MedicineRoute
class MedicineUnitMeasureResource(resources.ModelResource):
    class Meta:
        model = MedicineUnitMeasure
class RemoteMedicineResource(resources.ModelResource):
    class Meta:
        model = RemoteMedicine