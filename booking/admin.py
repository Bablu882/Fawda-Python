from django.contrib import admin
from .models import *
# Register your models here.

class BookingJobAdmin(admin.ModelAdmin):
    list_display = ('id','booking_user')
    # list_filter = ("status",)
    list_display_links = ("id", )
    # list_per_page = 10
    # search_fields = ("id", 'user__username',)




admin.site.register(JobBooking,BookingJobAdmin)
admin.site.register(Rating)
