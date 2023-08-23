from django.db import models
from authentication.models import User
from authentication.models import ReferCode

# class LandPreparation(models.Model):
#     name=models.CharField(max_length=500,null=True,blank=True)
#     def __str__(self):
#         return self.name

# class Harvesting(models.Model):
#     name=models.CharField(max_length=500,null=True,blank=True)
#     def __str__(self):
#         return self.name

# class Sowing(models.Model):
#     name=models.CharField(max_length=500,null=True,blank=True)
#     def __str__(self):
#         return self.name    
class WorkType(models.Model):
    name=models.CharField(max_length=100,null=True,blank=True)
    def __str__(self) -> str:
        return self.name

class MachineType(models.Model):
    worktype=models.ForeignKey(WorkType,on_delete=models.CASCADE)
    machine=models.CharField(max_length=100,null=True,blank=True) 
    def __str__(self) -> str:
        return f"{self.machine}:work for:{self.worktype}"   

class FawdaFee(models.Model):
    fawda_fee_percentage = models.CharField(max_length=100,default='2.5%')
    def __str__(self) -> str:
        return self.fawda_fee_percentage

class JobSahayak(models.Model):
    STATUS_TYPE_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Booked', 'Booked'),
        ('Ongoing','Ongoing'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
        ('Timeout','Timeout'),
        ('Cancelled-After-Payment','Cancelled-After-Payment')
    )
    JOB_TYPE_CHOICES = (
        ('theke_pe_kam', 'theke_pe_kam'),
        ('individuals_sahayak', 'individuals_sahayak')
    )
    grahak = models.ForeignKey(User, on_delete=models.CASCADE)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    status=models.CharField(max_length=50,choices=STATUS_TYPE_CHOICES,default='Pending')
    village = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    datetime= models.DateTimeField() 
    payment_your = models.CharField(max_length=100,blank=True,null=True)
    fawda_fee=models.CharField(max_length=100,blank=True,null=True)
    fawda_fee_grahak=models.CharField(max_length=100,null=True,blank=True)
    fawda_fee_sahayak=models.CharField(max_length=100,null=True,blank=True)
    description = models.TextField(blank=True)
    fawda_fee_percentage = models.ForeignKey(FawdaFee, on_delete=models.CASCADE, null=True, blank=True, default=1)
    count_male=models.CharField(max_length=100,blank=True,null=True)
    count_female=models.CharField(max_length=100,blank=True,null=True)
    pay_amount_male = models.CharField(max_length=100, blank=True, null=True)
    pay_amount_female = models.CharField(max_length=100, blank=True, null=True)
    total_amount=models.CharField(max_length=100, blank=True, null=True)
    total_amount_sahayak=models.CharField(max_length=100,null=True,blank=True)
    total_amount_theka=models.CharField(max_length=100,null=True,blank=True)
    num_days = models.CharField(max_length=100,blank=True, null=True)
    land_area=models.CharField(max_length=100,null=True,blank=True)
    LAND_TYPE=(
        ('Killa','Killa'),
        ('Bigha','Bigha'),
        ('None','None')
    )
    land_type=models.CharField(max_length=10,choices=LAND_TYPE)
    job_number=models.CharField(max_length=50,null=True,blank=True)
    is_first=models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.job_type} job in {self.village} on {self.date}"
    
    def formatted_datetime(self):
        return self.datetime.strftime('%I:%M %p')
    
    def save(self, *args, **kwargs):
        if self.job_type == 'individuals_sahayak':
            jobs_grahak_sahayak = (JobSahayak.objects.filter(grahak=self.grahak)).count()
            jobs_grahak_machine = (JobMachine.objects.filter(grahak=self.grahak)).count()
            # check_refer = ReferCode.objects.filter(from_user=self.grahak_id)
            # is_refer = False
            # for refers in check_refer:
            #     refer_status = refers.is_refer_active
            #     used_refer_count = refers.used_count
            #     # print(used_refer_count)
            #     if refer_status is True:
            #         is_refer = True
            #     updated_used_count = 0    
            #     if used_refer_count == 0 or used_refer_count == 1:
            #         updated_used_count = used_refer_count+ 1
            #         refers.used_count = updated_used_count
            #         refers.save()   
            job_count = jobs_grahak_machine + jobs_grahak_sahayak
            count_male = int(self.count_male) if self.count_male else 0
            count_female = int(self.count_female) if self.count_female else 0
            pay_amount_male = int(self.pay_amount_male) if self.pay_amount_male else 0
            pay_amount_female = int(self.pay_amount_female) if self.pay_amount_female else 0
            num_days = int(self.num_days) if self.num_days else 0
            
            # Extract the percentage value from fawda_fee_percentage field
            fawda_fee_percentage_str = self.fawda_fee_percentage.fawda_fee_percentage.rstrip('%')
            if job_count == 0:
                fawda_fee_percentage = 0
            # elif is_refer is True and (updated_used_count == 1 or updated_used_count == 2):
            #     fawda_fee_percentage = 1.25    
            else:
                fawda_fee_percentage = float(fawda_fee_percentage_str) if fawda_fee_percentage_str else 0
            print(fawda_fee_percentage)
            # calculate total amount without fawda_fee
            total_amount_without_fawda = (count_male * pay_amount_male + count_female * pay_amount_female) * num_days
            
            # calculate fawda_fee amount
            fawda_fee_amount = round(total_amount_without_fawda * (fawda_fee_percentage/ 100), 2)
            
            # calculate total amount with fawda_fee
            total_amount = round(total_amount_without_fawda + fawda_fee_amount, 2)
            
            # calculate payment_your amount
            # payment_your = round(total_amount_without_fawda - fawda_fee_amount, 2)
            
            # update the model fields
            self.fawda_fee_grahak = str(fawda_fee_amount)
            self.total_amount = str(total_amount)
            # self.payment_your = str(payment_your)
            self.total_amount_sahayak=str(total_amount_without_fawda)
            self.fawda_fee_percentage = self.fawda_fee_percentage  # update the original field value without percentage symbol
        if self.job_type == 'theke_pe_kam':
            jobs_grahak_sahayak = (JobSahayak.objects.filter(grahak=self.grahak)).count()
            jobs_grahak_machine = (JobMachine.objects.filter(grahak=self.grahak)).count()
            # check_refer = ReferCode.objects.filter(from_user=self.grahak_id)

            # is_refer = False
            # for refers in check_refer:
            #     refer_status = refers.is_refer_active
            #     used_refer_count = refers.used_count
            #     # print(used_refer_count)
            #     if refer_status is True:
            #         is_refer = True
            #     updated_used_count = 0    
            #     if used_refer_count == 0 or used_refer_count == 1:
            #         updated_used_count = used_refer_count+ 1
            #         refers.used_count = updated_used_count
            #         refers.save()   

            job_count = jobs_grahak_machine + jobs_grahak_sahayak
            total_amount_theka = int(self.total_amount_theka) if self.total_amount_theka else 0
            fawda_fee_percentage_str = self.fawda_fee_percentage.fawda_fee_percentage.rstrip('%')
            if job_count == 0:
                fawda_fee_percentage = 0
            # elif is_refer is True and (updated_used_count == 1 or updated_used_count == 2):
            #     fawda_fee_percentage = 1.25
            else :
                fawda_fee_percentage = float(fawda_fee_percentage_str) if fawda_fee_percentage_str else 0
            total_amount_without_fawda = total_amount_theka
            fawda_fee_amount = round(total_amount_without_fawda * (fawda_fee_percentage / 100), 2)
            total_amount = round(total_amount_without_fawda + fawda_fee_amount, 2)
            # payment_your = round(total_amount_without_fawda - fawda_fee_amount, 2)
            self.fawda_fee_grahak = str(fawda_fee_amount)
            # self.fawda_fee = str(fawda_fee_amount)
            self.total_amount = str(total_amount)
            # self.payment_your = str(payment_your)
            self.fawda_fee_percentage = self.fawda_fee_percentage  # update the original field value without percentage symbol
        super(JobSahayak, self).save(*args, **kwargs)





class JobMachine(models.Model):
    STATUS_TYPE_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Booked', 'Booked'),
        ('Ongoing','Ongoing'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
        ('Timeout','Timeout'),
        ('Cancelled-After-Payment','Cancelled-After-Payment')


    )
    LAND_TYPE_CHOICES=(
        ('Killa','Killa'),
        ('Bigha','Bigha'),
        ('None','None')
    )
    grahak=models.ForeignKey(User,on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)
    # time=models.TimeField()
    datetime= models.DateTimeField() 
    description=models.TextField(null=True,blank=True)
    land_type=models.CharField(max_length=10,choices=LAND_TYPE_CHOICES)
    job_type=models.CharField(max_length=20,default='machine_malik')
    status=models.CharField(max_length=50,choices=STATUS_TYPE_CHOICES,default='Pending')
    land_area=models.CharField(max_length=100,null=True,blank=True)
    total_amount=models.CharField(max_length=100, blank=True, null=True)
    fawda_fee=models.CharField(max_length=100,blank=True,null=True)
    fawda_fee_grahak=models.CharField(max_length=100,null=True,blank=True)
    fawda_fee_machine=models.CharField(max_length=100,null=True,blank=True)
    fawda_fee_percentage = models.ForeignKey(FawdaFee, on_delete=models.CASCADE, null=True, blank=True, default=1)
    total_amount_machine=models.CharField(max_length=100, blank=True, null=True)
    payment_your=models.CharField(max_length=100,blank=True,null=True)
    work_type=models.CharField(max_length=100,null=True,blank=True)
    machine=models.CharField(max_length=100,null=True,blank=True)
    # sowing=models.ForeignKey(Sowing,on_delete=models.CASCADE)
    others=models.CharField(max_length=500,null=True,blank=True)
    job_number=models.CharField(max_length=50,null=True,blank=True)
    is_first=models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.job_type},work_type:{self.work_type},machine:{self.machine}"
    
    def formatted_datetime(self):
        return self.datetime.strftime('%I:%M %p')
    
    def save(self, *args, **kwargs):
        if self.job_type == 'machine_malik':
            jobs_grahak_machine = (JobMachine.objects.filter(grahak=self.grahak)).count()
            jobs_grahak_sahayak = (JobSahayak.objects.filter(grahak=self.grahak)).count()
            # check_refer = ReferCode.objects.filter(from_user=self.grahak_id)
            # is_refer = False
            # for refers in check_refer:
            #     refer_status = refers.is_refer_active
            #     used_refer_count = refers.used_count
            #     # print(used_refer_count)
            #     if refer_status is True:
            #         is_refer = True
            #     updated_used_count = 0    
            #     if used_refer_count == 0 or used_refer_count == 1:
            #         updated_used_count = used_refer_count+ 1
            #         refers.used_count = updated_used_count
            #         refers.save() 
            
            job_count = jobs_grahak_machine + jobs_grahak_sahayak
            total_amount_machine = int(self.total_amount_machine) if self.total_amount_machine else 0
            fawda_fee_percentage_str = self.fawda_fee_percentage.fawda_fee_percentage.rstrip('%')
            if job_count == 0 :
                fawda_fee_percentage = 0
            # elif is_refer is True and (updated_used_count == 1 or updated_used_count == 2):
            #     fawda_fee_percentage = 1.25    
            else:
                fawda_fee_percentage = float(fawda_fee_percentage_str) if fawda_fee_percentage_str else 0
            total_amount_without_fawda = total_amount_machine
            fawda_fee_amount = round(total_amount_without_fawda * (fawda_fee_percentage / 100), 2)
            total_amount = round(total_amount_without_fawda + fawda_fee_amount, 2)
            # payment_your = round(total_amount_without_fawda - fawda_fee_amount, 2)
            # self.fawda_fee = str(fawda_fee_amount)
            self.fawda_fee_grahak = str(fawda_fee_amount)
            self.total_amount = str(total_amount)
            # self.payment_your = str(payment_your)
            self.fawda_fee_percentage = self.fawda_fee_percentage  # update the original field value without percentage symbol
            super(JobMachine, self).save(*args, **kwargs)





# from django.contrib.gis.geos import Point
# from django.contrib.gis.db.models.functions import Distance

# user_location = Point(user_longitude, user_latitude)
# distance_limit = 5000  # in meters
# jobs_within_range = Job.objects.annotate(
#     distance=Distance('job_location', user_location)
# ).filter(distance__lte=distance_limit)
