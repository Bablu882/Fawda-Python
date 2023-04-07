from django.urls import path,include
from .views import *
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'states', StateViewSet, basename='state')
# router.register(r'districts', DistrictViewSet, basename='district')


urlpatterns = [
    path('',test),
    path('api/', include(router.urls)),
    path('api/register/', RegisterApi.as_view()),
    path('api/login/',LoginApi.as_view()),
    path('api/verify/',VerifyMobile.as_view()),
    path('api/profile/',ProfileApi.as_view()),
    # path('api/profile/',profile_view,name='profile'),
    path('chart-ajax/', views.chartJsonListView.as_view(), name="chart-ajax"),
    path('chart-ajax-admin/', views.chartJsonListViewAdmin.as_view(), name="chart-ajax-admin"),
    path('logout/',logout_view,name='logout'),
    path('api/districts/',DistrictApiView.as_view()),
    path('api/logout/',User_logout,name='User_logout'),
   


]
