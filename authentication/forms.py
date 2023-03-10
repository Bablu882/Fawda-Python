from django.contrib.auth.admin import UserAdmin
from .models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator

class UserCreationFormWithMobile(UserCreationForm):
    mobile_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Mobile number must be entered in the format: '8427262631'. Only 10 digits allowed."
    )
    mobile_no = forms.CharField(validators=[mobile_regex], max_length=17, required=True, help_text='Required. Enter a valid mobile number.')
    
    class Meta:
        model = User
        fields = ('username', 'mobile_no')


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationFormWithMobile
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'mobile_no'),
        }),
    )
