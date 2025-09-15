import calendar
from datetime import  date, datetime, timedelta, timezone as dt_timezone
import json
from django.utils import timezone
import logging
from django.urls import reverse
from django.db.models import F
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, JsonResponse
from django.db.models import Sum, Max, Count
from django.db.models import OuterRef, Subquery
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from clinic.forms import CounselingForm, DischargesNotesForm, ImagingRecordForm, LaboratoryOrderForm, ObservationRecordForm, ProcedureForm, ReferralForm, StaffProfileForm
from django.core.exceptions import ValidationError
from clinic.models import  Consultation,   Medicine,   Staffs
from django.views.decorators.http import require_POST, require_GET
from .models import ClinicChiefComplaint,   ConsultationNotes,  ConsultationOrder, Counseling, Country, CustomUser, Diagnosis, DischargesNotes, Employee, EmployeeDeduction, HealthRecord, ImagingRecord,  LaboratoryOrder, MedicineDosage, MedicineRoute, ObservationRecord, Order, PatientDiagnosisRecord, PatientVisits, PatientVital, Prescription, PrescriptionFrequency, Procedure, Patients,  Referral, SalaryChangeRecord,Service
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator

@login_required
def doctor_dashboard(request):
    try:
        today = date.today()
       
        total_patients_count = Patients.objects.count()

        # Today's Visits
        today_visits = PatientVisits.objects.filter(updated_at__date=today)
        today_total_patients = today_visits.count()

        # Today's Consultations
        today_notes = ConsultationNotes.objects.filter(updated_at__date=today)
        completed_notes = today_notes.filter(doctor_plan__in=["Discharge", "Referral"])
        in_progress_notes = today_notes.exclude(doctor_plan__in=["Discharge", "Referral"])
        today_completed_patients = completed_notes.values('patient').distinct().count()
        today_in_progress_patients = in_progress_notes.values('patient').distinct().count()

        # Lab Orders
        today_lab_orders = LaboratoryOrder.objects.filter(created_at__date=today)
        today_lab_patients_count = today_lab_orders.values('patient').distinct().count()
        in_progress_lab_patients_count = today_lab_orders.filter(Q(result__isnull=True) | Q(result__exact='')).values('patient').distinct().count()
        completed_lab_patients_count = today_lab_patients_count - in_progress_lab_patients_count if today_lab_patients_count else 0

        # Prescriptions
        today_prescriptions = Prescription.objects.filter(created_at__date=today)
        today_today_prescription_count = today_prescriptions.values('patient').distinct().count()

        # Procedures
        today_procedures = Procedure.objects.filter(created_at__date=today)
        today_procedure_patients_count = today_procedures.values('patient').distinct().count()
        in_progress_procedure_patients_count = today_procedures.filter(Q(result__isnull=True) | Q(result__exact='')).values('patient').distinct().count()
        completed_procedure_patients_count = today_procedure_patients_count - in_progress_procedure_patients_count if today_procedure_patients_count else 0

        # Imaging
        today_imagings = ImagingRecord.objects.filter(created_at__date=today)
        today_imaging_patients_count = today_imagings.values('patient').distinct().count()
        in_progress_imaging_patients_count = today_imagings.filter(Q(result__isnull=True) | Q(result__exact='')).values('patient').distinct().count()
        completed_imaging_patients_count = today_imaging_patients_count - in_progress_imaging_patients_count if today_imaging_patients_count else 0

        # Recent consultations (last 10)
        recent_consultations = ConsultationNotes.objects.select_related('patient').order_by('-created_at')[:10]

        # Upcoming appointments (next 7 days)
        upcoming_appointments = Consultation.objects.filter(
            appointment_date__gte=today,
            appointment_date__lte=today + timedelta(days=7)
        ).select_related('patient').order_by('appointment_date')[:10]

        context = {
            # General
            'total_patients_count': total_patients_count,
            'today_total_patients': today_total_patients,

            # Consultations
            'today_in_progress_patients': today_in_progress_patients,
            'today_completed_patients': today_completed_patients,

            # Lab Orders
            'today_lab_orders': today_lab_patients_count,
            'in_progress_lab_orders': in_progress_lab_patients_count,
            'completed_lab_orders': completed_lab_patients_count,

            # Prescriptions
            'today_today_prescription_count': today_today_prescription_count,

            # Procedures
            'today_procedure_patients': today_procedure_patients_count,
            'in_progress_procedures': in_progress_procedure_patients_count,
            'completed_procedures': completed_procedure_patients_count,

            # Imaging
            'today_imaging_patients': today_imaging_patients_count,
            'in_progress_imagings': in_progress_imaging_patients_count,
            'completed_imagings': completed_imaging_patients_count,

            # Additional data for the premium dashboard
            'recent_consultations': recent_consultations,
            'upcoming_appointments': upcoming_appointments,
        }

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        context = {
            'total_patients_count': 0,
            'today_total_patients': 0,
            'today_in_progress_patients': 0,
            'today_completed_patients': 0,
            'today_lab_orders': 0,
            'in_progress_lab_orders': 0,
            'completed_lab_orders': 0,
            'today_today_prescription_count': 0,
            'today_procedure_patients': 0,
            'in_progress_procedures': 0,
            'completed_procedures': 0,
            'today_imaging_patients': 0,
            'in_progress_imagings': 0,
            'completed_imagings': 0,
            'recent_consultations': [],
            'upcoming_appointments': [],
        }

    return render(request, "doctor_template/home_content.html", context)




@login_required
def doctor_today_patients(request):
    today = date.today()
    doctor = request.user.staff  # Assuming the user is linked to Staffs model
    
    # Get today's patients for this doctor
    today_patients = Patients.objects.filter(
        Q(consultation__doctor=doctor, consultation__appointment_date=today) |
        Q(consultationnotes__doctor=doctor, consultationnotes__created_at__date=today) |
        Q(imagingrecord__doctor=doctor, imagingrecord__order_date=today) |
        Q(procedure__doctor=doctor, procedure__order_date=today) |
        Q(laboratoryorder__doctor=doctor, laboratoryorder__order_date=today)
    ).distinct()
    
    context = {
        'patients': today_patients,
        'page_title': "Today's Patients"
    }
    return render(request, 'doctor_template/today_patients.html', context)

@login_required
def doctor_in_progress_consultations(request):
    doctor = request.user.staff
    
    # Get in-progress consultations for this doctor
    in_progress_consultations = ConsultationNotes.objects.filter(
        doctor=doctor
    ).exclude(
        Q(doctor_plan__in=["Discharge", "Referral"])
    ).order_by('-created_at')
    
    context = {
        'consultations': in_progress_consultations,
        'page_title': "In Progress Consultations"
    }
    return render(request, 'doctor_template/in_progress_consultations.html', context)

@login_required
def doctor_completed_consultations(request):
    doctor = request.user.staff
    today = date.today()
    
    # Get completed consultations for today for this doctor
    completed_consultations = ConsultationNotes.objects.filter(
        doctor=doctor,
        created_at__date=today,
        doctor_plan__in=["Discharge", "Referral"]
    ).order_by('-created_at')
    
    context = {
        'consultations': completed_consultations,
        'page_title': "Completed Consultations"
    }
    return render(request, 'doctor_template/completed_consultations.html', context)



@login_required
def doctor_today_imaging_orders(request):
    doctor = request.user.staff
    today = date.today()
    
    # Get today's imaging orders for this doctor
    today_imaging_orders = ImagingRecord.objects.filter(
        doctor=doctor,
        order_date=today
    ).order_by('-created_at')
    
    context = {
        'imaging_orders': today_imaging_orders,
        'page_title': "Today's Imaging Orders"
    }
    return render(request, 'doctor_template/today_imaging_orders.html', context)

@login_required
def doctor_pending_imaging(request):
    doctor = request.user.staff
    
    # Get pending imaging results for this doctor
    pending_imaging = ImagingRecord.objects.filter(
        doctor=doctor
    ).filter(
        Q(result__isnull=True) | Q(result__exact='')
    ).order_by('-created_at')
    
    context = {
        'imaging_records': pending_imaging,
        'page_title': "Pending Imaging Results"
    }
    return render(request, 'doctor_template/pending_imaging.html', context)

@login_required
def doctor_completed_imaging(request):
    doctor = request.user.staff
    
    # Get completed imaging for this doctor
    completed_imaging = ImagingRecord.objects.filter(
        doctor=doctor
    ).exclude(
        Q(result__isnull=True) | Q(result__exact='')
    ).order_by('-created_at')
    
    context = {
        'imaging_records': completed_imaging,
        'page_title': "Completed Imaging"
    }
    return render(request, 'doctor_template/completed_imaging.html', context)

@login_required
def doctor_today_procedures(request):
    doctor = request.user.staff
    today = date.today()
    
    # Get today's procedures for this doctor
    today_procedures = Procedure.objects.filter(
        doctor=doctor,
        order_date=today
    ).order_by('-created_at')
    
    context = {
        'procedures': today_procedures,
        'page_title': "Today's Procedures"
    }
    return render(request, 'doctor_template/today_procedures.html', context)

@login_required
def doctor_pending_procedures(request):
    doctor = request.user.staff
    
    # Get pending procedures for this doctor
    pending_procedures = Procedure.objects.filter(
        doctor=doctor
    ).filter(
        Q(result__isnull=True) | Q(result__exact='')
    ).order_by('-created_at')
    
    context = {
        'procedures': pending_procedures,
        'page_title': "Pending Procedures"
    }
    return render(request, 'doctor_template/pending_procedures.html', context)

@login_required
def doctor_completed_procedures(request):
    doctor = request.user.staff
    
    # Get completed procedures for this doctor
    completed_procedures = Procedure.objects.filter(
        doctor=doctor
    ).exclude(
        Q(result__isnull=True) | Q(result__exact='')
    ).order_by('-created_at')
    
    context = {
        'procedures': completed_procedures,
        'page_title': "Completed Procedures"
    }
    return render(request, 'doctor_template/completed_procedures.html', context)

@login_required
def doctor_consultation_list(request):
    doctor = request.user.staff
    
    # Get all consultations for this doctor
    consultations = ConsultationNotes.objects.filter(
        doctor=doctor
    ).order_by('-created_at')
    
    context = {
        'consultations': consultations,
        'page_title': "All Consultations"
    }
    return render(request, 'doctor_template/consultation_list.html', context)


@login_required
def doctor_dashboard_stats_api(request):
    """
    API endpoint to fetch all statistics for the doctor dashboard
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        # Get today's date
        today = timezone.now().date()
        doctor = request.user.staff
        
        # Today's appointments
        today_appointments = Consultation.objects.filter(
            doctor=doctor,
            appointment_date=today,
            status__in=[0, 6]  # Pending or Confirmed
        ).count()

        # Pending consultations
        pending_consultations = ConsultationOrder.objects.filter(
            doctor=doctor          
        ).count()

        # Total patients seen by this doctor
        total_patients = Patients.objects.filter(
            consultation__doctor=doctor
        ).distinct().count()

        # Upcoming appointments in next 7 days
        seven_days_later = today + timedelta(days=7)
        upcoming_appointments = Consultation.objects.filter(
            doctor=doctor,
            appointment_date__range=(today, seven_days_later),
            status__in=[0, 6]
        ).count()
        
        # Order counts (today and total)
        consultation_orders_today = ConsultationOrder.objects.filter(
            doctor=doctor, 
            order_date=today
        ).count()
        
        consultation_orders_total = ConsultationOrder.objects.filter(
            doctor=doctor
        ).count()
        
        radiology_orders_today = ImagingRecord.objects.filter(
            doctor=doctor, 
            order_date=today
        ).count()
        
        radiology_orders_total = ImagingRecord.objects.filter(
            doctor=doctor
        ).count()
        
        procedure_orders_today = Procedure.objects.filter(
            doctor=doctor, 
            order_date=today
        ).count()
        
        procedure_orders_total = Procedure.objects.filter(
            doctor=doctor
        ).count()

        return JsonResponse({
            'today_appointments': today_appointments,
            'pending_consultations': pending_consultations,
            'total_patients': total_patients,
            'upcoming_appointments': upcoming_appointments,
            'consultation_orders_today': consultation_orders_today,
            'consultation_orders_total': consultation_orders_total,
            'radiology_orders_today': radiology_orders_today,
            'radiology_orders_total': radiology_orders_total,
            'procedure_orders_today': procedure_orders_today,
            'procedure_orders_total': procedure_orders_total,
            'status': 'success'
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)


@login_required
def appointment_redirect(request, appointment_id):
    """
    Redirect any appointment detail URL to the appointment list page.
    """
    # Optionally, you can fetch the appointment to validate it exists
    get_object_or_404(Consultation, id=appointment_id)

    # Redirect to appointment list using URL name
    redirect_url = reverse("doctor_appointment_list")  # replace with your URL name
    return redirect(redirect_url)


@login_required
def doctor_notifications_api(request):
    """
    API endpoint to fetch doctor-specific notifications
    """
    try:
        doctor = request.user.staff
        today = timezone.now().date()
        three_days_ago = today - timedelta(days=3)
        notifications = []

        # -------------------- TODAY'S APPOINTMENTS --------------------
        today_appointments = Consultation.objects.filter(
            doctor=doctor,
            appointment_date=today,
            status__in=[0, 6]  # Pending or Confirmed
        ).select_related('patient')

        for appointment in today_appointments:
            time_str = appointment.start_time.strftime("%H:%M") if appointment.start_time else "Time not set"
            notifications.append({
                'id': appointment.id,
                'icon': 'fas fa-calendar-check',
                'iconColor': 'text-primary',
                'title': 'Appointment Today',
                'time': time_str,
                'details': f'Patient: {appointment.patient.full_name}',
                'url': f'/doctor/appointment/{appointment.id}/',  # Adjust URL as needed
                'timestamp': appointment.created_at.isoformat()
            })

        # -------------------- RECENT CONSULTATION ORDERS --------------------
        recent_consultations = ConsultationOrder.objects.filter(
            Q(doctor=doctor) & Q(order_date__gte=three_days_ago)
        ).select_related('patient', 'consultation')[:5]

        for consultation in recent_consultations:
            service_name = consultation.consultation.name if consultation.consultation else "Consultation"
            notifications.append({
                'id': consultation.id,
                'icon': 'fas fa-stethoscope',
                'iconColor': 'text-info',
                'title': 'Consultation Order',
                'time': consultation.order_date.strftime("%Y-%m-%d") if consultation.order_date else "Date not set",
                'details': f'Patient: {consultation.patient.full_name} - {service_name}',
                'url': f'/doctor/consultation-order/{consultation.id}/',
                'timestamp': consultation.created_at.isoformat()
            })

        # -------------------- RECENT IMAGING ORDERS --------------------
        recent_imaging = ImagingRecord.objects.filter(
            Q(doctor=doctor) & Q(order_date__gte=three_days_ago)
        ).select_related('patient', 'imaging')[:5]

        for imaging in recent_imaging:
            service_name = imaging.imaging.name if imaging.imaging else "Imaging"
            notifications.append({
                'id': imaging.id,
                'icon': 'fas fa-x-ray',
                'iconColor': 'text-warning',
                'title': 'Imaging Order',
                'time': imaging.order_date.strftime("%Y-%m-%d") if imaging.order_date else "Date not set",
                'details': f'Patient: {imaging.patient.full_name} - {service_name}',
                'url': f'/doctor/imaging-order/{imaging.id}/',
                'timestamp': imaging.created_at.isoformat()
            })

        # -------------------- RECENT PROCEDURES --------------------
        recent_procedures = Procedure.objects.filter(
            Q(doctor=doctor) & Q(order_date__gte=three_days_ago)
        ).select_related('patient', 'name')[:5]

        for procedure in recent_procedures:
            service_name = procedure.name.name if procedure.name else "Procedure"
            notifications.append({
                'id': procedure.id,
                'icon': 'fas fa-procedures',
                'iconColor': 'text-success',
                'title': 'Procedure Order',
                'time': procedure.order_date.strftime("%Y-%m-%d") if procedure.order_date else "Date not set",
                'details': f'Patient: {procedure.patient.full_name} - {service_name}',
                'url': f'/doctor/procedure/{procedure.id}/',
                'timestamp': procedure.created_at.isoformat()
            })

        # -------------------- SORT & FORMAT --------------------
        notifications.sort(key=lambda x: x['timestamp'], reverse=True)
        notifications = notifications[:10]

        # Format timestamp into "time ago"
        for notif in notifications:
            notif['time'] = time_ago(notif['timestamp'])

        return JsonResponse({
            'notifications': notifications,
            'status': 'success'
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)


# -------------------- HELPER FUNCTION --------------------
def time_ago(timestamp: str) -> str:
    """
    Convert ISO timestamp into a human-readable 'time ago' string.
    """
    try:
        now = datetime.now(dt_timezone.utc)
        dt = datetime.fromisoformat(timestamp)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=dt_timezone.utc)
        diff = now - dt
        seconds = diff.total_seconds()

        if seconds < 60:
            return f"{int(seconds)} seconds ago"
        elif seconds < 3600:
            return f"{int(seconds // 60)} minutes ago"
        elif seconds < 86400:
            return f"{int(seconds // 3600)} hours ago"
        else:
            return f"{int(seconds // 86400)} days ago"
    except Exception:
        return timestamp


@login_required
def doctor_all_notifications(request):
    """
    View to render the notifications page
    """
    context = {
        'page_title': 'Notifications Center',
    }
    return render(request, 'doctor_template/notifications.html', context)

@login_required
def doctor_all_notifications_api(request):
    """
    API endpoint to fetch paginated notifications with filters
    """
    try:
        doctor = request.user.staff
        today = timezone.now().date()
        
        # Get filter parameters
        page_number = request.GET.get('page', 1)
        type_filter = request.GET.get('type', 'all')
        date_range = request.GET.get('date_range', '')
        status_filter = request.GET.get('status', 'all')
        sort_filter = request.GET.get('sort', 'newest')
        
        notifications = []
        
        # Base queries with date filtering if applicable
        if date_range:
            try:
                start_date, end_date = date_range.split(' - ')
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
                date_filter = Q(created_at__date__range=(start_date, end_date))
            except:
                # If date range is invalid, default to last 30 days
                thirty_days_ago = today - timedelta(days=30)
                date_filter = Q(created_at__date__gte=thirty_days_ago)
        else:
            # Default to last 30 days if no date range specified
            thirty_days_ago = today - timedelta(days=30)
            date_filter = Q(created_at__date__gte=thirty_days_ago)
        
        # Appointments
        if type_filter in ['all', 'appointment']:
            appointments = Consultation.objects.filter(
                Q(doctor=doctor) & date_filter
            ).select_related('patient')
            
            for appointment in appointments:
                status_text = " (Today)" if appointment.appointment_date == today else ""
                notifications.append({
                    'id': f'appt_{appointment.id}',
                    'type': 'appointment',
                    'type_display': 'Appointment',
                    'title': f'Appointment{status_text}',
                    'details': f'Patient: {appointment.patient.full_name}',
                    'date': appointment.appointment_date.strftime('%Y-%m-%d'),
                    'time': appointment.start_time.strftime("%H:%M") if appointment.start_time else "Time not set",
                    'url': f'/doctor/appointment/{appointment.id}/',
                    'created_at': appointment.created_at,
                    'is_read': False  # You would need to implement read status tracking
                })
        
        # Consultation orders
        if type_filter in ['all', 'consultation']:
            consultations = ConsultationOrder.objects.filter(
                Q(doctor=doctor) & date_filter
            ).select_related('patient', 'consultation')
            
            for consultation in consultations:
                service_name = consultation.consultation.name if consultation.consultation else "Consultation"
                notifications.append({
                    'id': f'cons_{consultation.id}',
                    'type': 'consultation',
                    'type_display': 'Consultation Order',
                    'title': 'Consultation Order',
                    'details': f'Patient: {consultation.patient.full_name} - {service_name}',
                    'date': consultation.order_date.strftime('%Y-%m-%d') if consultation.order_date else consultation.created_at.strftime('%Y-%m-%d'),
                    'time': consultation.created_at.strftime("%H:%M"),
                    'url': f'/doctor/consultation-order/{consultation.id}/',
                    'created_at': consultation.created_at,
                    'is_read': False
                })
        
        # Imaging orders
        if type_filter in ['all', 'imaging']:
            imaging_orders = ImagingRecord.objects.filter(
                Q(doctor=doctor) & date_filter
            ).select_related('patient', 'imaging')
            
            for order in imaging_orders:
                service_name = order.imaging.name if order.imaging else "Imaging"
                notifications.append({
                    'id': f'img_{order.id}',
                    'type': 'imaging',
                    'type_display': 'Imaging Order',
                    'title': 'Imaging Order',
                    'details': f'Patient: {order.patient.full_name} - {service_name}',
                    'date': order.order_date.strftime('%Y-%m-%d') if order.order_date else order.created_at.strftime('%Y-%m-%d'),
                    'time': order.created_at.strftime("%H:%M"),
                    'url': f'/doctor/imaging-order/{order.id}/',
                    'created_at': order.created_at,
                    'is_read': False
                })
        
        # Procedure orders
        if type_filter in ['all', 'procedure']:
            procedures = Procedure.objects.filter(
                Q(doctor=doctor) & date_filter
            ).select_related('patient', 'name')
            
            for procedure in procedures:
                service_name = procedure.name.name if procedure.name else "Procedure"
                notifications.append({
                    'id': f'proc_{procedure.id}',
                    'type': 'procedure',
                    'type_display': 'Procedure Order',
                    'title': 'Procedure Order',
                    'details': f'Patient: {procedure.patient.full_name} - {service_name}',
                    'date': procedure.order_date.strftime('%Y-%m-%d') if procedure.order_date else procedure.created_at.strftime('%Y-%m-%d'),
                    'time': procedure.created_at.strftime("%H:%M"),
                    'url': f'/doctor/procedure/{procedure.id}/',
                    'created_at': procedure.created_at,
                    'is_read': False
                })
        
        # Apply sorting
        if sort_filter == 'newest':
            notifications.sort(key=lambda x: x['created_at'], reverse=True)
        elif sort_filter == 'oldest':
            notifications.sort(key=lambda x: x['created_at'])
        elif sort_filter == 'type':
            notifications.sort(key=lambda x: x['type'])
        
        # Apply status filter (for demonstration; in a real app, you'd have a read status field)
        if status_filter == 'unread':
            notifications = [n for n in notifications if not n['is_read']]
        elif status_filter == 'read':
            notifications = [n for n in notifications if n['is_read']]
        
        # Paginate results
        paginator = Paginator(notifications, 10)  # Show 10 notifications per page
        page_obj = paginator.get_page(page_number)
        
        # Format the notifications for the response
        formatted_notifications = []
        for notif in page_obj.object_list:
            formatted_notif = notif.copy()
            # Convert datetime to string for JSON serialization
            formatted_notif['created_at'] = notif['created_at'].isoformat()
            formatted_notifications.append(formatted_notif)
        
        return JsonResponse({
            'status': 'success',
            'notifications': formatted_notifications,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'total_count': paginator.count
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

@login_required
def doctor_toggle_notification_api(request):
    """
    API endpoint to toggle notification read status
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            notification_id = data.get('notification_id')
            
            # In a real implementation, you would update a Notification model
            # For now, we'll just return success
            # Example: notification = Notification.objects.get(id=notification_id, user=request.user)
            # notification.is_read = not notification.is_read
            # notification.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Notification status updated'
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'status': 'error'
            }, status=500)
    
    return JsonResponse({
        'error': 'Invalid request method',
        'status': 'error'
    }, status=400)

@login_required
def doctor_delete_notification_api(request):
    """
    API endpoint to delete a notification
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            notification_id = data.get('notification_id')
            
            # In a real implementation, you would delete from a Notification model
            # For now, we'll just return success
            # Example: Notification.objects.filter(id=notification_id, user=request.user).delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Notification deleted'
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'status': 'error'
            }, status=500)
    
    return JsonResponse({
        'error': 'Invalid request method',
        'status': 'error'
    }, status=400)


@login_required
def doctor_profile(request):
    # Get the currently logged-in user
    user = request.user
    
    try:
        # Fetch the doctor's details from the Staffs model (assuming the doctor is a staff member)
        staff = Staffs.objects.get(admin=user, role='doctor')
        
        # Pass the doctor details to the template
        return render(request, 'doctor_template/profile.html', {'staff': staff})

    except Staffs.DoesNotExist:
        # Handle case if no staff member with the role 'doctor' is found
        return render(request, 'doctor_template/profile.html', {'error': 'Doctor not found.'})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Prevent user logout before redirecting
            messages.success(request, "Your password was successfully updated! Please log in again.")
            logout(request)  # Log out the user
            
            # Redirect based on workplace
            if request.user.staff.work_place == 'kahama':
                return redirect('kahamahmis:kahama')  # Redirect to Kahama login page
            else:
                return redirect('login')  # Redirect to default login page (Resa)

        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'doctor_template/change_password.html', {'form': form})          

@method_decorator(login_required, name='dispatch')
class EditStaffProfileView(View):
    template_name = 'doctor_template/edit_profile.html'

    def get(self, request, pk):
        staff = get_object_or_404(Staffs, id=pk, admin=request.user)
        form = StaffProfileForm(instance=staff)
        return render(request, self.template_name, {'form': form, 'staff': staff})

    def post(self, request, pk):
        staff = get_object_or_404(Staffs, id=pk, admin=request.user)
        form = StaffProfileForm(request.POST, request.FILES, instance=staff)

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('doctor_edit_staff_profile', pk=staff.id)


def get_gender_yearly_data(request):
    if request.method == 'GET':
        selected_year = request.GET.get('year')
        
        # Query the database to get the total number of male and female patients for the selected year
        male_count = Patients.objects.filter(gender='Male', created_at__year=selected_year).count()
        female_count = Patients.objects.filter(gender='Female', created_at__year=selected_year).count()

        # Create a dictionary with the total male and female counts
        yearly_gender_data = {
            'Male': male_count,
            'Female': female_count
        }

        return JsonResponse(yearly_gender_data)
    else:
        # Return an error response if the request method is not GET or if it's not an AJAX request
        return JsonResponse({'error': 'Invalid request'})
    
def get_gender_monthly_data(request):
    if request.method == 'GET':
        selected_year = request.GET.get('year')       
        # Initialize a dictionary to store gender-wise monthly data
        gender_monthly_data = {}

        # Loop through each month and calculate gender-wise counts
        for month in range(1, 13):
            # Get the number of males and females for the current month and year
            male_count = Patients.objects.filter(
                gender='Male',
                created_at__year=selected_year,
                created_at__month=month
            ).count()            
            female_count = Patients.objects.filter(
                gender='Female',
                created_at__year=selected_year,
                created_at__month=month
            ).count()

            # Store the counts in the dictionary
            month_name = calendar.month_name[month]
            gender_monthly_data[month_name] = {'Male': male_count, 'Female': female_count}

        return JsonResponse(gender_monthly_data)
    else:
        return JsonResponse({'error': 'Invalid request'})




@login_required
def manage_patient(request):
    patient_records=Patients.objects.all().order_by('-created_at') 
    range_121 = range(1, 121)
    all_country = Country.objects.all()
    doctors=Staffs.objects.filter(role='doctor')
    return render(request,"doctor_template/manage_patients.html", {
        "patients":patient_records,
        "range_121":range_121,
        "doctors":doctors,
        "all_country":all_country,
        })
    


@login_required
def manage_consultation(request):
    patients=Patients.objects.all()
    doctors=Staffs.objects.filter(role='doctor')
    context = {
        'patients':patients,   
        'doctors':doctors,
    }
    return render(request,"doctor_template/manage_consultation.html",context)



logger = logging.getLogger(__name__)


    
@csrf_exempt
def appointment_view_remote(request, patient_id):
    try:
        if request.method == 'POST':
            # Extract data from the request
            doctor_id = request.POST.get('doctor')
            date_of_consultation = request.POST.get('date_of_consultation')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            description = request.POST.get('description')

            # Check if all required fields are present
            if not (doctor_id and date_of_consultation and start_time and end_time):
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

            # Retrieve doctor and patient instances
            doctor = get_object_or_404(Staffs, id=doctor_id)
            patient = get_object_or_404(Patients, id=patient_id)

            # Create a Consultation instance
            consultation = Consultation(
                doctor=doctor,
                patient=patient,
                appointment_date=date_of_consultation,
                start_time=start_time,
                end_time=end_time,
                description=description
            )
            consultation.save()
            messages.success(request, "Appointment created successfully.")
            return JsonResponse({'status': 'success'})
       
    except IntegrityError as e:
        # Handle integrity error (e.g., duplicate entry)
        messages.error(request, f"Error creating appointment: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)})
    except Exception as e:
        # Handle other exceptions
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred'})

    # Handle invalid request method
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})





def confirm_meeting(request, appointment_id):
    try:
        # Retrieve the appointment
        appointment = get_object_or_404(Consultation, id=appointment_id)

        if request.method == 'POST':
            # Get the selected status from the form
            selected_status = int(request.POST.get('status'))

            # Check if the appointment is not already confirmed
            if not appointment.status:
                # Perform the confirmation action (e.g., set status to selected status)
                appointment.status = selected_status
                appointment.save()
                
            elif appointment.status:
                # Perform the confirmation action (e.g., set status to selected status)
                appointment.status = selected_status
                appointment.save()

                # Add a success message
                messages.success(request, f"Meeting with {appointment.patient.mrn} confirmed.")
            else:
                messages.warning(request, f"Meeting with {appointment.patient.mrn} is already confirmed.")
        else:
            messages.warning(request, "Invalid request method for confirming meeting.")

    except IntegrityError as e:
        # Handle IntegrityError (e.g., database constraint violation)
        messages.error(request, f"Error confirming meeting: {str(e)}")

    return redirect('doctor_read_appointments')  # Adjust the URL name based on your actual URL structure

def edit_meeting(request, appointment_id):
    try:
        if request.method == 'POST':
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')

            appointment = get_object_or_404(Consultation, id=appointment_id)

            # Perform the edit action (e.g., update start time and end time)
            appointment.start_time = start_time
            appointment.end_time = end_time
            appointment.save()

            messages.success(request, f"Meeting time for {appointment.patient} edited successfully.")
    except Exception as e:
        messages.error(request, f"Error editing meeting time: {str(e)}")

    return redirect('doctor_read_appointments')




def save_procedure(request):
    if request.method == 'POST':
        procedure_id = request.POST.get('procedure_id')
        procedure = get_object_or_404(Procedure, id=procedure_id)
        form = ProcedureForm(request.POST, instance=procedure)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Procedure updated successfully.'})
        else:
            return JsonResponse({'success': False, 'message': 'Form is not valid.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})




@csrf_exempt
def change_referral_status(request):
    if request.method == 'POST':
        try:
            referral_id = request.POST.get('referralId')
            new_status = request.POST.get('newStatus')
            
            # Update referral record with new status
            referral_record = Referral.objects.get(id=referral_id)
            referral_record.status = new_status
            referral_record.save()

            return JsonResponse({'success': True, 'message': f'Status for {referral_record} changed successfully.'})
        except Referral.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid Referral ID.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {e}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required
def manage_referral(request):
    referrals = Referral.objects.all()
    patients = Patients.objects.all()
    return render(request, 'doctor_template/manage_referral.html', {'referrals': referrals,'patients':patients})


def appointment_list_view(request):
    """
    View for displaying all appointments assigned to the current doctor
    """
    # Get the current doctor (staff member)
    doctor = get_object_or_404(Staffs, admin=request.user)
    
    # Get all appointments for this doctor
    appointments = Consultation.objects.filter(doctor=doctor).order_by('-appointment_date', '-created_at')
    
    # Get counts for different statuses
    status_counts = {
        'total': appointments.count(),
        'pending': appointments.filter(status=0).count(),
        'completed': appointments.filter(status=1).count(),
        'canceled': appointments.filter(status=2).count(),
        'rescheduled': appointments.filter(status=3).count(),
        'noshow': appointments.filter(status=4).count(),
        'in_progress': appointments.filter(status=5).count(),
        'confirmed': appointments.filter(status=6).count(),
        'arrived': appointments.filter(status=7).count(),
    }
    
    context = {
        'appointments': appointments,
        'status_counts': status_counts,
    }
    
    return render(request, 'doctor_template/manage_appointment.html', context)


  

@csrf_exempt
def save_chief_complaint(request):
    try:
        # Ensure the request method is POST
        if request.method == 'POST':
            # Extract data from the POST request
            patient_id = request.POST.get('patient_id')
            visit_id = request.POST.get('visit_id')
            health_record_id = request.POST.get('chief_complain_name')
            other_chief_complaint = request.POST.get('other_complaint')          
            if request.POST.get('chief_complain_duration'):
                duration = request.POST.get('chief_complain_duration')  
            else:
                duration = request.POST.get('other_complain_duration')       

            # Create a new ChiefComplaint object
            chief_complaint = ClinicChiefComplaint(
                duration=duration,
                patient_id=patient_id,
                visit_id=visit_id
            )

            # Set the appropriate fields based on the provided data
            if health_record_id == "other":
                # Check if a ChiefComplaint with the same other_complaint already exists for the given visit_id
                if ClinicChiefComplaint.objects.filter(visit_id=visit_id, other_complaint=other_chief_complaint).exists():
                    return JsonResponse({'status': False, 'message': 'A Other ChiefComplaint with the same name already exists for this patient'})
                chief_complaint.other_complaint = other_chief_complaint
            else:
                # Check if a ChiefComplaint with the same health_record_id already exists for the given visit_id
                if ClinicChiefComplaint.objects.filter(health_record_id=health_record_id, visit_id=visit_id).exists():
                    return JsonResponse({'status': False, 'message': 'A ChiefComplaint with the same name  already exists for this patient'})
                chief_complaint.health_record_id = health_record_id          

            chief_complaint.data_recorder = request.user.staff  
            # Save the ChiefComplaint object
            chief_complaint.save()

            # Initialize health_record_data to None
            health_record_data = None

            # Serialize the HealthRecord object if applicable
            if health_record_id and health_record_id != "other":
                health_record = HealthRecord.objects.get(pk=health_record_id)
                # Extract the name of the health record
                health_record_data = {'name': health_record.name}
            
            # Return the saved data as a JSON response
            response_data = {
                'status': True,
                'id': chief_complaint.id,
                'health_record': health_record_data,
                'duration': chief_complaint.duration,
            }

            # Include other_complaint in the response data if present
            if other_chief_complaint:
                response_data['other_complaint'] = other_chief_complaint

            return JsonResponse(response_data)

        # If request method is not POST, return an error response
        return JsonResponse({'status': False, 'message': 'Invalid request method'})
    except Exception as e:
        # Catch any exceptions and return an error response
        return JsonResponse({'status': False, 'message': str(e)})
    
def update_chief_complaint(request, chief_complaint_id):
    if request.method == 'POST':
        try:
            # Fetch the complaint record
            chief_complaint = get_object_or_404(ClinicChiefComplaint, id=chief_complaint_id)
            
            # Parse the JSON data from the request body
            data = json.loads(request.body)            
            chief_complain_duration = data.get('chief_complain_duration')
            other_complaint = data.get('other_complaint')           

            if chief_complain_duration:
                chief_complaint.duration = chief_complain_duration
            if other_complaint:
                chief_complaint.other_complaint = other_complaint

            # Save the updated record
            chief_complaint.save()

            # Return a success response
            return JsonResponse({'status': True, 'message': 'Chief complaint updated successfully.'})
        
        except ClinicChiefComplaint.DoesNotExist:
            # Handle the case where the chief complaint record does not exist
            return JsonResponse({'status': False, 'message': 'Chief complaint not found.'})
        
        except ValueError as e:
            # Handle invalid data errors
            return JsonResponse({'status': False, 'message': f'Invalid data: {str(e)}'})
        
        except Exception as e:
            # Handle any other unexpected errors
            return JsonResponse({'status': False, 'message': f'An unexpected error occurred: {str(e)}'})

    # If not a POST request, return a method not allowed response
    return JsonResponse({'status': False, 'message': 'Invalid request method.'})
  

def fetch_existing_data(request):
    try:
        # Extract patient_id and visit_id from the request parameters
        patient_id = request.GET.get('patient_id')
        visit_id = request.GET.get('visit_id')

        # Query the database to fetch existing chief complaints based on patient_id and visit_id
        existing_data = ClinicChiefComplaint.objects.filter(patient_id=patient_id, visit_id=visit_id).values()
        
        # Create a list to hold the modified data with unified information
        modified_data = []

        # Iterate through each entry in the existing data
        for entry in existing_data:
            # Determine the information to display based on whether the health record is null or not
            display_info = None
            if entry['health_record_id'] is not None:
                try:
                    health_record = HealthRecord.objects.get(pk=entry['health_record_id'])
                    display_info = health_record.name
                except ObjectDoesNotExist:
                    # Handle the case where the HealthRecord object does not exist
                    display_info = "Unknown Health Record"
            else:
                # Use the "other complaint" field if health record is null
                display_info = entry['other_complaint'] if entry['other_complaint'] else "Unknown"
 
            # Create a modified entry with unified information under the 'health_record' key Staff.objects.get(admin=request.user.staff)
            admin = CustomUser.objects.get(id=request.user.id)
            staff = Staffs.objects.get(admin=admin)  # Tumia object ya `admin` moja kwa moja
         
            modified_entry = {
                'id': entry['id'],
                'patient_id': entry['patient_id'],
                'visit_id': entry['visit_id'],
                'data_recorder_id': entry['data_recorder_id'],
                'staff_id':staff.id,
                'health_record': display_info,
                'health_record_id': health_record.id,
                'duration': entry['duration'],
                'created_at': entry['created_at'],
                'updated_at': entry['updated_at']
            }

            # Add the modified entry to the list
            modified_data.append(modified_entry)

        # Return the modified data as a JSON response
        return JsonResponse(modified_data, safe=False)
    
    except Exception as e:
        # If an error occurs, return an error response with status code 500
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
def delete_chief_complaint(request, chief_complaint_id):
    try:
        if request.method == 'POST' and request.POST.get('_method') == 'DELETE':
            # Fetch the ChiefComplaint object to delete
            chief_complaint = get_object_or_404(ClinicChiefComplaint, id=chief_complaint_id)
            
            # Delete the ChiefComplaint
            chief_complaint.delete()
            
            # Return a success response
            return JsonResponse({'message': 'Chief complaint deleted successfully'})
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        # Return detailed error message for client-side display
        return JsonResponse({'error': f"Error: {str(e)}"}, status=500)

    
@login_required
def save_remotesconsultation_notes(request, patient_id, visit_id):
    import numpy as np
    doctor = request.user.staff
    patient = get_object_or_404(Patients, pk=patient_id)
    visit = get_object_or_404(PatientVisits, patient=patient, id=visit_id)
    patient_visits = PatientVisits.objects.filter(patient=patient)
    
    # Retrieve patient vitals and health records
    try:
        patient_vitals = PatientVital.objects.filter(patient=patient, visit=visit)
        health_records = HealthRecord.objects.all()
    except Exception:
        patient_vitals = None
        health_records = None

    # Get existing consultation note or None
    consultation_note = ConsultationNotes.objects.filter(patient=patient, visit=visit).first()
    previous_referrals = Referral.objects.filter(patient=patient_id, visit=visit)
    # Get or create provisional diagnosis record
    provisional_record, _ = PatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)
    previous_discharges = DischargesNotes.objects.filter(patient=patient_id, visit=visit)
    provisional_diagnosis_ids = provisional_record.provisional_diagnosis.values_list('id', flat=True)
    final_provisional_diagnosis= provisional_record.final_diagnosis.values_list('id', flat=True)
    # Numeric ranges for form inputs
    context = {
        'patient': patient,
        'visit': visit,
        'previous_discharges': previous_discharges,
        'previous_referrals': previous_referrals,
        'health_records': health_records,
        'patient_visits': patient_visits,
        'patient_vitals': patient_vitals,
        'final_provisional_diagnosis': final_provisional_diagnosis,
        'provisional_diagnoses': Diagnosis.objects.all(),
        'provisional_diagnosis_ids': provisional_diagnosis_ids,
        'range_51': range(51),
        'range_301': range(301),
        'range_101': range(101),
        'range_15': range(3, 16),
        'temps': np.arange(0, 510, 1) / 10,
        'consultation_note': consultation_note,
    }

    if request.method == 'POST':
        try:
            # Collect data from form submission
            history = request.POST.get('history_of_presenting_illness')
            doctor_plan = request.POST.get('doctor_plan')
            plan_note = request.POST.get('doctor_plan_note')
            ros = request.POST.get('review_of_systems')
            exam_notes = request.POST.get('physical_examination')
            allergy_summary = request.POST.get('allergy_summary')
            comorbidity_summary = request.POST.get('known_comorbidities_summary')
            provisional_ids = request.POST.getlist('provisional_diagnosis[]')

            # Save provisional diagnosis
            if not provisional_ids:
                provisional_record.data_recorder = doctor
            provisional_record.provisional_diagnosis.set(provisional_ids)
            provisional_record.save()

            # Create or update consultation note
            if consultation_note:
                consultation_note.history_of_presenting_illness = history
                consultation_note.doctor_plan = doctor_plan
                consultation_note.doctor_plan_note = plan_note
                consultation_note.review_of_systems = ros
                consultation_note.physical_examination = exam_notes
                consultation_note.allergy_summary = allergy_summary
                consultation_note.known_comorbidities_summary = comorbidity_summary
                consultation_note.save()
            else:
                # Prevent duplicate consultation for same visit
                if ConsultationNotes.objects.filter(patient=patient, visit=visit).exists():
                    messages.error(request, 'A consultation note already exists for this patient and visit.')
                    return render(request, 'doctor_template/add_consultation_notes.html', context)

               
                # Create a new consultation note
                consultation_note = ConsultationNotes.objects.create(
                    doctor=doctor,
                    patient=patient,
                    visit=visit,
                    history_of_presenting_illness=history,
                    doctor_plan=doctor_plan,
                    doctor_plan_note=plan_note,
                    review_of_systems=ros,
                    physical_examination=exam_notes,
                    allergy_summary=allergy_summary,
                    known_comorbidities_summary=comorbidity_summary
                )

            if doctor_plan == "Laboratory":
                messages.success(request, 'Consultation record saved successfully.')
                return redirect(reverse('doctor_save_laboratory', args=[patient_id, visit_id]))
            else:
                messages.success(request, 'Consultation record saved successfully.')
                return redirect(reverse('doctor_save_remotesconsultation_notes_next', args=[patient_id, visit_id]))            


        except Exception as e:
            messages.error(request, f'Error saving consultation note: {str(e)}')
            return render(request, 'doctor_template/add_consultation_notes.html', context)

    # If GET request, render form
    return render(request, 'doctor_template/add_consultation_notes.html', context)

    
@login_required
def save_remotesconsultation_notes_next(request, patient_id, visit_id):
    try:
    # Retrieve the patient and visit objects
        patient = get_object_or_404(Patients, pk=patient_id)
        visit = get_object_or_404(PatientVisits, patient=patient_id, id=visit_id)
        doctor_plan_note = ConsultationNotes.objects.filter(patient=patient_id, visit=visit).first()
        data_recorder = request.user.staff

        # Retrieve the consultation note object if it exists, otherwise create a new one
        consultation_note, created = PatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)

        # Retrieve all provisional and final diagnoses
        provisional_diagnoses = Diagnosis.objects.all()
        final_diagnoses = Diagnosis.objects.all()

        # Get the IDs of the provisional and final diagnoses associated with the consultation note
        provisional_diagnosis_ids = consultation_note.provisional_diagnosis.values_list('id', flat=True)
        final_diagnosis_ids = consultation_note.final_diagnosis.values_list('id', flat=True)

        # Retrieve the doctor plan from the query string
        if request.method == 'POST':          
            final_diagnosis = request.POST.getlist('final_diagnosis[]')
            doctor_plan = request.POST.get('doctor_plan')            
            if not consultation_note:
                consultation_note = PatientDiagnosisRecord.objects.create(patient=patient, visit=visit)
                consultation_note.data_recorder = data_recorder
            consultation_note.final_diagnosis.set(final_diagnosis)
            consultation_note.save()
            # Add success message
            messages.success(request, 'Consultation notes saved successfully.')

            # Redirect based on the doctor's plan
            if doctor_plan == 'Prescription':
                return redirect(reverse('doctor_save_prescription', args=[patient_id, visit_id]))
            elif doctor_plan == 'Laboratory':
                return redirect(reverse('doctor_save_remotesconsultation_notes',  args=[patient_id, visit_id]))
            elif doctor_plan == 'Referral':
                return redirect(reverse('doctor_save_remotereferral', args=[patient_id, visit_id]))
            elif doctor_plan == 'Counselling':
                return redirect(reverse('doctor_save_remote_counseling', args=[patient_id, visit_id]))
            elif doctor_plan == 'Procedure':
                return redirect(reverse('doctor_save_remoteprocedure', args=[patient_id, visit_id]))
            elif doctor_plan == 'Observation':
                return redirect(reverse('doctor_save_observation', args=[patient_id, visit_id]))
            elif doctor_plan == 'Discharge':
                return redirect(reverse('doctor_save_remote_discharges_notes', args=[patient_id, visit_id]))
            elif doctor_plan == 'Radiology':
                return redirect(reverse('doctor_add_radiology', args=[patient_id, visit_id]))

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    # If an exception occurs or if the request method is not POST, render the form again
    context = {
        'provisional_diagnoses': provisional_diagnoses,
        'final_diagnoses': final_diagnoses,
        'patient': patient,
        'visit': visit,
        'consultation_note': consultation_note,
        'provisional_diagnosis_ids': provisional_diagnosis_ids,
        'final_diagnosis_ids': final_diagnosis_ids,
        'doctor_plan_note': doctor_plan_note,
    }
    return render(request, 'doctor_template/add_patientprovisional_diagnosis.html', context)    
    
@login_required
def consultation_order_redirect(request, consultation_id):
    """
    This view does nothing except redirect to the remote consultation notes URL using URL name.
    """
    # Fetch the consultation order
    order = get_object_or_404(ConsultationOrder, id=consultation_id)

    # Build the redirect URL using URL name
    redirect_url = reverse(
        "doctor_save_remotesconsultation_notes", 
        args=[order.patient.id, order.visit.id]
    )

    # Redirect the user
    return redirect(redirect_url)


@login_required    
def save_counsel(request, patient_id, visit_id):
    # Retrieve patient and visit objects
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)              
    data_recorder = request.user.staff
    # Retrieve existing remote counseling record if it exists
    remote_counseling = Counseling.objects.filter(patient=patient, visit=visit).first()
    consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)  
    # Prepare context for rendering the template
    context = {
        'patient': patient, 
        'visit': visit,
        'remote_counseling': remote_counseling,
        'consultation_notes': consultation_notes,
    }
    
    # Handle form submission
    if request.method == 'POST':        
        form = CounselingForm(request.POST, instance=remote_counseling)
        
        # Check if a record already exists for the patient and visit
        if remote_counseling:
            # If a record exists, update it
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'counseling updated successfully.')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            # If no record exists, create a new one
            form.instance.patient = patient
            form.instance.data_recorder = data_recorder
            form.instance.visit = visit
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, 'counseling saved successfully.')
                except ValidationError as e:
                    messages.error(request, f'Validation Error: {e}')
            else:
                messages.error(request, 'Please correct the errors in the form.')

        # Redirect to the appropriate page after saving
        return redirect(reverse('doctor_save_remotesconsultation_notes',  args=[patient_id, visit_id]))
   
    else:
        # If it's a GET request, initialize the form with existing data (if any)
        form = CounselingForm(instance=remote_counseling)   
    # Add the form to the context
    context['form'] = form    
    return render(request, 'doctor_template/counsel_template.html', context)

@login_required    
def save_remote_discharges_notes(request, patient_id, visit_id):
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)
    consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)    
    remote_discharges_notes = DischargesNotes.objects.filter(patient=patient, visit=visit).first()  
    context = {
            'patient': patient,
            'visit': visit,
            'consultation_notes': consultation_notes,
            'remote_discharges_notes': remote_discharges_notes,         
        }
        
    try:      
        # Check if the request user is staff
        data_recorder = request.user.staff      
        # Handle form submission
        if request.method == 'POST':
            form = DischargesNotesForm(request.POST, instance=remote_discharges_notes)
            if form.is_valid():
                remote_discharges_notes = form.save(commit=False)
                remote_discharges_notes.patient = patient
                remote_discharges_notes.visit = visit
                remote_discharges_notes.data_recorder = data_recorder
                remote_discharges_notes.save()
                messages.success(request, 'discharge notes saved successfully.')
                return redirect(reverse('doctor_save_remotesconsultation_notes',  args=[patient_id, visit_id]))  # Redirect to the next view
            else:
                messages.error(request, 'Please correct the errors in the form.')
        else:
            form = DischargesNotesForm(instance=remote_discharges_notes)        
        # Prepare context for rendering the template
        context['form'] = form
        return render(request, 'doctor_template/discharge_template.html', context)    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'doctor_template/discharge_template.html', context)
        

@login_required
def save_remotereferral(request, patient_id, visit_id):
    try:
        # Retrieve patient and visit objects
        patient = get_object_or_404(Patients, id=patient_id)
        visit = get_object_or_404(PatientVisits, id=visit_id)
        data_recorder = request.user.staff
        referral = Referral.objects.filter(patient=patient, visit=visit).first()
        consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)    
        context = {'patient': patient, 'visit': visit, 'referral': referral,'consultation_notes':consultation_notes}

        if request.method == 'POST':
            form = ReferralForm(request.POST, instance=referral)
            if form.is_valid():
                try:
                    referral = form.save(commit=False)
                    referral.patient = patient
                    referral.visit = visit
                    referral.data_recorder = data_recorder
                    # Ensure source_location is set
                    if not referral.source_location:
                        referral.source_location = "Default Source Location"
                    referral.save()
                    messages.success(request, 'Referral saved successfully.')
                    return redirect(reverse('doctor_save_remotesconsultation_notes',  args=[patient_id, visit_id]))
                except Exception as e:
                    messages.error(request, f'Error saving referral: {str(e)}')
            else:
                # Add form errors to messages
                form_errors = form.errors.as_json()
                messages.error(request, f'Form validation errors: {form_errors}')               
        else:
            form = ReferralForm(instance=referral)

        context['form'] = form
        return render(request, 'doctor_template/save_remotereferral.html', context)
    except Exception as e:
        messages.error(request, f'An unexpected error occurred: {str(e)}')
        return render(request, 'doctor_template/save_remotereferral.html', context)
    
    
    
@login_required
def save_observation(request, patient_id, visit_id):
    patient = get_object_or_404(Patients, id=patient_id)
    visit = get_object_or_404(PatientVisits, id=visit_id)
    data_recorder = request.user.staff
    record_exists = ObservationRecord.objects.filter(patient_id=patient_id, visit_id=visit_id).first()
    consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)    
    context = {'patient': patient, 
               'visit': visit, 
               'consultation_notes': consultation_notes, 
               'record_exists': record_exists
               }
    if request.method == 'POST':
        form = ObservationRecordForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['observation_notes']
            try:
                if record_exists:
                    # If a record exists, update it
                    observation_record = ObservationRecord.objects.get(patient_id=patient_id, visit_id=visit_id)
                    observation_record.observation_notes = description
                    observation_record.data_recorder = data_recorder
                    observation_record.save()
                    messages.success(request, 'observation record updated successfully.')
                else:
                    # If no record exists, create a new one
                    ObservationRecord.objects.create(
                        patient=patient,
                        visit=visit,
                        data_recorder=data_recorder,
                        observation_notes=description,
                    )
                    messages.success(request, 'observation record saved successfully.')
                return redirect(reverse('doctor_save_remotesconsultation_notes',  args=[patient_id, visit_id]))
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please fill out all required fields.')
    else:
        form = ObservationRecordForm(initial={'observation_notes': record_exists.observation_notes if record_exists else ''})

    context['form'] = form
    return render(request, 'doctor_template/observation_template.html', context)    

@login_required
def save_remoteprocedure(request, patient_id, visit_id):
    try:
        # Get patient and visit objects early
        try:
            patient = Patients.objects.get(id=patient_id)
        except Patients.DoesNotExist:
            return render(request, '404.html', {'error_message': "Patient not found."})

        try:
            visit = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)
        except PatientVisits.DoesNotExist:
            return render(request, '404.html', {'error_message': "Visit not found."})

        # Fetch related data
        prescriptions = Prescription.objects.filter(patient=patient, visit=visit)
        previous_procedures = Procedure.objects.filter(patient=patient, visit=visit)
        consultation_note = ConsultationNotes.objects.filter(patient=patient, visit=visit).first()
        
        provisional_record, _ = PatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)
        final_provisional_diagnosis = provisional_record.final_diagnosis.values_list('id', flat=True)

        procedures = Procedure.objects.filter(patient=patient, visit=visit)
        total_price = sum(p.total_price for p in prescriptions)

        # Fetch procedure services based on payment form
        if patient.payment_form == 'insurance':
            remote_service = Service.objects.filter(
                Q(type_service='procedure') & Q(coverage='insurance')
            )
        else:
            remote_service = Service.objects.filter(type_service='procedure')

        # Calculate total cost of procedures
        total_procedure_cost = procedures.aggregate(Sum('cost'))['cost__sum'] or 0

        return render(request, 'doctor_template/procedure_template.html', {
            'visit': visit,
            'patient': patient,
            'prescriptions': prescriptions,
            'total_price': total_price,
            'previous_procedures': previous_procedures,
            'final_provisional_diagnosis': final_provisional_diagnosis,
            'consultation_note': consultation_note,
            'procedures': procedures,
            'remote_service': remote_service,
            'total_procedure_cost': total_procedure_cost,
        })

    except Exception as e:
        return render(request, '404.html', {'error_message': f"Oop's sorry we can't find that page! ({str(e)})"})
    
@csrf_exempt    
def get_patient_details(request, patient_id):
    try:
        patient = Patients.objects.get(id=patient_id)
        # Fetching services based on coverage and type
        if patient.payment_form == 'insurance':
            # If patient's payment form is insurance, fetch services with matching coverage
            remote_service = Service.objects.filter(
                type_service='procedure',
                coverage=patient.payment_form
            ).values('id', 'name')
        else:
            # If payment form is cash, fetch all services of type procedure
            remote_service = Service.objects.filter(
                type_service='procedure'
            ).values('id', 'name')        
        return JsonResponse({'success': True, 'patient': patient, 'remote_service': list(remote_service)})
    except Patients.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Patient not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@csrf_exempt
def get_procedure_cost(request):
    if request.method == 'POST':  # Change to POST method
        procedure_id = request.POST.get('procedure_id')
        patient_id = request.POST.get('patient_id')  # Receive patient ID        
        try:
            procedure = Service.objects.get(id=procedure_id)            
            # Get the patient
            patient = Patients.objects.get(id=patient_id)            
            # Check the patient's payment form
            payment_form = patient.payment_form            
            # Initialize cost variable
            cost = None            
            # If payment form is cash, fetch cash cost
            if payment_form == 'Cash':
                cost = procedure.cash_cost
            elif payment_form == 'Insurance':
                # Check if insurance company name is NHIF
                if patient.insurance_name == 'NHIF':
                    cost = procedure.nhif_cost
                else:
                    cost = procedure.insurance_cost
            
            if cost is not None:
                return JsonResponse({'cost': cost})
            else:
                return JsonResponse({'error': 'Cost not available for this payment form'}, status=404)
        
        except Service.DoesNotExist:
            return JsonResponse({'error': 'Procedure not found'}, status=404)
        except Patients.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required    
def add_procedure(request):
    if request.method == 'POST':
        procedures_data = zip(
            request.POST.getlist('procedure_name[]'),
            request.POST.getlist('description[]'),
            request.POST.getlist('equipments_used[]'),
            request.POST.getlist('cost[]')
        )
        created_procedures = []

        for name_id, description, equipments_used, cost in procedures_data:
            try:
                # Extract patient and visit objects
                patient_id = request.POST.get('patient_id')
                visit_id = request.POST.get('visit_id')
                orderDate = request.POST.get('order_date')
                patient = get_object_or_404(Patients, id=patient_id)
                visit = get_object_or_404(PatientVisits, id=visit_id)
                
                # Retrieve the current user as the doctor
                doctor = request.user.staff

                # Create and save the new Procedure instance
                procedure = Procedure.objects.create(
                    patient=patient,
                    visit=visit,
                    doctor=doctor,
                    data_recorder=doctor,
                    order_date=orderDate,
                    name_id=name_id,
                    description=description,
                    equipments_used=equipments_used,
                    cost=cost
                )
                created_procedures.append({
                    'id': procedure.id,
                    'name': procedure.name.name,
                    'description': procedure.description,
                    'equipments_used': procedure.equipments_used,
                    'cost': procedure.cost,
                })
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
        return JsonResponse({'status': 'success', 'message': 'Procedures added successfully', 'created_procedures': created_procedures})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
            


@csrf_exempt
@require_POST
def add_remoteprescription(request):
    try:
        with transaction.atomic():
            # ----------------- Extract data -----------------
            patient_id = request.POST.get('patient_id')
            visit_id = request.POST.get('visit_id')
            medicines = request.POST.getlist('medicine[]')
            formulations = request.POST.getlist('formulation[]')
            dosages = request.POST.getlist('dosage[]')
            frequencies = request.POST.getlist('frequency[]')
            durations = request.POST.getlist('duration[]')
            quantities = request.POST.getlist('quantity[]')
            routes = request.POST.getlist('route[]')
            total_prices = request.POST.getlist('total_price[]')
            entered_by = getattr(request.user, "staff", None)

            # ----------------- Validation: Patient & Visit -----------------
            if not all([patient_id, visit_id]):
                return JsonResponse({'status': 'error', 'message': 'Patient and visit information are required.'})

            try:
                patient = Patients.objects.get(id=patient_id)
                visit = PatientVisits.objects.get(id=visit_id)
            except (Patients.DoesNotExist, PatientVisits.DoesNotExist):
                return JsonResponse({'status': 'error', 'message': 'Invalid patient or visit information.'})

            # ----------------- Business Rule: Prevent adding after payment -----------------
            existing_status = Prescription.get_visit_status(visit)
            if existing_status.get("status") == "paid":
                return JsonResponse({
                    'status': 'error',
                    'message': 'This visit is already fully paid. No additional prescriptions can be added.'
                })

            # ----------------- Validation: At least one medicine -----------------
            if not medicines:
                return JsonResponse({'status': 'error', 'message': 'At least one medicine is required.'})

            prescriptions_to_create = []
            today = timezone.now().date()

            # ----------------- Loop through all medicines -----------------
            for i in range(len(medicines)):
                # Get medicine
                try:
                    medicine = Medicine.objects.get(id=medicines[i])
                except Medicine.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': f'Medicine at position {i+1} does not exist.'})

                # Check if expired
                if medicine.expiration_date and medicine.expiration_date < today:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'{medicine.drug_name} is expired (Expiry: {medicine.expiration_date}).'
                    })

                # Validate quantity
                quantity_used_str = quantities[i]
                if not quantity_used_str:
                    return JsonResponse({'status': 'error', 'message': f'Quantity required for {medicine.drug_name}.'})

                try:
                    quantity_used = int(quantity_used_str)
                except ValueError:
                    return JsonResponse({'status': 'error', 'message': f'Invalid quantity for {medicine.drug_name}.'})

                if quantity_used <= 0:
                    return JsonResponse({'status': 'error', 'message': f'Quantity must be greater than zero for {medicine.drug_name}.'})

                if medicine.remain_quantity is not None and quantity_used > medicine.remain_quantity:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Insufficient stock for {medicine.drug_name}. Only {medicine.remain_quantity} available.'
                    })

                # Get dosage object (optional)
                try:
                    dosage_obj = MedicineDosage.objects.get(id=dosages[i]) if dosages[i] else None
                except MedicineDosage.DoesNotExist:
                    dosage_obj = None

                # Get frequency object (required)
                try:
                    frequency_obj = PrescriptionFrequency.objects.get(id=frequencies[i])
                except PrescriptionFrequency.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': f'Invalid frequency for {medicine.drug_name}.'})

                # Get route object (optional)
                route_obj = None
                if routes and i < len(routes) and routes[i]:
                    try:
                        route_obj = MedicineRoute.objects.get(id=routes[i])
                    except MedicineRoute.DoesNotExist:
                        route_obj = None

                # ----------------- Create prescription object -----------------
                prescription = Prescription(
                    patient=patient,
                    visit=visit,
                    medicine=medicine,
                    entered_by=entered_by,
                    formulation_dose=formulations[i],
                    dosage=dosage_obj.dosage_value if dosage_obj else None,
                    frequency=frequency_obj,
                    duration=durations[i],
                    quantity_used=quantity_used,
                    total_price=total_prices[i] if total_prices and i < len(total_prices) else None,
                    route=route_obj.name if route_obj else None,

                    # Default statuses
                    verified="not_verified",
                    issued="not_issued",
                    status="unpaid",
                )
                prescriptions_to_create.append(prescription)

            # ----------------- Save all prescriptions -----------------
            for prescription in prescriptions_to_create:
                prescription.save()

            return JsonResponse({'status': 'success', 'message': 'Prescription saved successfully. Inventory will be deducted upon payment.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'})
    
    
@login_required
def save_prescription(request, patient_id, visit_id):
    try:
        # Get patient and visit objects first
        try:
            patient = Patients.objects.get(id=patient_id)
        except Patients.DoesNotExist:
            return render(request, '404.html', {'error_message': "Patient not found."})

        try:
            visit = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)
        except PatientVisits.DoesNotExist:
            return render(request, '404.html', {'error_message': "Visit not found."})

        # Check if prescriptions already exist and their status
        prescriptions = Prescription.objects.filter(patient=patient, visit=visit)
        can_add_prescriptions = True
        restriction_reason = ""
        
        if prescriptions.exists():
            status_info = Prescription.get_visit_status(visit)
            
            # Check if any prescription is verified, issued, or paid
            if status_info["verified"] != "not_verified":
                can_add_prescriptions = False
                restriction_reason = "Prescriptions have already been verified."
            elif status_info["issued"] != "not_issued":
                can_add_prescriptions = False
                restriction_reason = "Medications have already been issued."
            elif status_info["status"] != "unpaid":
                can_add_prescriptions = False
                restriction_reason = "Prescriptions have already been paid for."

        # Retrieve related data
        frequencies = PrescriptionFrequency.objects.all()

        provisional_record, _ = PatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)
        consultation_note = ConsultationNotes.objects.filter(patient=patient, visit=visit).first()
        final_provisional_diagnosis = provisional_record.final_diagnosis.values_list('id', flat=True)

        current_date = timezone.now().date()
        total_price = sum(p.total_price for p in prescriptions)

        medicines = Medicine.objects.filter(
            remain_quantity__gt=0,
            expiration_date__gt=current_date
        ).distinct()

        range_31 = range(31)

        return render(request, 'doctor_template/prescription_template.html', {
            'patient': patient,
            'visit': visit,
            'final_provisional_diagnosis': final_provisional_diagnosis,
            'consultation_note': consultation_note,
            'medicines': medicines,
            'total_price': total_price,
            'range_31': range_31,
            'prescriptions': prescriptions,
            'frequencies': frequencies,
            'can_add_prescriptions': can_add_prescriptions,
            'restriction_reason': restriction_reason,
        })

    except Exception as e:
        return render(request, '404.html', {
            'error_message': f"Oop's sorry we can't find that page! ({str(e)})"
        })
    

@require_POST
@csrf_exempt
def get_unit_price(request):
    medicine_id = request.POST.get('medicine_id')
    patient_id = request.POST.get('patient_id')

    if not medicine_id or not patient_id:
        return JsonResponse({'error': 'Medicine ID and Patient ID are required'}, status=400)

    try:
        patient = Patients.objects.get(id=patient_id)
        medicine = Medicine.objects.get(pk=medicine_id)
    except Patients.DoesNotExist:
        return JsonResponse({'error': 'Patient not found'}, status=404)
    except Medicine.DoesNotExist:
        return JsonResponse({'error': 'Medicine not found'}, status=404)

    unit_price = None

    if patient.payment_form == 'Cash':
        unit_price = medicine.cash_cost
    elif patient.payment_form == 'Insurance':
        if patient.insurance_name == 'NHIF':
            unit_price = medicine.nhif_cost
        else:
            unit_price = medicine.insurance_cost

    if unit_price is not None:
        return JsonResponse({'unit_price': unit_price})
    else:
        return JsonResponse({'error': 'Cost not available for this payment form'}, status=404)
    
    

        

# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
def add_radiology(request, patient_id, visit_id):
    try:    
        try:
            visit = PatientVisits.objects.get(id=visit_id, patient_id=patient_id)
        except PatientVisits.DoesNotExist:
            visit = None
       
        doctors=Staffs.objects.filter(role='doctor', work_place = 'resa')
        patient = Patients.objects.get(id=patient_id)
        consultation_notes = PatientDiagnosisRecord.objects.filter(patient=patient_id, visit=visit_id)
        radiology_record = ImagingRecord.objects.filter(patient=patient_id, visit=visit_id)
        consultation_note = ConsultationNotes.objects.filter(patient=patient, visit=visit).first()
        provisional_record, _ = PatientDiagnosisRecord.objects.get_or_create(patient=patient, visit=visit)     
        final_provisional_diagnosis= provisional_record.final_diagnosis.values_list('id', flat=True)
        # Fetching services based on coverage and type
        if patient.payment_form == 'insurance':
            # If patient's payment form is insurance, fetch services with matching coverage
            remote_service = Service.objects.filter(
                Q(type_service='Imaging') & Q(coverage=patient.payment_form)
            )
        else:
            # If payment form is cash, fetch all services of type procedure
            remote_service = Service.objects.filter(type_service='Imaging')
       
        return render(request, 'doctor_template/add_radiology.html', {
            'visit': visit,
            'patient': patient,
            'radiology_record': radiology_record,          
            'final_provisional_diagnosis': final_provisional_diagnosis,          
            'doctors': doctors,          
            'consultation_note': consultation_note,          
            'consultation_notes': consultation_notes,          
            'remote_service': remote_service,
        
        })
    except Exception as e:
        # Handle other exceptions if necessary
        return render(request, '404.html', {'error_message': str(e)})
        

@login_required
@csrf_exempt
def add_imaging(request):
    if request.method == 'POST':
        try:
            # Assuming your form fields are named appropriately in your template
            patient_id = request.POST.get('patient_id')
            doctor = request.user.staff
            visit_id = request.POST.get('visit_id')
            imaging_names = request.POST.getlist('imaging_name[]')
            descriptions = request.POST.getlist('description[]')            
            costs = request.POST.getlist('cost[]')
            order_date = request.POST.get('order_date')

            # Loop through the submitted data and create ImagingRecord objects
            for i in range(len(imaging_names)):
                imaging_record = ImagingRecord.objects.create(
                    patient_id=patient_id,
                    visit_id=visit_id,
                    order_date=order_date,
                    doctor=doctor,
                    data_recorder=doctor,
                    imaging_id=imaging_names[i],
                    description=descriptions[i],                 
                    cost=costs[i],
                    # Set other fields as needed
                )
                # Save the imaging record to the database
                imaging_record.save()

            # Assuming the imaging records were successfully saved
            return JsonResponse({'status': 'success', 'message': 'Imaging records saved successfully'})
        except IntegrityError as e:
            # Handle integrity errors, such as unique constraint violations
            return JsonResponse({'status': 'error', 'message': 'Integrity error occurred: ' + str(e)})
        except Exception as e:
            # Handle other unexpected errors
            return JsonResponse({'status': 'error', 'message': 'An error occurred: ' + str(e)})
    else:
        # If the request method is not POST, return an error response
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def save_laboratory(request, patient_id, visit_id):
    try:
        doctor = request.user.staff

        # Get patient and visit objects
        patient = get_object_or_404(Patients, id=patient_id)
        visit = get_object_or_404(PatientVisits, id=visit_id, patient_id=patient_id)

        # Fetch lab investigations for this visit
        investigations = LaboratoryOrder.objects.filter(patient_id=patient_id, visit_id=visit_id)

        # Fetch consultation notes for this visit
        consultation_note = ConsultationNotes.objects.filter(patient=patient, visit=visit).first()

        # Get available lab technicians
        lab_technicians = Staffs.objects.filter(role='labTechnician', work_place="resa")

        # Filter laboratory services based on payment form
        if patient.payment_form == 'insurance':
            remote_service = Service.objects.filter(
                type_service='Laboratory',
                coverage=patient.payment_form
            )
        else:
            remote_service = Service.objects.filter(type_service='Laboratory')

        # Calculate total lab cost
        total_lab_cost = investigations.aggregate(total=Sum('cost'))['total']

        context = {
            'visit': visit,
            'patient': patient,
            'Investigation': investigations,
            'previous_results': investigations,
            'doctors': lab_technicians,
            'remote_service': remote_service,
            'total_imaging_cost': total_lab_cost,
            'consultation_note': consultation_note,
        }

        return render(request, 'doctor_template/laboratory_template.html', context)

    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}) 
    
@csrf_exempt
def add_investigation(request):
    if request.method == 'POST':
        try:
            # Assuming your form fields are named appropriately in your template
            patient_id = request.POST.get('patient_id')
            doctor = request.user.staff
            visit_id = request.POST.get('visit_id')
            investigation_names = request.POST.getlist('investigation_name[]')
            descriptions = request.POST.getlist('description[]')            
            costs = request.POST.getlist('cost[]')
            order_date = request.POST.get('order_date')
            doctor_id = request.POST.get('doctor_id')

            # Loop through the submitted data and create LaboratoryOrder objects
            for i in range(len(investigation_names)):
                investigation_record = LaboratoryOrder.objects.create(
                    patient_id=patient_id,
                    doctor_id=doctor_id,
                    visit_id=visit_id,
                    order_date=order_date,                 
                    data_recorder=doctor,
                    lab_test_id=investigation_names[i],
                    description=descriptions[i],                 
                    cost=costs[i],
                    # Set other fields as needed
                )
                # Save the LaboratoryOrder record to the database
                investigation_record.save()

            # Assuming the LaboratoryOrder records were successfully saved
            return JsonResponse({'status': 'success', 'message': 'Laboratory records saved successfully'})
        except IntegrityError as e:
            # Handle integrity errors, such as unique constraint violations
            return JsonResponse({'status': 'error', 'message': 'Integrity error occurred: ' + str(e)})
        except Exception as e:
            # Handle other unexpected errors
            return JsonResponse({'status': 'error', 'message': 'An error occurred: ' + str(e)})
    else:
        # If the request method is not POST, return an error response
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}) 
    

@login_required
def patient_visit_history_view(request, patient_id):
    # Retrieve visit history for the specified patient
    visits = PatientVisits.objects.filter(patient_id=patient_id) 
    patient = Patients.objects.get(id=patient_id)
    return render(request, 'doctor_template/manage_patient_visit_history.html', {
        'visits': visits,
        'patient':patient,     
        })
    


@login_required
def consultation_notes_view(request):
    # Get all patients who have consultation notes
    patient_records = Patients.objects.filter(
        consultationnotes__isnull=False
    ).distinct().order_by('-consultationnotes__updated_at')

    return render(request, 'doctor_template/manage_consultation_notes.html', {
        'patient_records': patient_records
    })


@login_required
def new_consultation_order(request):
    # Get today's date
    today = timezone.now().date()

    # Filter consultation orders for today
    today_orders = ConsultationOrder.objects.filter(order_date=today).select_related('patient')

    # Get unique patients from today's consultation orders
    patients = Patients.objects.filter(id__in=today_orders.values_list('patient_id', flat=True)).distinct()

    return render(request, 'doctor_template/new_consultation_order.html', {
        'orders': today_orders,
        'patient_records': patients
    })




@login_required
def radiology_order(request):
    # Get all imaging records
    imaging_records = ImagingRecord.objects.all().order_by('-created_at')
   
    # Group records by patient, visit, doctor, and date (without time)
    grouped_records = {}
    
    for record in imaging_records:
        # Create a unique key for grouping
        key = (
            record.patient_id,
            record.visit_id if record.visit else 0,
            record.doctor_id if record.doctor else 0,
            record.order_date if record.order_date else record.created_at.date()
        )
        
        if key not in grouped_records:
            grouped_records[key] = {
                'patient': record.patient,
                'visit': record.visit,
                'doctor': record.doctor,
                'date': record.order_date if record.order_date else record.created_at.date(),
                'records': [],
                'latest_date': record.created_at
            }
        
        grouped_records[key]['records'].append(record)
        
        # Update the latest date if this record is newer
        if record.created_at > grouped_records[key]['latest_date']:
            grouped_records[key]['latest_date'] = record.created_at
    
    # Convert to list for template
    imaging_groups = list(grouped_records.values())
    
    context = {
        'imaging_records': imaging_records,
        'imaging_groups': imaging_groups,
    }
    
    return render(request, 'doctor_template/manage_radiology.html', context)


@login_required
def new_radiology_order(request):
    # Get today's date
    today = timezone.now().date()
    
    # Get the current doctor (staff member)
    try:
        current_doctor = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        current_doctor = None
    
    # Get today's radiology records for the current doctor
    if current_doctor:
        today_radiology_records = ImagingRecord.objects.filter(
            Q(doctor=current_doctor) & 
            (Q(order_date=today) | Q(created_at__date=today))
        ).select_related(
            'patient', 'visit', 'doctor', 'doctor__admin', 'imaging'
        ).order_by('-created_at')
        
        # Group radiology records by patient, visit, doctor, and date
        grouped_radiology = {}
        for record in today_radiology_records:
            # Use order_date if available, otherwise use created_at date
            record_date = record.order_date if record.order_date else record.created_at.date()
            
            key = (
                record.patient.id, 
                record.visit.id if record.visit else None, 
                record.doctor.id,
                record_date
            )
            
            if key not in grouped_radiology:
                grouped_radiology[key] = {
                    'patient': record.patient,
                    'visit': record.visit,
                    'doctor': record.doctor,
                    'date': record_date,
                    'records': [],
                    'latest_date': record.created_at
                }
            
            grouped_radiology[key]['records'].append(record)
            
            # Update the latest date if this record is newer
            if record.created_at > grouped_radiology[key]['latest_date']:
                grouped_radiology[key]['latest_date'] = record.created_at
        
        # Convert to list for template
        radiology_groups = list(grouped_radiology.values())
    else:
        radiology_groups = []
    
    context = {
        'radiology_groups': radiology_groups,
        'today_radiology_count': sum(len(group['records']) for group in radiology_groups)
    }
    
    return render(request, 'doctor_template/new_radiology_order.html', context)


    
@login_required
def patient_procedure_view(request):
    # Group procedures by patient, visit, doctor, and date
    procedure_groups = []
    
    # Get all procedures with related data
    procedures = Procedure.objects.select_related(
        'patient', 'visit', 'doctor', 'doctor__admin', 'name'
    ).order_by('-created_at')
    
    # Create a dictionary to group procedures
    groups_dict = {}
    
    for procedure in procedures:
        # Create a unique key for grouping
        key = (
            procedure.patient_id, 
            procedure.visit_id if procedure.visit else 0, 
            procedure.doctor_id,
            procedure.created_at.date()  # Group by date only (not time)
        )
        
        if key not in groups_dict:
            groups_dict[key] = {
                'patient': procedure.patient,
                'visit': procedure.visit,
                'doctor': procedure.doctor,
                'date': procedure.created_at.date(),
                'latest_date': procedure.created_at,
                'procedures': []
            }
        else:
            # Update the latest date if this procedure is more recent
            if procedure.created_at > groups_dict[key]['latest_date']:
                groups_dict[key]['latest_date'] = procedure.created_at
        
        # Add procedure to the group
        groups_dict[key]['procedures'].append(procedure)
    
    # Convert dictionary to list
    procedure_groups = list(groups_dict.values())
    
    # Sort groups by latest date
    procedure_groups.sort(key=lambda x: x['latest_date'], reverse=True)
    
    # Calculate summary statistics
    total_procedures_count = sum(len(group['procedures']) for group in procedure_groups)
    unique_patients_count = len(set(group['patient'].id for group in procedure_groups))
    unique_doctors_count = len(set(group['doctor'].id for group in procedure_groups))
    
    context = {
        'procedure_groups': procedure_groups,
        'total_procedures_count': total_procedures_count,
        'unique_patients_count': unique_patients_count,
        'unique_doctors_count': unique_doctors_count,
    }
    
    return render(request, 'doctor_template/manage_procedure.html', context)
    




@login_required
def edit_procedure_result(request, procedure_id):
    # Get the procedure
    procedure = get_object_or_404(Procedure, id=procedure_id)

    # From the procedure we can access patient and visit directly
    patient = procedure.patient
    visit = procedure.visit

    # Prepare context for rendering the template
    context = {
        'patient': patient,
        'visit': visit,
        'procedure': procedure,
    }

    if request.method == 'POST':
        form = ProcedureForm(request.POST, instance=procedure)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Procedure result updated successfully.')
            except ValidationError as e:
                messages.error(request, f'Validation Error: {e}')
        else:
            messages.error(request, 'Please correct the errors in the form.')

        # Redirect after saving
        return redirect(reverse('doctor_patient_procedure_view'))

    else:
        form = ProcedureForm(instance=procedure)

    context['form'] = form
    return render(request, 'doctor_template/edit_procedure_result.html', context)


@login_required
def edit_radiology_result(request, radiology_id):
    # Get the imaging record
    imaging_record = get_object_or_404(ImagingRecord, id=radiology_id)

    # Access related patient and visit directly
    patient = imaging_record.patient
    visit = imaging_record.visit

    # Prepare context for rendering
    context = {
        'patient': patient,
        'visit': visit,
        'imaging_record': imaging_record,
    }

    if request.method == 'POST':
        form = ImagingRecordForm(request.POST, request.FILES, instance=imaging_record)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Radiology result updated successfully.')
            except ValidationError as e:
                messages.error(request, f'Validation Error: {e}')
        else:
            messages.error(request, 'Please correct the errors in the form.')

        # Redirect after saving
        return redirect(reverse('doctor_radiology_order'))

    else:
        form = ImagingRecordForm(instance=imaging_record)

    context['form'] = form
    return render(request, 'doctor_template/edit_radiology_result.html', context)



@login_required
def patient_laboratory_view(request):
    # Get distinct (patient, visit) combinations with latest result date
    distinct_lab_sets = (
        LaboratoryOrder.objects
        .values('patient_id', 'visit_id')
        .annotate(latest_date=Max('created_at'))
        .order_by('-latest_date')
    )

    patient_lab_data = []

    for entry in distinct_lab_sets:
        patient_id = entry['patient_id']
        visit_id = entry['visit_id']
        latest_date = entry['latest_date']

        lab_tests = LaboratoryOrder.objects.filter(
            patient_id=patient_id,
            visit_id=visit_id
        ).select_related('patient', 'visit', 'data_recorder__admin')

        if lab_tests.exists():
            first_lab = lab_tests.first()
            patient_lab_data.append({
                'patient': first_lab.patient,
                'visit': first_lab.visit,
                'latest_date': latest_date,
                'lab_done_by': first_lab.data_recorder,
                'lab_tests': lab_tests
            })

    context = {
        'patient_labs': patient_lab_data,
    }

    return render(request, 'doctor_template/lab_order_result.html', context)


@login_required
def new_procedure_order(request):
    # Get today's date
    today = timezone.now().date()
    
    # Get the current doctor (staff member)
    try:
        current_doctor = Staffs.objects.get(admin=request.user)
    except Staffs.DoesNotExist:
        current_doctor = None
    
    # Get today's procedures for the current doctor
    if current_doctor:
        today_procedures = Procedure.objects.filter(
            Q(doctor=current_doctor) & 
            (Q(order_date=today) | Q(created_at__date=today))
        ).select_related(
            'patient', 'visit', 'doctor', 'doctor__admin', 'name'
        ).order_by('-created_at')
        
        # Group procedures by patient, visit, doctor, and date
        grouped_procedures = {}
        for procedure in today_procedures:
            # Use order_date if available, otherwise use created_at date
            proc_date = procedure.order_date if procedure.order_date else procedure.created_at.date()
            
            key = (
                procedure.patient.id, 
                procedure.visit.id if procedure.visit else None, 
                procedure.doctor.id,
                proc_date
            )
            
            if key not in grouped_procedures:
                grouped_procedures[key] = {
                    'patient': procedure.patient,
                    'visit': procedure.visit,
                    'doctor': procedure.doctor,
                    'date': proc_date,
                    'procedures': [],
                    'latest_date': procedure.created_at
                }
            
            grouped_procedures[key]['procedures'].append(procedure)
            
            # Update the latest date if this procedure is newer
            if procedure.created_at > grouped_procedures[key]['latest_date']:
                grouped_procedures[key]['latest_date'] = procedure.created_at
        
        # Convert to list for template
        procedure_groups = list(grouped_procedures.values())
    else:
        procedure_groups = []
    
    context = {
        'procedure_groups': procedure_groups,
        'today_procedures_count': sum(len(group['procedures']) for group in procedure_groups)
    }
    
    return render(request, 'doctor_template/new_procedure_order.html', context)





def counseling_list_view(request):
    counselings = Counseling.objects.all().order_by('-created_at')
    return render(request, 'doctor_template/manage_counselling.html', {'counselings': counselings})    

def observation_record_list_view(request):
    observation_records = ObservationRecord.objects.all().order_by('-created_at')
    return render(request, 'doctor_template/manage_observation_record.html', {'observation_records': observation_records})



@login_required
def employee_detail(request):
    try:
        # Get the logged-in staff member
        staff_member = request.user.staff        
        # Get the employee record for the logged-in staff member
        employee = get_object_or_404(Employee, name=staff_member)       
        # Fetch the related employee deductions and salary change records
        employee_deductions = EmployeeDeduction.objects.filter(employee=employee)
        salary_change_records = SalaryChangeRecord.objects.filter(employee=employee)

        # Context data to pass to the template
        context = {
            'staff_member': staff_member,
            'employee': employee,
            'employee_deductions': employee_deductions,
            'salary_change_records': salary_change_records,
        }
    except Staffs.DoesNotExist:
        context = {
            'error': "Staff member not found."
        }
    except Employee.DoesNotExist:
        context = {
            'error': "Employee record not found."
        }
    except Exception as e:
        context = {
            'error': str(e)
        }
    
    return render(request, 'doctor_template/employee_detail.html', context)

