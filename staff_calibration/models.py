from django.db import models
from django.utils import timezone
from django.conf import settings

# import user models
from staffs.models import Staff, DigitalLevel
from accounts.models import CustomUser

# Create your models here.

class uCalibrationUpdate(models.Model):
    user = models.ForeignKey(CustomUser, 
                        default = 1, 
                        null = True,  
                        on_delete = models.SET_NULL 
                        ) 
    submission_date = models.DateTimeField(default=timezone.now)
    staff_number = models.ForeignKey(Staff, on_delete=models.CASCADE, blank = True, null=True)
    level_number = models.ForeignKey(DigitalLevel, on_delete=models.CASCADE, blank = True, null=True)
    calibration_date = models.DateField()
    processed_date = models.DateTimeField()
    correction_factor = models.FloatField()
    observed_temperature = models.FloatField()
    observer = models.CharField(max_length=100, blank=True, null=True)
    correction_factor_temperature = models.FloatField()
    
    # Unique Index
    update_index = models.CharField(max_length=100, primary_key=True)
    
    class Meta:
        ordering = ['-calibration_date']
        indexes = [
            models.Index(fields=['update_index']), 
        ]
    
    def __str__(self):
        return f'{self.calibration_date.strftime("%Y-%m-%d"), (self.staff_number.staff_number)}'
    
    def save(self, *args, **kwargs):
        self.update_index =  self.calibration_date.strftime('%Y%m%d')+'-'+self.staff_number.staff_number
        super(uCalibrationUpdate, self).save(*args, **kwargs)

# Raw data model
class uRawDataModel(models.Model):
    user = models.ForeignKey(CustomUser, 
                        default = 1, 
                        null = True,  
                        on_delete = models.SET_NULL 
                        ) 
    staff_number = models.CharField(max_length=20)
    calibration_date = models.DateField()
    pin_number = models.IntegerField(null=True)
    staff_reading = models.FloatField(null=True)
    number_of_readings = models.IntegerField(null=True)
    standard_deviations = models.FloatField(null=True)
    # Unique Index
    update_index = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['calibration_date']
        indexes = [
            models.Index(fields=['update_index']), 
        ]
    
    def save(self, *args, **kwargs):
        self.update_index =  "%s-%s" % (self.calibration_date.strftime('%Y%m%d'), self.staff_number)
        super(uRawDataModel, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.update_index

    
    
    
