from django.db import models
from authentication.models import User



class Job(models.Model):
    STATUS_TYPE_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Booked', 'Booked'),
        ('Ongoing','Ongoing'),
        ('Completed','Completed'),
    )
    JOB_TYPE_CHOICES = (
        ('theke_pe_kam', 'Theke Pe Kam'),
        ('individuals_sahayak', 'Individuals Sahayak'),
        ('machine_job', 'Machine Job'),
    )
    grahak = models.ForeignKey(User, on_delete=models.CASCADE)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    village = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    payment_amount = models.DecimalField(max_digits=8, decimal_places=2)
    sahayak_status = models.CharField(max_length=20,choices=STATUS_TYPE_CHOICES)
    machine_malik_status = models.CharField(max_length=20,choices=STATUS_TYPE_CHOICES)
    machine_type = models.CharField(max_length=20, blank=True)
    job_description = models.TextField(blank=True)
    job_land_size = models.CharField(max_length=20, blank=True)
    pay_amount_male = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    pay_amount_female = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    num_days = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.job_type} job in {self.village} on {self.date}"




# from django.contrib.gis.geos import Point
# from django.contrib.gis.db.models.functions import Distance

# user_location = Point(user_longitude, user_latitude)
# distance_limit = 5000  # in meters
# jobs_within_range = Job.objects.annotate(
#     distance=Distance('job_location', user_location)
# ).filter(distance__lte=distance_limit)
