from datetime import datetime
import logging
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from clinic.models import DiseaseRecode, InsuranceCompany,  PathodologyRecord, Patients, Medicine, Procedure, Referral, RemoteCompany, RemoteConsultation, RemoteLaboratoryOrder, RemoteObservationRecord, RemotePatient, RemoteProcedure, RemoteReferral, Staffs
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import F
from django.contrib.auth.decorators import login_required
# Define a logger
logger = logging.getLogger(__name__)




def update_consultation_data(request, appointment_id):
    # Get the Consultation instance
    if request.method == 'POST':
        try:
            # Extract form data from the request
            doctor_id = request.POST.get('doctor')
            patient_id = request.POST.get('patient')
            appointment_date = request.POST.get('appointmentDate')
            start_time = request.POST.get('startTime')
            end_time = request.POST.get('endTime')
            description = request.POST.get('description')          
            consultation = get_object_or_404(RemoteConsultation, id=appointment_id)
            # Update Consultation instance with new data
            consultation.doctor = Staffs.objects.get(id=doctor_id)
            consultation.patient = Patients.objects.get(id=patient_id)
            consultation.appointment_date = appointment_date
            consultation.start_time = start_time
            consultation.end_time = end_time
            consultation.description = description          

            # Save the updated Consultation instance
            consultation.save()

            # Return a JsonResponse to indicate success
            return redirect("kahama_appointment_list")
        except Exception as e:
            # Return a JsonResponse with an error message
            return HttpResponseBadRequest(f"Error: {str(e)}") 

    # If the request is not a POST request, you might want to handle it accordingly (e.g., render a form)
    return HttpResponseBadRequest("Invalid request method")


