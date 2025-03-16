
from datetime import  datetime
from django.shortcuts import  redirect, render
from django.contrib.auth import logout,login
from django.http import  HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import F
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from clinic.emailBackEnd import EmailBackend
from clinic.forms import AddStaffForm
from clinic.models import ContactDetails, CustomUser, Staffs
from django.core.exceptions import  ValidationError
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
# Create your views here.
def index(request):
    return render(request,"index.html")


def contact(request):
    return render(request,"contact.html")
def blog_single(request):
    return render(request,"blog-single.html")
def page_404(request):
    return render(request,"404.html")


def ShowLogin(request):  
  return render(request,'login.html')



def DoLogin(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("login"))
    else:
        user = EmailBackend.authenticate(request, request.POST.get("email"), request.POST.get("password"))
        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is not active. Please contact the administrator for support.")
                return HttpResponseRedirect(reverse("login"))

            login(request, user)
            if user.user_type == "1":
                return HttpResponseRedirect(reverse("admin_dashboard"))
            elif user.user_type == "2":
                # Assuming staff user is always associated with Staffs model
                staff = Staffs.objects.get(admin=user)
                role = staff.role.lower()  # Convert role to lowercase for consistency

                # Redirect staff user based on their role
                if staff.work_place == 'resa':                   
                    if role == "doctor":
                        return redirect("doctor_dashboard")
                    elif role == "nurse":
                        return redirect("nurse_dashboard")
                    elif role == "admin":
                        return redirect("admin_dashboard")
                    elif role == "physiotherapist":
                        return redirect("physiotherapist_dashboard")
                    elif role == "labtechnician":
                        return redirect("labtechnician_dashboard")
                    elif role == "pharmacist":
                        return redirect("pharmacist_dashboard")
                    elif role == "receptionist":
                        return redirect("receptionist_dashboard")
                    else:
                        # If role is not recognized, redirect to login
                        return HttpResponseRedirect(reverse("login"))

                # Check if the staff's workplace is valid
                else :
                    messages.error(request, "You are not a staff for this hospital or clinic. Please contact the administrator for support.")
                    return HttpResponseRedirect(reverse("login"))
            else:
                return HttpResponseRedirect(reverse("login"))
        else:
            messages.error(request, "Invalid Login Details")
            return HttpResponseRedirect(reverse("login"))
    
    
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
    form_class = None  # No Django form is used
    success_url = '/success/'  # Set the URL where users should be redirected on success
    success_message = "Your message was submitted successfully. We'll get back to you soon."

    def form_valid(self, form):
        try:
            # Process the form data
            your_name = self.request.POST.get('your_name')
            your_email = self.request.POST.get('your_email')
            your_subject = self.request.POST.get('your_subject', '')
            your_message = self.request.POST.get('your_message')

            # Save to the model (optional)
            ContactDetails.objects.create(
                your_name=your_name,
                your_email=your_email,
                your_subject=your_subject,
                your_message=your_message
            )

            # Send email to the administrator
            send_mail(
                f'New Contact Form Submission: {your_subject}',
                f'Name: {your_name}\nEmail: {your_email}\nMessage: {your_message}',
                'from@example.com',  # Sender's email address
                ['mrishohamisi2348@gmail.com'],  # Administrator's email address
                fail_silently=False,
            )

            messages.success(self.request, self.get_success_message())
            return self.form_valid_redirection(self.form_valid_redirect())
        except Exception as e:
            messages.error(self.request, f"An error occurred: {str(e)}")
            return self.form_invalid(self.get_form())

    def form_invalid(self, form):
        # Handle the case where the form is invalid
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid_redirection(self, redirect_to):
        return self.render_to_response({'redirect_to': redirect_to})

    def form_valid_redirect(self):
        return self.get_success_url()    


def portfolio_details(request):
    return render(request,"portfolio-details.html")

def add_staff(request):
    if request.method == "POST":
        form = AddStaffForm(request.POST, request.FILES)
        
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            phone_number = form.cleaned_data["phone_number"]
            gender = form.cleaned_data["gender"]
            middle_name = form.cleaned_data["middle_name"]
            marital_status = form.cleaned_data["marital_status"]
            profession = form.cleaned_data["profession"]
            role = form.cleaned_data["role"]
            work_place = form.cleaned_data["work_place"]
            joining_date = form.cleaned_data["joining_date"]
            mct_number = form.cleaned_data["mct_number"]  # MCT Number
            date_of_birth = form.cleaned_data.get("date_of_birth")

            # Validate passwords
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, "add_staff.html", {"form": form})

            try:
                # Ensure username is not an email
                if "@" in username:
                    raise ValidationError("Username cannot be an email address. Please choose another username.")
                
                # Ensure unique email and username
                if CustomUser.objects.filter(email=email).exists():
                    raise ValidationError("Email already exists. Try another email or contact the administrator for support.")
                if CustomUser.objects.filter(username=username).exists():
                    raise ValidationError("Username already exists. Try another username or contact the administrator for support.")
                
                # Ensure the staff name is unique (if required)
                if Staffs.objects.filter(admin__first_name=first_name, middle_name=middle_name, admin__last_name=last_name).exists():
                    raise ValidationError("A staff member with this full name already exists. Try another name or contact the administrator for support.")
                
                # Validate that the user is at least 18 years old
                if date_of_birth:
                    today = datetime.today().date()
                    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
                    if age < 18:
                        raise ValidationError("Any staff member must be at least 18 years old.")

                # Ensure the joining date is not in the future
                if joining_date > datetime.today().date():
                    raise ValidationError("Joining date cannot be in the future.")
                
                # Ensure MCT number is unique if provided
                if mct_number and Staffs.objects.filter(mct_number=mct_number).exists():
                    raise ValidationError("MCT number already exists. Please provide a unique MCT number.")

                # Create the user and staff
                user = CustomUser.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    user_type=2  # assuming user type 2 is for staff
                )
                user.staff.middle_name = middle_name
                user.staff.gender = gender
                user.staff.phone_number = phone_number
                user.staff.marital_status = marital_status
                user.staff.profession = profession
                user.staff.role = role
                user.staff.work_place = work_place
                user.staff.joining_date = joining_date
                user.staff.mct_number = mct_number  # Save MCT Number

                if date_of_birth:
                    user.staff.date_of_birth = date_of_birth

                user.is_active = False  # Deactivate account until admin activates it
                user.save()

                # Send email notification
                send_mail(
                    'Welcome to RESA - Account Creation Successful',
                    f'Dear {first_name} {last_name},\n\n'
                    'Your account has been successfully created on RESA. However, before you can log in, your account needs to be activated by the administrator.\n\n'
                    'Please note the following:\n'
                    '1. Your account will be reviewed and activated by the administrator shortly.\n'
                    '2. If the activation takes too long, please feel free to contact the administrator for assistance.\n'
                    '3. You will receive an email notification once your account is activated.\n\n'
                    'Thank you for joining our community!\n\n'
                    'Best regards,\n'
                    'MRISHO HAMISI\n'
                    'RESA Team\n\n'
                    'Note: This is an automated message. Please do not reply directly to this email.',
                    'admin@example.com',
                    [email],
                    fail_silently=False,
                )

                messages.success(request, "Account created successfully! Please check your email for activation instructions.")
                return redirect(reverse("clinic:success_page"))

            except ValidationError as ve:
                messages.error(request, str(ve))
            except Exception as e:
                messages.error(request, f"Failed to save staff: {str(e)}")

        else:
            errors = form.errors.as_data()  # Retrieve form errors
            for field, error_list in errors.items():
                for error in error_list:
                   if field == "__all__":
                        messages.error(request, f"{error}")  # Handle non-field errors separately
                   else:
                        messages.error(request, f"{field.capitalize()}: {error}")

            messages.error(request, "Form validation failed. Please check the errors below.")

    else:
        form = AddStaffForm()  # Ensures the form is initialized properly

    return render(request, "add_staff.html", {"form": form})  # Pass form instead of forms


def check_mct_number_exist(request):
    if request.method == "POST":
        mct_number = request.POST.get("mct_number", "").strip()
        if Staffs.objects.filter(mct_number=mct_number).exists():
            return JsonResponse("True", safe=False)
        return JsonResponse("False", safe=False)
          

def account_creation_success(request):
    return render(request, 'success_page.html')

@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_object = CustomUser.objects.filter(email=email).exists()
    if user_object:
        return HttpResponse(True)
    
    else:
        return HttpResponse(False)
    
    
@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_object = CustomUser.objects.filter(username=username).exists()
    if user_object:
        return HttpResponse(True)
    
    else:
        return HttpResponse(False)

@login_required
def profile_view(request):
    # Fetch the currently logged-in user
    user = request.user
    
    try:
        # Check if the user is a staff member by checking user_type
        if user.user_type == 'Staffs':
            # Try to get the staff's details
            staff = Staffs.objects.get(admin=user)
            
            # Check if the staff's work place is "Resa" or "Kahama"
            if staff.work_place == 'Resa':
                # For Resa, check the staff role and render the corresponding template
                if staff.role == 'admin':
                    return render(request, 'staff/profile.html', {'staff': staff})  # Render Admin's dashboard template
                elif staff.role == 'doctor':
                    return render(request, 'staff/profile.html', {'staff': staff})  # Render Doctor's dashboard template
                elif staff.role == 'nurse':
                    return render(request, 'staff/profile.html', {'staff': staff})  # Render Nurse's dashboard template
                elif staff.role == 'physiotherapist':
                    return render(request, 'staff/profile.html', {'staff': staff})  # Render Physiotherapist's dashboard template
                elif staff.role == 'labTechnician':
                    return render(request, 'staff/profile.html', {'staff': staff})  # Render Lab Technician's dashboard template
                elif staff.role == 'pharmacist':
                    return render(request, 'staff/profile.html', {'staff': staff})  # Render Pharmacist's dashboard template
                elif staff.role == 'receptionist':
                    return render(request, 'staff/profile.html', {'staff': staff})  # Render Receptionist's dashboard template
                else:
                    messages.error(request, "Role not recognized.")
                    return render(request, 'home.html')  # Render home page if role is unknown
            
            elif staff.work_place == 'Kahama':
                # For Kahama, check if the staff role is 'doctor' or 'admin'
                if staff.role == 'doctor':
                    return render(request, 'staff/doctor_dashboard.html', {'staff': staff})  # Render Doctor's dashboard template
                elif staff.role == 'admin':
                    return render(request, 'staff/admin_dashboard.html', {'staff': staff})  # Render Admin's dashboard template
                else:
                    messages.error(request, "Only Doctor and Admin roles are allowed in Kahama.")
                    return render(request, 'home.html')  # Render home page if role is not allowed in Kahama
            
            else:
                # If the work place is not "Resa" or "Kahama", render the profile view normally
                return render(request, 'staff/profile.html', {'staff': staff})
        
        elif user.user_type == 'AdminHOD':
            # If the user is HOD, render the profile page or redirect accordingly
            return render(request, 'staff/hod_profile.html', {'staff': user})
        
        else:
            # For normal users, handle accordingly
            return render(request, 'staff/normal_user_dashboard.html', {'user': user})  # Normal user dashboard or appropriate page
    
    except Staffs.DoesNotExist:
        # If the user is not found in the Staffs model, handle accordingly
        messages.error(request, "Staff information not found.")
        return render(request, 'home.html')  # Or any page you want to render in case of error

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')  # Redirect to profile after changing password
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'staff/change_password.html', {'form': form})
