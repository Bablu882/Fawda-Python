from django.contrib import admin
from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import UserCreationFormWithMobile, CustomUserAdmin

# admin.site.register(User, CustomUserAdmin)

# Register your models here.
# admin.site.register(User)
admin.site.register(Profile)
admin.site.register(OTP)
admin.site.register(State)
admin.site.register(District)

from django.contrib.auth.models import Group
from .models import User as MyCustomUser



class MyCustomUserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ()}),
        (('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    # Remove authorization and authentication fields
    fieldsets[2][1]['fields'] = ('is_active','is_staff','is_superuser','is_verified','mobile_no','status')

admin.site.register(MyCustomUser, MyCustomUserAdmin)
admin.site.unregister(Group)
# admin.site.unregister(User)
