Models
======

Overview
--------

The Staff Calibration application will need to store the raw data, the adjustments, and the corrections associated with the staves, and they should always be associated to the users. 

The models defined in this application include:

* ``uCalibrationUpdate`` - link to **staffs** and **accounts** models plus few other additions
* ``uRawDataModel`` - store raw staff readings

Adjustments are not stored as they are done on button click. 

uCalibrationUpdate
------------------

.. code-block:: python

	#filename: staff/staff_calibration/models.py

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

RawDataModel
------------

Raw measurements are stored like this:

+--------------+--------------+------------------+------------+----------------+-------------------+----------------+---------+
| unique_index | staff_number | calibration_date | pin_number |  staff_reading | number_of_reading | std_deviations | user_id | 
+==============+==============+==================+============+================+===================+================+=========+
|20180111-209  |    209       |    2018-01-11    |    1       |   0.07082      |        10         |   1.0e-05      |     1   |
+--------------+--------------+------------------+------------+----------------+-------------------+----------------+---------+
|20180111-209  |    209       |    2018-01-11    |    2       |   0.16173      |        10         |   1.0e-05      |     1   |
+--------------+--------------+------------------+------------+----------------+-------------------+----------------+---------+
|20180111-209  |    209       |    2018-01-11    |    3       |   0.32593      |        10         |   1.0e-05      |     1   |
+--------------+--------------+------------------+------------+----------------+-------------------+----------------+---------+
|20180111-209  |    209       |    2018-01-11    |    4       |   0.47206      |        10         |   3.0e-05      |     1   |
+--------------+--------------+------------------+------------+----------------+-------------------+----------------+---------+
|20180111-209  |    209       |    2018-01-11    |    5       |   0.68494      |        10         |   2.0e-05      |     1   |
+--------------+--------------+------------------+------------+----------------+-------------------+----------------+---------+
|20180111-209  |    209       |    2018-01-11    |    6       |   0.87108      |        10         |   1.0e-05      |     1   |
+--------------+--------------+------------------+------------+----------------+-------------------+----------------+---------+
|20180111-209  |    209       |    2018-01-11    |    7       |   1.0709       |        10         |   1.0e-05      |     1   |
+--------------+--------------+------------------+------------+----------------+-------------------+----------------+---------+
|20180111-209  |    209       |    2018-01-11    |    8       |   1.27582      |        10         |   1.0e-05      |     1   |
+--------------+--------------+------------------+------------+----------------+-------------------+----------------+---------+
|20180111-209  |    209       |    2018-01-11    |    9       |   1.52320      |        10         |   3.0e-05      |     1   |
+--------------+--------------+------------------+------------+----------------+-------------------+----------------+---------+
|20180111-209  |    209       |    2018-01-11    |    10      |   1.79073      |        10         |   1.0e-05      |     1   |
+--------------+--------------+------------------+------------+----------------+-------------------+----------------+---------+

by defining a model called ``uRawDataModel``:

.. code-block:: python
	
	#filename: staff/staff_calibration/models.py
	
	...

	# Raw data model to store the raw staff readings in the same way as the table shown above
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


