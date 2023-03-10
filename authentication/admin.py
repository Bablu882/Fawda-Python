from django.contrib import admin
from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import UserCreationFormWithMobile, CustomUserAdmin

# admin.site.register(User, CustomUserAdmin)

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(OTP)
admin.site.register(State)
admin.site.register(District)

