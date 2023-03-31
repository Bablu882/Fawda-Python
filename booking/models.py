from django.db import models
from authentication.models import User
from jobs.models import JobSahayak,JobMachine
from django.core.exceptions import PermissionDenied
from django.utils import timezone


class JobBooking(models.Model):
    STATUS_TYPE_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Booked', 'Booked'),
        ('Ongoing','Ongoing'),
        ('Completed','Completed'),
    )
    # total_amount=models.CharField(max_length=100,null=True,blank=True) 
    jobsahayak = models.ForeignKey(JobSahayak, on_delete=models.CASCADE,null=True,blank=True)
    jobmachine=models.ForeignKey(JobMachine, on_delete=models.CASCADE,null=True,blank=True)
    booking_user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_accepted=models.DateTimeField(auto_now_add=True)
    date_booked = models.DateTimeField(null=True,blank=True)
    date_ongoing=models.DateTimeField(null=True,blank=True)
    date_completed=models.DateTimeField(null=True,blank=True)
    status = models.CharField(max_length=20, choices=STATUS_TYPE_CHOICES)
    count_male=models.CharField(max_length=100,null=True,blank=True)
    count_female=models.CharField(max_length=100,null=True,blank=True)
    total_amount=models.CharField(max_length=100,null=True,blank=True)
    total_amount_sahayak=models.CharField(max_length=100,null=True,blank=True)
    total_amount_theka=models.CharField(max_length=100,null=True,blank=True)
    total_amount_machine=models.CharField(max_length=100,null=True,blank=True)
    payment_your=models.CharField(max_length=100,null=True,blank=True)
    fawda_fee=models.CharField(max_length=100,null=True,blank=True)
    admin_commission=models.CharField(max_length=100,null=True,blank=True)
    pay_amount_male=models.CharField(max_length=100,null=True,blank=True)
    pay_amount_female=models.CharField(max_length=100,null=True,blank=True)
    ADMIN_PAYMENT=(
        ('Pending','Pending'),
        ('Paid','Paid')
    )
    is_admin_paid=models.CharField(max_length=20,choices=ADMIN_PAYMENT, default='Pending')

    def __str__(self):
        if self.jobsahayak:
            return f"{self.jobsahayak.job_type}: grahak:{self.jobsahayak.grahak.profile.name}"
        else:    
            return f"{self.jobmachine.job_type}: grahak:{self.jobmachine.grahak.profile.name}" 
    def save(self, *args, **kwargs):
    # Set the corresponding date field based on the new status
        if self.status == 'Booked':
            self.date_booked = timezone.now()
        elif self.status == 'Ongoing':
            self.date_ongoing = timezone.now()
        elif self.status == 'Completed':
            self.date_completed = timezone.now()

        super(JobBooking, self).save(*args, **kwargs) 

    
class Rating(models.Model):
    booking_job=models.ForeignKey(JobBooking,on_delete=models.CASCADE)
    rating=models.IntegerField(null=True,blank=True)
    comment=models.TextField()
    def __str__(self) -> str:
        return f"{self.booking_job} rating +{self.rating}"
