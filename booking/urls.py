from django.urls import path
from .views import *
from . import views
urlpatterns=[
       path('api/accept_individuals/',JobAcceptIndividuals.as_view()),
       path('api/accept_theka/',JobAcceptedSahayakTheka.as_view()),
]