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
        message="Mobile number must be entered in the format: '8427262631'. Only 10 digits allowed."
    )
    mobile_no = models.CharField(validators=[mobile_regex], max_length=17, blank=True) # validators should be a list
    is_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=USER_STATUS_CHOICES)



class OTP(models.Model):
    otp=models.CharField(max_length=20)
    user=models.ForeignKey(User,on_delete=models.CASCADE)


class Profile(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=100,null=True,blank=True)
    gender=models.CharField(max_length=10,choices=GENDER_CHOICES) 
    # avatar=models.ImageField(null=True,blank=True,default='avatars/default.png',upload_to='avatars')
    mohalla=models.CharField(max_length=250,null=True,blank=True)
    village=models.CharField(max_length=250,null=True,blank=True)


# class Job(models.Model):
#     JOB_TYPE_CHOICES = (
#         ('theke_pe_kam', 'Theke Pe Kam'),
#         ('individuals_sahayak', 'Individuals Sahayak'),
#         ('machine_job', 'Machine Job'),
#     )

#     grahak = models.ForeignKey(User, on_delete=models.CASCADE)
#     job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
#     village = models.CharField(max_length=100)
#     date = models.DateField()
#     time = models.TimeField()
#     status = models.CharField(max_length=20, default='pending')
#     payment_amount = models.DecimalField(max_digits=8, decimal_places=2)
#     sahayak_accepted = models.BooleanField(default=False)
#     machine_malik_accepted = models.BooleanField(default=False)
#     machine_type = models.CharField(max_length=20, blank=True)
#     job_description = models.TextField(blank=True)
#     job_land_size = models.CharField(max_length=20, blank=True)
#     pay_amount_male = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
#     pay_amount_female = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
#     num_days = models.IntegerField(blank=True, null=True)

#     class Meta:
#         ordering = ['-date', '-time']

#     def __str__(self):
#         return f"{self.job_type} job in {self.village} on {self.date}"


###-----------------------------------------------------------------------------------####


from django.db import models
from django.utils.text import slugify

class State(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=2)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(State, self).save(*args, **kwargs)

class District(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(District, self).save(*args, **kwargs)
