from django.db import models
from authentication.models import User
from jobs.models import JobSahayak,JobMachine


class JobBooking(models.Model):
    STATUS_TYPE_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Booked', 'Booked'),
        ('Ongoing','Ongoing'),
        ('Completed','Completed'),
    )
    jobsahayak = models.ManyToManyField(JobSahayak, related_name='jobbooking_set')
    jobmachine=models.ManyToManyField(JobMachine, related_name='jobbooking_set')
    booking_user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_booked = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_TYPE_CHOICES)
    # other fields as needed