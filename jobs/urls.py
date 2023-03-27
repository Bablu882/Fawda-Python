from django.urls import path
from .views import *
from . import views

urlpatterns=[
    path('api/post_thekepekam/',BookingThekePeKam.as_view()),
    path('api/post_individuals/',BookingSahayakIndividuals.as_view()),
    path('api/post_machine/',BookingJobMachine.as_view()),
    # path('api/jobs/',JobSahayakWithin5km.as_view()),
    path('api/nearjob/',GetAllJob.as_view()),
    path('api/user/',Requestuser.as_view()),
    path('api/sahayak_job_details/',GetSahayakJobDetails.as_view()),
    path('api/machine_job_details/',GetMachineJobDetails.as_view()),
    path('api/machines/',GetMachineDetails.as_view()),
    path('api/edit_thekepekam/',EditThekePeKam.as_view()),
    path('api/edit_individuals/',EditIndividualSahayak.as_view()),
    path('api/edit_machine/',EditJobMachine.as_view()),
    
    

]