from django.db import models

# Create your models here.

class BookingHistorySahayak(models.Model):
    grahak_name=models.CharField(max_length=100,null=True,blank=True)
    grahak_mobile_no=models.CharField(max_length=100,null=True,blank=True)
    job_type=models.CharField(max_length=100,null=True,blank=True)
    job_number=models.CharField(max_length=100,null=True,blank=True)
    job_posting_date=models.CharField(max_length=100,null=True,blank=True)
    job_booking_date=models.CharField(max_length=100,null=True,blank=True)
    job_status=models.CharField(max_length=100,null=True,blank=True)
    payment_status_by_admin=models.CharField(max_length=100,null=True,blank=True)
    paid_to_service_provider=models.CharField(max_length=100,null=True,blank=True)
    paid_by_grahak=models.CharField(max_length=100,null=True,blank=True)
    sahayak_name=models.CharField(max_length=100,null=True,blank=True)
    sahayak_mobile_no=models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return f"{self.grahak_name}+{self.sahayak_name}+{self.job_type} success {self.payment_status_by_admin}"


class BookingHistoryMachine(models.Model):
    grahak_name=models.CharField(max_length=100,null=True,blank=True)
    grahak_mobile_no=models.CharField(max_length=100,null=True,blank=True)
    job_type=models.CharField(max_length=100,null=True,blank=True)
    job_number=models.CharField(max_length=100,null=True,blank=True)
    job_posting_date=models.CharField(max_length=100,null=True,blank=True)
    job_booking_date=models.CharField(max_length=100,null=True,blank=True)
    job_status=models.CharField(max_length=100,null=True,blank=True)
    payment_status_by_admin=models.CharField(max_length=100,null=True,blank=True)
    paid_to_service_provider=models.CharField(max_length=100,null=True,blank=True)
    paid_by_grahak=models.CharField(max_length=100,null=True,blank=True)
    machine_malik_name=models.CharField(max_length=100,null=True,blank=True)
    machine_malik_mobile_no=models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return f"{self.grahak_name}+{self.machine_malik_name}+{self.job_type} success {self.payment_status_by_admin}"

 
class ClientInformations(models.Model):
    privacy_policy=models.TextField()
    terms_condition=models.TextField()
    phone_no=models.CharField(max_length=20)
    about_us=models.TextField()
    client_address=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.phone_no

class AppVersion(models.Model):
    version=models.CharField(max_length=20)    
    release_date=models.DateTimeField(auto_now_add=True)
    def __str__(self) -> str:
        return self.version
