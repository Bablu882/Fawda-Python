from django.contrib import admin
from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import UserCreationFormWithMobile, CustomUserAdmin


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user','name','gender')
    list_display_links = ("id", 'user','name' )
    # list_per_page = 10
    # search_fields = ("id", 'user__username',)


admin.site.register(Profile,ProfileAdmin)
admin.site.register(OTP)
admin.site.register(State)
admin.site.register(District)

from django.contrib.auth.models import Group
from .models import User as MyCustomUser



class MyCustomUserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('mobile_no',)}),
        (('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    # Remove authorization and authentication fields
    fieldsets[2][1]['fields'] = ('is_active','is_staff','is_superuser','is_verified','user_type')
    list_display = ('id','mobile_no','user_type','is_verified')
    list_display_links = ("id", 'mobile_no', )



admin.site.register(MyCustomUser, MyCustomUserAdmin)
admin.site.unregister(Group)
# admin.site.unregister(User)
