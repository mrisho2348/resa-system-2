from django.urls import path
from kahamahmis import kahamaEditView

urlpatterns = [    
    # Consultation data
    path('update_consultation_data/<int:appointment_id>/', kahamaEditView.update_consultation_data, name='kahama_update_consultation_data'),
    

]
