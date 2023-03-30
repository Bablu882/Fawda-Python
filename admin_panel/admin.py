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
from .views import my_custom_view,custom_users_view

class MyModelAdmin(admin.ModelAdmin):
    # ... your other ModelAdmin code ...

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('custom/', my_custom_view, name='admin_custom'),
            path('user_list/',custom_users_view, name='user_list'),
        ]
        return custom_urls + urls
    

