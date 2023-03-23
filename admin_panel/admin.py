from django.contrib import admin
from django.http import HttpResponse
# Register your models here.
from .models import *
admin.site.register(BookingHistorySahayak)
admin.site.register(BookingHistoryMachine)



