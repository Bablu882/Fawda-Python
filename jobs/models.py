from django.db import models
from authentication.models import User

class LandPreparation(models.Model):
    name=models.CharField(max_length=500,null=True,blank=True)
    def __str__(self):
        return self.name

class Harvesting(models.Model):
    name=models.CharField(max_length=500,null=True,blank=True)
    def __str__(self):
        return self.name

class Sowing(models.Model):
    name=models.CharField(max_length=500,null=True,blank=True)
    def __str__(self):
        return self.name    

class JobSahayak(models.Model):
    STATUS_TYPE_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Booked', 'Booked'),
        ('Ongoing','Ongoing'),
        ('Completed','Completed'),
    )
    JOB_TYPE_CHOICES = (
        ('theke_pe_kam', 'theke_pe_kam'),
        ('individuals_sahayak', 'individuals_sahayak')
    )
    grahak = models.ForeignKey(User, on_delete=models.CASCADE)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    status=models.CharField(max_length=20,choices=STATUS_TYPE_CHOICES,default='Pending')
    village = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    datetime= models.DateTimeField() 
    payment_amount = models.CharField(max_length=100,blank=True,null=True)
    description = models.TextField(blank=True)
    count_male=models.CharField(max_length=100,blank=True,null=True)
    count_female=models.CharField(max_length=100,blank=True,null=True)
    pay_amount_male = models.CharField(max_length=100, blank=True, null=True)
    pay_amount_female = models.CharField(max_length=100, blank=True, null=True)
    total_amount=models.CharField(max_length=100, blank=True, null=True)
    num_days = models.CharField(max_length=100,blank=True, null=True)
    land_area=models.CharField(max_length=100,null=True,blank=True)
    LAND_TYPE=(
        ('Killa','Killa'),
        ('Bigha','Bigha')
    )
    land_type=models.CharField(max_length=10,choices=LAND_TYPE)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.job_type} job in {self.village} on {self.date}"
    
    def formatted_datetime(self):
        return self.datetime.strftime('%I:%M %p')
    
    def save(self, *args, **kwargs):
        if self.job_type == 'individuals_sahayak':
            count_male = int(self.count_male) if self.count_male else 0
            count_female = int(self.count_female) if self.count_female else 0
            pay_amount_male = int(self.pay_amount_male) if self.pay_amount_male else 0
            pay_amount_female = int(self.pay_amount_female) if self.pay_amount_female else 0
            num_days = int(self.num_days) if self.num_days else 0
            self.total_amount = str((count_male * pay_amount_male + count_female * pay_amount_female) * num_days)
        super().save(*args, **kwargs)


class JobMachine(models.Model):
    STATUS_TYPE_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Booked', 'Booked'),
        ('Ongoing','Ongoing'),
        ('Completed','Completed'),
    )
    LAND_TYPE_CHOICES=(
        ('Killa','Killa'),
        ('Bigha','Bigha')
    )
    grahak=models.ForeignKey(User,on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)
    # time=models.TimeField()
    datetime= models.DateTimeField() 
    description=models.TextField(blank=True)
    land_type=models.CharField(max_length=10,choices=LAND_TYPE_CHOICES)
    status=models.CharField(max_length=20,choices=STATUS_TYPE_CHOICES,default='Pending')
    land_area=models.CharField(max_length=100,null=True,blank=True)
    total_amount=models.CharField(max_length=100, blank=True, null=True)
    amount=models.CharField(max_length=100, blank=True, null=True)
    landpreparation=models.ForeignKey(LandPreparation,on_delete=models.CASCADE)
    harvesting=models.ForeignKey(Harvesting,on_delete=models.CASCADE)
    sowing=models.ForeignKey(Sowing,on_delete=models.CASCADE)
    others=models.CharField(max_length=500,null=True,blank=True)
    def __str__(self) -> str:
        return self.grahak.mobile_no
    
    def formatted_datetime(self):
        return self.datetime.strftime('%I:%M %p')




# from django.contrib.gis.geos import Point
# from django.contrib.gis.db.models.functions import Distance

# user_location = Point(user_longitude, user_latitude)
# distance_limit = 5000  # in meters
# jobs_within_range = Job.objects.annotate(
#     distance=Distance('job_location', user_location)
# ).filter(distance__lte=distance_limit)
