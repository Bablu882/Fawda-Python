"""fawda URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from admin_panel.views import my_custom_view,custom_users_view,booking_log_history
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/booking_history/', my_custom_view, name='booking_history'),
    path('admin/user_list/',custom_users_view, name='user_list'),
    path('admin/booking_log/',booking_log_history, name='booking_log'),
    path('admin/', admin.site.urls),
    path('',include('authentication.urls')),
    path('',include('jobs.urls')),
    path('',include('booking.urls')),
    path('',include('payments.urls')),
    path('',include('admin_panel.urls')),
    path('tinymce/', include('tinymce.urls')),

]
if settings.DEBUG:
    urlpatterns += (
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        )