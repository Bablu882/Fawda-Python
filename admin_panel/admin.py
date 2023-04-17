from django.contrib import admin
from django.http import HttpResponse,Http404
from django.http import HttpResponse
from django.urls import path
from .models import *
from django.contrib.admin import AdminSite,ModelAdmin
from django.utils.html import format_html

# Register your models here.
from .models import *
admin.site.register(BookingHistoryMachine)
admin.site.register(BookingHistorySahayak)
# admin.site.register(ClientInformations)
admin.site.register(AppVersion)
from .views import my_custom_view,custom_users_view,booking_log_history

class MyModelAdmin(admin.ModelAdmin):
    # ... your other ModelAdmin code ...

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('booking_history/', my_custom_view, name='booking_history'),
            path('user_list/',custom_users_view, name='user_list'),
            path('booking_log/',booking_log_history,name='booking_log'),
        ]
        return custom_urls + urls
    

from .models import ClientInformation
from django_summernote.admin import SummernoteModelAdmin

class ClientInformationsAdmin(SummernoteModelAdmin):
    summernote_fields = ('privacy_policy', 'terms_condition', 'about_us')

admin.site.register(ClientInformation, ClientInformationsAdmin)