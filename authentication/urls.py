from django.urls import path,include
from .views import *
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'states', StateViewSet, basename='state')
router.register(r'districts', DistrictViewSet, basename='district')


urlpatterns = [
    path('',test),
    path('api/', include(router.urls)),
    path('api/register/', Register.as_view(), name='register'),
    path('api/mobile_verify/',VerifyMobile.as_view()),
    path('chart-ajax/', views.chartJsonListView.as_view(), name="chart-ajax"),
    path('chart-ajax-admin/', views.chartJsonListViewAdmin.as_view(), name="chart-ajax-admin"),

]
