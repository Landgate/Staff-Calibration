from django.db import models
from django.urls import reverse
from django.core.validators  import MaxValueValidator, MinValueValidator
from django.conf import settings
# Create your models here.
User = settings.AUTH_USER_MODEL 
from accounts.models import CustomUser
from accounts.models import Authority

class StaffType(models.Model):
    staff_type = models.CharField(max_length=25,help_text="e.g., Invar, Fibre glass", unique=True)
    thermal_coefficient = models.FloatField(help_text="Staff coefficient in ppm")
    added_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)
    
    def get_absolute_url(self):
        return reverse('staffs:stafftype-detail', args=[str(self.id)])

    def __str__(self):
        return self.staff_type
    
class Staff(models.Model):
    user = models.ForeignKey(CustomUser, 
                        null = True,
                        blank = True,   
                        on_delete = models.SET_NULL,
                        ) 
    staff_number = models.CharField(max_length=15, 
                                    help_text="Staff serial number", 
                                    unique=True,
                                    )
    staff_type = models.ForeignKey(StaffType, on_delete = models.SET_NULL, null = True)
    staff_length = models.FloatField(
        validators = [MinValueValidator(1.0), MaxValueValidator(7.0)], 
        help_text="Staff length in meters")
    standard_temperature = models.FloatField(default=25.0)
    correction_factor = models.FloatField(null=True, blank=True)
    calibration_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering= ['staff_number', '-calibration_date']
    
    def __str__(self):
        return f'{self.staff_number, (self.staff_type.staff_type)}'
        # return f'{self.calibration_date.strftime("%Y-%m-%d"), self.staff_number({self.staff_type})}'

    #def get_absolute_url(self):
    #    return reverse('staffs:staff-detail', args=[str(self.id)])

class DigitalLevel(models.Model):
    user = models.ForeignKey(CustomUser,   
                        null = True,
                        blank = True,   
                        on_delete = models.SET_NULL,
                        ) 
    level_number = models.CharField(max_length=15, help_text="Enter the instrument serial number", unique=True)
    level_make = models.CharField(max_length=15, help_text="e.g., Leica")
    level_model = models.CharField(max_length=15, help_text="e.g., LS15 or DNA03")

    class Meta:
        ordering = ['level_number','level_make']
    
    def get_absolute_url(self):
        return reverse('staffs:level-detail', args=[str(self.id)])
    
    def __str__(self):
        return f'{self.level_number} ({self.level_model})'   
    
