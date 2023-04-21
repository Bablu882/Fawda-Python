from django.urls import path
from .views import *
from . import views
urlpatterns=[
       path('api/accept_individuals/',JobAcceptIndividuals.as_view()),
       path('api/accept_theka/',JobAcceptedSahayakTheka.as_view()),
       path('api/accept_machine/',JobAcceptMachin.as_view()),
       path('api/myjobs/',MyJobsDetais.as_view()),
       path('api/mybooking_sahayak_details/',MyBookingDetailsSahayak.as_view()),
       path('api/mybooking_machine_details/',MyBookingDetailsMachine.as_view()),
       path('api/mybooking_pending_sahayak_details/',MyBookingPendingDetailsSahayak.as_view()),
       path('api/mybooking_pending_machine_details/',MyBookingPendingDetailsMachine.as_view()),
       path('api/my_booking_details/',MyBookingDetails.as_view()),
       path('api/rating/create/',RatingCreate.as_view()),
       path('api/booking_ongoing/',OngoingStatusApi.as_view()),
       path('api/booking_completed/',CompletedStatusApi.as_view()),
       path('api/get-rating/',RatingGet.as_view()),
       path('api/rejected/',RejectedBooking.as_view()),
       path('api/cancel/',CancellationBookingJob.as_view()),
       path('api/booking-history-grahak/',MyBookingDetailsHistory.as_view()),

]