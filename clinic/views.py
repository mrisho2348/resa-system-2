
from datetime import datetime
from django.shortcuts import redirect, render
from django.contrib.auth import logout, login
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from clinic.emailBackEnd import EmailBackend
from clinic.forms import AddStaffForm
from clinic.models import ContactDetails, CustomUser, Staffs
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings

# Create your views here.
def index(request):
    return render(request,"index.html")

def RESAPortal(request):
    """RESA Portal login view for all apps (clinic, kahamahmis, pembahmis)"""
    return render(request, 'resa_portal.html')

def RESAPortalLogin(request):
    """RESA Portal login processing for all apps"""
    if request.method != "POST":
        return HttpResponseRedirect(reverse("resa_portal"))
    else:
        user = EmailBackend.authenticate(request, request.POST.get("email"), request.POST.get("password"))
        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is not active. Please contact the administrator for support.")
                return HttpResponseRedirect(reverse("resa_portal"))

            login(request, user)
            if user.user_type == "1":
                # Admin users - redirect based on workplace
                try:
                    staff = Staffs.objects.get(admin=user)
                    if staff.work_place == 'kahama':
                        return HttpResponseRedirect(reverse("kahama_admin_dashboard"))
                    elif staff.work_place == 'pemba':
                        return HttpResponseRedirect(reverse("pemba_admin_dashboard"))
                    else:
                        # Default to resa admin dashboard
                        return HttpResponseRedirect(reverse("resa_admin_dashboard"))
                except Staffs.DoesNotExist:
                    # If no staff record, redirect to resa admin dashboard
                    return HttpResponseRedirect(reverse("resa_admin_dashboard"))
                    
            elif user.user_type == "2":
                # Staff users - redirect based on workplace and role
                try:
                    staff = Staffs.objects.get(admin=user)
                    role = staff.role.lower()
                    
                    if staff.work_place == 'resa':
                        # Resa clinic staff
                        if role == "doctor":
                            return redirect("doctor_dashboard")
                        elif role == "nurse":
                            return redirect("receptionist_dashboard")
                        elif role == "admin":
                            return redirect("resa_admin_dashboard")
                        elif role == "physiotherapist":
                            return redirect("physiotherapist_dashboard")
                        elif role == "labtechnician":
                            return redirect("labtechnician_dashboard")
                        elif role == "pharmacist":
                            return redirect("pharmacist_dashboard")
                        elif role == "receptionist":
                            return redirect("receptionist_dashboard")
                        else:
                            messages.error(request, f"Role '{role}' is not recognized for this workplace.")
                            return HttpResponseRedirect(reverse("resa_portal"))
                            
                    elif staff.work_place == 'kahama':
                        # Kahama clinic staff
                        if role == "doctor":
                            return HttpResponseRedirect(reverse("kahama_doctor_dashboard"))
                        elif role == "admin":
                            return HttpResponseRedirect(reverse("kahama_admin_dashboard"))
                        else:
                            messages.error(request, f"Role '{role}' is not available for Kahama clinic.")
                            return HttpResponseRedirect(reverse("resa_portal"))
                            
                    elif staff.work_place == 'pemba':
                        # Pemba clinic staff
                        if role == "doctor":
                            return HttpResponseRedirect(reverse("pemba_doctor_dashboard"))
                        elif role == "admin":
                            return HttpResponseRedirect(reverse("pemba_admin_dashboard"))
                        else:
                            messages.error(request, f"Role '{role}' is not available for Pemba clinic.")
                            return HttpResponseRedirect(reverse("resa_portal"))
                    else:
                        messages.error(request, "You are not assigned to any workplace. Please contact the administrator.")
                        return HttpResponseRedirect(reverse("resa_portal"))
                        
                except Staffs.DoesNotExist:
                    messages.error(request, "Staff profile not found. Please contact the administrator.")
                    return HttpResponseRedirect(reverse("resa_portal"))
            else:
                messages.error(request, "Invalid user type.")
                return HttpResponseRedirect(reverse("resa_portal"))
        else:
            messages.error(request, "Invalid Login Details")
            return HttpResponseRedirect(reverse("resa_portal"))

def forgot_password(request):
    """Forgot password view"""
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = CustomUser.objects.get(email=email)
            if user.is_active:
                # Generate password reset token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Create reset link
                reset_url = request.build_absolute_uri(
                    reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                
                # Render HTML email
                context = {
                    'user': user,
                    'reset_url': reset_url,
                }
                html_message = render_to_string('password_reset_email.html', context)
                plain_message = strip_tags(html_message)
                
                send_mail(
                    "RESA Medical Group - Password Reset",
                    plain_message,
                    settings.EMAIL_HOST_USER,
                    [email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                return redirect('password_reset_done')
            else:
                messages.error(request, "This account is not active.")
        except CustomUser.DoesNotExist:
            messages.error(request, "No user found with this email address.")
    
    return render(request, 'forgot_password.html')


def password_reset_confirm(request, uidb64, token):
    """Password reset confirmation view"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            
            if password1 and password2:
                if password1 == password2:
                    user.set_password(password1)
                    user.save()
                    messages.success(request, "Your password has been reset successfully. You can now login with your new password.")
                    return redirect('resa_portal')
                else:
                    messages.error(request, "Passwords do not match.")
            else:
                messages.error(request, "Please fill in all fields.")
        
        return render(request, 'password_reset_confirm.html')
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect('resa_portal')

def GetUserDetails(request):
    user = request.user
    if user.is_authenticated:
        return HttpResponse("User : "+user.email+" usertype : " + user.usertype)
    else:
        return HttpResponse("Please login first")   
  
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse("clinic:home"))
    
class ContactFormView(SuccessMessageMixin, FormView):
    template_name = 'contact_form.html'
    form_class = AddStaffForm
    success_url = '/success/'  # Set the URL where users should be redirected on success
    success_message = "Your message was submitted successfully. We'll get back to you soon."

    def form_valid(self, form):
        # Get form data
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']
        
        # Create ContactDetails object
        contact = ContactDetails(
            first_name=first_name,
            last_name=last_name,
            email=email,
            message=message
        )
        contact.save()
        
        # Send email notification
        subject = f"New Contact Form Submission from {first_name} {last_name}"
        message_body = f"""
        New contact form submission:
        
        Name: {first_name} {last_name}
        Email: {email}
        Message: {message}
        
        Submitted on: {datetime.now()}
        """
        
        send_mail(
            subject,
            message_body,
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],  # Send to admin email
            fail_silently=False,
        )
        
        return super().form_valid(form)

    def form_invalid(self, form):
        # Handle the case where the form is invalid
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def form_valid_redirection(self, redirect_to):
        return redirect(redirect_to)

    def form_valid_redirect(self):
        return redirect(self.success_url)

def portfolio_details(request):
    return render(request,"portfolio_details.html")

def contact(request):
    return render(request,"contact.html")

def blog_single(request):
    return render(request,"blog_single.html")

def page_404(request):
    return render(request,"page_404.html")

def add_staff(request):
    if request.method == "POST":
        form = AddStaffForm(request.POST, request.FILES)
        if form.is_valid():
            # Create user
            user = CustomUser.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                user_type=2  # Staff user
            )
            
            # Create staff profile
            staff = form.save(commit=False)
            staff.admin = user
            staff.save()
            
            messages.success(request, "Staff account created successfully!")
            return redirect('success_page')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AddStaffForm()
    
    return render(request, 'add_staff.html', {'form': form})

@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse("True")
    else:
        return HttpResponse("False")

@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse("True")
    else:
        return HttpResponse("False")

@login_required
def profile_view(request):
    # Fetch the currently logged-in user
    user = request.user
    
    # Get the staff profile if it exists
    try:
        staff = Staffs.objects.get(admin=user)
        context = {
            'user': user,
            'staff': staff
        }
    except Staffs.DoesNotExist:
        # If no staff profile exists, just pass the user
        context = {
            'user': user,
            'staff': None
        }
    
    return render(request, 'profile.html', context)

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Prevent user logout before redirecting
            messages.success(request, "Your password was successfully updated!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {'form': form})

@csrf_exempt
def check_mct_number_exist(request):
    mct_number = request.POST.get("mct_number")
    staff_obj = Staffs.objects.filter(mct_number=mct_number).exists()
    if staff_obj:
        return HttpResponse("True")
    else:
        return HttpResponse("False")

def account_creation_success(request):
    return render(request, 'success_page.html')
