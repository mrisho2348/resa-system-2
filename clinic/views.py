
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
    forms = AddStaffForm() 
    return render(request,"add_staff.html",{"forms":forms})    
    
def add_staff_save(request):
    if request.method != "POST":
        return HttpResponse("Method not allowed")

    form = AddStaffForm(request.POST, request.FILES)

    if form.is_valid():
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
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
        profile_picture = form.cleaned_data["profile_picture"]

        date_of_birth_str = form.cleaned_data["date_of_birth"]
        date_of_birth = None

        if isinstance(date_of_birth_str, str):
            try:
                date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            except ValueError:
                form.add_error("date_of_birth", "Invalid date of birth format. Please use yyyy-mm-dd")
                messages.error(request, "Invalid date of birth format. Please use yyyy-mm-dd")
                return HttpResponseRedirect(reverse("clinic:add_staff"))

        try:
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError("Email already exists Try another email or contact with administator for support")

            if CustomUser.objects.filter(username=username).exists():
                raise ValidationError("Username already exists try another username or contact with administator for support")

            user = CustomUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                user_type=2
            )
            user.staff.middle_name = middle_name
            user.staff.gender = gender
            user.staff.phone_number = phone_number
            user.staff.marital_status = marital_status
            user.staff.profession = profession
            user.staff.role = role
            user.staff.work_place = work_place
            user.staff.joining_date = joining_date
            user.staff.profile_picture = profile_picture

            if date_of_birth is not None:
                user.staff.date_of_birth = date_of_birth

            user.is_active = False  # Deactivate account until admin activates it
            user.save()

            # Send email to the user
            send_mail(
                'Welcome to RESA - Account Creation Successful',
                f'Dear {first_name} {last_name},\n\n'
                'We are excited to inform you that your account has been successfully created on RESA. However, before you can log in, your account needs to be activated by the administrator.\n\n'
                'Please note the following:\n'
                '1. Your account will be reviewed and activated by the administrator shortly.\n'
                '2. If the activation takes too long, please feel free to contact the administrator for assistance.\n'
                '3. You will receive an email notification once your account is activated or if any additional information is required.\n\n'
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
            return HttpResponseRedirect(reverse("clinic:success_page"))  # Redirect to a success page

        except ValidationError as ve:
            messages.error(request, str(ve))
            return HttpResponseRedirect(reverse("clinic:add_staff"))
        except Exception as e:
            print("Error:", e)
            messages.error(request, "Failed to save staff")
            return HttpResponseRedirect(reverse("clinic:add_staff"))

    else:
        messages.error(request, "Failed to save staff")
        return render(request, "add_staff.html", {"form": form})   

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