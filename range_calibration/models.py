from django.db import models
from datetime import date
from staffs.models import (
                            Staff,
                            DigitalLevel,
                            )
from accounts.models import CustomUser
# Create your models here.


# Calibration update
class Calibration_Update(models.Model):
    staff_number = models.ForeignKey(Staff, on_delete = models.CASCADE, blank = True, null=True)
    level_number =  models.ForeignKey(DigitalLevel, on_delete = models.CASCADE, blank = True, null=True)
    surveyor = models.ForeignKey(CustomUser, 
                        default = 1, 
                        null = True,  
                        on_delete = models.SET_NULL 
                        ) 
    observation_date = models.DateField()
    update_table = models.BooleanField(null = True, blank=True)
    # Unique Index
    update_index = models.CharField(max_length=100, primary_key=True)
    
    class Meta:
        ordering = ['observation_date']
        indexes = [
            models.Index(fields=['update_index']), 
        ]
    
    def __str__(self):
        return f'{self.observation_date.strftime("%Y-%m-%d"), (self.staff_number.staff_number)}'
    
    def save(self, *args, **kwargs):
        self.update_index =  self.observation_date.strftime('%Y%m%d')+'-'+self.staff_number.staff_number
        super(Calibration_Update, self).save(*args, **kwargs)
    # @property
    # def update_index(self):
    #     return '%s-%s' % (self.observation_date.strftime("%Y%m%d"), self.staff_number.staff_number)

# Raw data model
class RawDataModel(models.Model):
    staff_number = models.CharField(max_length=20)
    observation_date = models.DateField()
    obs_set = models.IntegerField(null=True)
    pin = models.CharField(max_length=20)
    temperature = models.FloatField(null=True)
    frm_pin = models.FloatField(null=True)
    to_pin = models.FloatField(null=True)
    standard_deviation = models.FloatField(null=True)
    observed_ht_diff = models.FloatField(null=True)
    corrected_ht_diff = models.FloatField(null=True)
    # Unique Index
    update_index = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['observation_date']
    
    def __str__(self):
        return self.update_index

# Adjustment data model
class AdjustedDataModel(models.Model):
    update_index = models.CharField(max_length=50)
    observation_date = models.DateField()
    pin = models.CharField(max_length=20)
    adjusted_ht_diff = models.FloatField(null=True)
    observed_ht_diff = models.FloatField(null=True)
    residuals = models.FloatField(null=True)
    standard_deviation = models.FloatField(null=True)
    std_dev_residual = models.FloatField(null=True)
    standard_residual = models.FloatField(null=True)
    
    class Meta:
        ordering = ['observation_date']

    def __str__(self):
        return self.update_index

# Adjusted height difference data model
class HeightDifferenceModel(models.Model):
    update_index = models.CharField(max_length=50)
    observation_date = models.DateField()
    pin = models.CharField(max_length=20)
    adjusted_ht_diff = models.FloatField(null=True)
    uncertainty = models.FloatField(null=True)
    observation_count = models.FloatField(null=True)
    
    class Meta:
        ordering = ['observation_date']

    def __str__(self):
        return self.update_index
    
# Boya Range Parameters
class RangeParameters(models.Model):
    pin = models.CharField(max_length=10, primary_key=True)
    Jan = models.FloatField(null=True)
    Feb = models.FloatField(null=True)
    Mar = models.FloatField(null=True)
    Apr = models.FloatField(null=True)
    May = models.FloatField(null=True)
    Jun = models.FloatField(null=True)
    Jul = models.FloatField(null=True)
    Aug = models.FloatField(null=True)
    Sep = models.FloatField(null=True)
    Oct = models.FloatField(null=True)
    Nov = models.FloatField(null=True)
    Dec = models.FloatField(null=True)
    
    def __str__(self):
        return self.pin
