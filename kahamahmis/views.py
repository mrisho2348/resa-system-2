
from django.shortcuts import  render
from django.contrib.auth import logout,login
from django.http import  HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.views.generic.edit import FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from clinic.emailBackEnd import EmailBackend
from clinic.models import ContactDetails, Staffs





def contact(request):
    return render(request,"contact.html")
def blog_single(request):
    return render(request,"blog-single.html")
def page_404(request):
    return render(request,"404.html")


def ShowLoginKahama(request):  
  return render(request,'kahama_template/login.html')

def DoLoginKahama(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not allowed</h2>")
    else:
        user = EmailBackend.authenticate(request, request.POST.get("email"), request.POST.get("password"))
        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is not active. Please contact the administrator for support.")
                return HttpResponseRedirect(reverse("kahamahmis:kahama"))

            login(request, user)
            if user.user_type == "1":
                return HttpResponseRedirect(reverse("kahama_dashboard"))
            elif user.user_type == "2":
                staff = Staffs.objects.get(admin=user)
                role = staff.role.lower()  # Convert role to lowercase for consistency
                if staff.work_place == 'kahama':
                    if role == "doctor":
                      return HttpResponseRedirect(reverse("kahama_dashboard"))                    
                    elif role == "admin":
                      return HttpResponseRedirect(reverse("divine_dashboard"))                    
                    else :
                      messages.error(request, f"for this clinic were currently dont have {role} role . Please contact the administrator for support.")  
                      return HttpResponseRedirect(reverse("kahamahmis:kahama"))                    
                else :
                    messages.error(request, "You are not a staff for this hospital or clinic. Please contact the administrator for support.")
                    return HttpResponseRedirect(reverse("kahamahmis:kahama"))            
            else:
                return HttpResponseRedirect(reverse("kahamahmis:kahama"))
        else:
            messages.error(request, "Invalid Login Details")
            return HttpResponseRedirect(reverse("kahamahmis:kahama"))
    
    
def GetUserDetails(request):
  user = request.user
  if user.is_authenticated:
    return HttpResponse("User : "+user.email+" usertype : " + user.usertype)
  else:
    return HttpResponse("Please login first")   
  
  
def logout_user(request):
  logout(request)
  return HttpResponseRedirect(reverse("home"))
    
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

