from django.contrib import admin
from .models import *
# Register your models here.

class BookingJobAdmin(admin.ModelAdmin):
    list_display = ('id','status','booking_user','jobsahayak','jobmachine')
    # list_filter = ("status",)
    list_display_links = ("id","status" )
    # list_per_page = 10
    # search_fields = ("id", 'user__username',)




admin.site.register(JobBooking,BookingJobAdmin)
admin.site.register(Rating)
