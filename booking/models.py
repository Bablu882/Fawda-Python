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
    # total_amount=models.CharField(max_length=100,null=True,blank=True) 
    jobsahayak = models.ForeignKey(JobSahayak, on_delete=models.CASCADE,null=True,blank=True)
    jobmachine=models.ForeignKey(JobMachine, on_delete=models.CASCADE,null=True,blank=True)
    booking_user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_booked = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_TYPE_CHOICES)
    count_male=models.CharField(max_length=100,null=True,blank=True)
    count_female=models.CharField(max_length=100,null=True,blank=True)
    total_amount=models.CharField(max_length=100,null=True,blank=True)
    total_amount_sahayak=models.CharField(max_length=100,null=True,blank=True)
    total_amount_theka=models.CharField(max_length=100,null=True,blank=True)
    total_amount_machine=models.CharField(max_length=100,null=True,blank=True)
    payment_your=models.CharField(max_length=100,null=True,blank=True)
    fawda_fee=models.CharField(max_length=100,null=True,blank=True)
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

    # # other fields as needed
    # def save(self, *args, **kwargs):
    #     if self.jobsahayak.job_type == 'individuals_sahayak':
    #         count_male = int(self.count_male) if self.count_male else 0
    #         count_female = int(self.count_female) if self.count_female else 0
    #         pay_amount_male = int(self.jobsahayak.pay_amount_male) if self.jobsahayak.pay_amount_male else 0
    #         pay_amount_female = int(self.jobsahayak.pay_amount_female) if self.jobsahayak.pay_amount_female else 0
    #         num_days = int(self.jobsahayak.num_days) if self.jobsahayak.num_days else 0
            
    #         # Extract the percentage value from fawda_fee_percentage field
    #         fawda_fee_percentage_str = self.jobsahayak.fawda_fee_percentage.fawda_fee_percentage.rstrip('%')
    #         fawda_fee_percentage = float(fawda_fee_percentage_str) if fawda_fee_percentage_str else 0

    #         # calculate total amount without fawda_fee
    #         total_amount_without_fawda = (count_male * pay_amount_male + count_female * pay_amount_female) * num_days
            
    #         # calculate fawda_fee amount
    #         fawda_fee_amount = round(total_amount_without_fawda * (fawda_fee_percentage / 100), 2)
            
    #         # calculate total amount with fawda_fee
    #         total_amount = round(total_amount_without_fawda + fawda_fee_amount, 2)
            
    #         # calculate payment_your amount
    #         payment_your = round(total_amount_without_fawda - fawda_fee_amount, 2)
            
    #         # update the model fields
    #         # self.fawda_fee = str(fawda_fee_percentage)
    #         self.total_amount = str(total_amount)
    #         self.payment_your = str(payment_your)
    #         self.total_amount_sahayak=str(total_amount_without_fawda)
    #         # self.fawda_fee_percentage = self.fawda_fee_percentage
    #     super(JobSahayak, self).save(*args, **kwargs)
    
class Rating(models.Model):
    booking_job=models.ForeignKey(JobBooking,on_delete=models.CASCADE)
    rating=models.IntegerField(null=True,blank=True)
    comment=models.TextField()
    def __str__(self) -> str:
        return f"{self.booking_job} rating +{self.rating}"
