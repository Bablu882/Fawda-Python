from django.urls import path
from .views import *
from . import views
# from .admin import custom_admin_site

urlpatterns=[
    path('home2/',home2,name='home2'),
    # path('job_booking_list/', views.job_booking_list, name='job_booking_list'),
    path('job_details/',JobDetailsAdmin.as_view()),
    path('job_details_admin/',JobDetailsAdminPanel.as_view()),
    path('payment_status/',AdminPaymentStatus.as_view()),
    # path('custom/', admin_site.admin_view(custom_view), name='custom'),
    # path('mycustomadmin/', custom_admin_site.urls),


        

]   