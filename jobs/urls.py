from django.urls import path
from .views import *
from . import views

urlpatterns=[
    path('api/post_thekepekam/',BookingThekePeKam.as_view()),
    path('api/post_individuals/',BookingSahayakIndividuals.as_view()),
    path('api/post_machine/',BookingJobMachine.as_view()),
    # path('api/jobs/',JobSahayakWithin5km.as_view()),
    # path('api/nearjob/',nearby_jobs),
    

]