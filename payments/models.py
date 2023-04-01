from django.db import models

# Create your models here.


class Payment(models.Model):
    booking_id = models.CharField(max_length=100)
    amount = models.CharField(max_length=100,null=True,blank=True)
    payment_id = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=100)
    payment_date = models.DateTimeField(auto_now_add=True)
    beneficiary_name=models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return f'{self.booking_id} - {self.amount} - {self.payment_status}'