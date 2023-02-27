from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    GRAHAK = 'G'
    SAHAYAK = 'S'
    MACHINEMALIK = 'M'
    USER_STATUS_CHOICES = [
        (GRAHAK, 'Grahak'),
        (SAHAYAK, 'Sahayak'),
        (MACHINEMALIK, 'MachineMalik'),
    ]

    mobile_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Mobile number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    mobile_no = models.CharField(validators=[mobile_regex], max_length=17, blank=True) # validators should be a list
    is_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=USER_STATUS_CHOICES)



class OTP(models.Model):
    otp=models.CharField(max_length=20)
    user=models.ForeignKey(User,on_delete=models.CASCADE)