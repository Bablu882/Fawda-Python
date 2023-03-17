from django.db import models
from django.utils.text import slugify
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
# from django.contrib.gis.db import models as mode
# from django.contrib.gis.geos import GEOSGeometry, fromstr


# from django.contrib.gis.db import models as mode


class User(AbstractUser):
    
    USER_STATUS_CHOICES = [
        ('Grahak', 'Grahak'),
        ('Sahayak', 'Sahayak'),
        ('MachineMalik', 'MachineMalik'),
    ]

    mobile_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Mobile number must be entered in the format: '8427262631'. Only 10 digits allowed."
    )
    mobile_no = models.CharField(validators=[mobile_regex], max_length=17, blank=True) # validators should be a list
    is_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=100, choices=USER_STATUS_CHOICES)



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
    state=models.CharField(max_length=50,null=True,blank=True)
    district=models.CharField(max_length=50,null=True,blank=True)
    latitude = models.DecimalField(max_digits=50, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=50, decimal_places=6, blank=True, null=True)
    is_accepted=models.BooleanField(default=False)
    # geo_location = mode.PointField(null=True) # New field

    # def create_geo_location(self):
    #     self.geo_location = fromstr(f'POINT({self.lng} {self.lat})', srid=4326)

    # # Overwrite save() to use create_geo_location()
    # def save(self, **kwargs):
    #     """ Creates a geo_location value (Point), if no prior-value exist"""
    #     if not self.geo_location:
    #         self.create_geo_location()

    def __str__(self):
        return self.user.mobile_no


###-----------------------------------------------------------------------------------####


class State(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=2)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(State, self).save(*args, **kwargs)

class District(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(District, self).save(*args, **kwargs)

