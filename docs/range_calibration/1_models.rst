Models
======

Overview
--------

The Range Calibration application will need to store the raw range data, the adjustments, adjusted height differences, and the range parameters (i.e., the monthly average range), associations to the **staffs** and **accounts** application, and other important metadata required. 

The models defined in this application include:

* ``Calibration_Update`` - link to **staffs** and **accounts** models plus few other additions
* ``RawDataModel`` - store raw staff readings
* ``AdjustedDataModel`` - store the adjustement
* ``HeightDifferenceModel`` - store the adjusted height differences
* ``RangeParameters`` - store the monthly average values

Calibration_Update
------------------

.. code-block:: python

	#filename: staff/range_calibration/models.py

	from django.db import models
	from datetime import date

	# import relevant models from the staffs application
	from staffs.models import (
	                            Staff,
	                            DigitalLevel,
	                            )
	# import user model
	from accounts.models import CustomUser

	# Create your models here.

	# This model enables link between this application, the user, and the staffs application and allows smooth update of the staff calibration table
	class Calibration_Update(models.Model):
	    staff_number = models.ForeignKey(Staff, on_delete = models.CASCADE, blank = True, null=True)
	    level_number =  models.ForeignKey(DigitalLevel, on_delete = models.CASCADE, blank = True, null=True)
	    surveyor = models.ForeignKey(CustomUser, 
	                        default = 1, 
	                        null = True,  
	                        on_delete = models.SET_NULL 
	                        ) 
	    observation_date = models.DateField()
	    # check if the range measurement is processed and included in the RangeParameters table    
	    update_table = models.BooleanField(null = True, blank=True)

	    # Unique Index to identify this observation set
	    update_index = models.CharField(max_length=100, primary_key=True)
	    
	    class Meta:
	        ordering = ['observation_date']
	        indexes = [
	            models.Index(fields=['update_index']), 
	        ]
	    
	    def __str__(self):
	        return f'{self.observation_date.strftime("%Y-%m-%d"), (self.staff_number.staff_number)}'
	    
	    # Auto-update the Unique Index by its date of observation and staff_number
	    def save(self, *args, **kwargs):
	        self.update_index =  self.observation_date.strftime('%Y%m%d')+'-'+self.staff_number.staff_number
	        super(Calibration_Update, self).save(*args, **kwargs)

RawDataModel
------------

Raw measurements are stored like this:

+--------------+--------------+------------------+---------+------+-------------+---------+--------+-----------+------------------+-------------------+
| unique_index | staff_number | observation_date | obs_set |  pin | temperature | frm_pin | to_pin | std_dev   | observed_ht_diff | corrected_ht_diff | 
+==============+==============+==================+=========+======+=============+=========+========+===========+==================+===================+
|20180111-26296|    26296     |    2018-01-11    |    1    | 1-2  |   22.0      | 0.07242 | 0.16331|   1.4e-05 |     0.09089      |        0.09089    |
+--------------+--------------+------------------+---------+------+-------------+---------+--------+-----------+------------------+-------------------+
|20180111-26296|    26296     |    2018-01-11    |    1    | 2-3  |   22.0      | 0.16331 | 0.32727|   1.4e-05 |     0.16396      |        0.16396    |
+--------------+--------------+------------------+---------+------+-------------+---------+--------+-----------+------------------+-------------------+
|20180111-26296|    26296     |    2018-01-11    |    1    | 3-4  |   22.0      | 0.32727 | 0.47334|   1.4e-05 |     0.14607      |        0.14607    |
+--------------+--------------+------------------+---------+------+-------------+---------+--------+-----------+------------------+-------------------+
|20180111-26296|    26296     |    2018-01-11    |    1    | 4-5  |   22.0      | 0.47334 | 0.68633|   1.4e-05 |     0.21299      |        0.21299    |
+--------------+--------------+------------------+---------+------+-------------+---------+--------+-----------+------------------+-------------------+
|20180111-26296|    26296     |    2018-01-11    |    1    | 5-6  |   22.0      | 0.68633 | 0.87255|   1.4e-05 |     0.18622      |        0.18622    |
+--------------+--------------+------------------+---------+------+-------------+---------+--------+-----------+------------------+-------------------+
|20180111-26296|    26296     |    2018-01-11    |    1    | 6-7  |   22.0      | 0.87255 | 1.07230|   1.4e-05 |     0.19975      |        0.19975    |
+--------------+--------------+------------------+---------+------+-------------+---------+--------+-----------+------------------+-------------------+
|20180111-26296|    26296     |    2018-01-11    |    1    | 7-8  |   22.0      | 1.07230 | 1.27736|   1.4e-05 |     0.20506      |        0.20506    |
+--------------+--------------+------------------+---------+------+-------------+---------+--------+-----------+------------------+-------------------+
|20180111-26296|    26296     |    2018-01-11    |    1    | 8-9  |   22.0      | 1.27736 | 1.52421|   1.4e-05 |     0.24685      |        0.24685    |
+--------------+--------------+------------------+---------+------+-------------+---------+--------+-----------+------------------+-------------------+
|20180111-26296|    26296     |    2018-01-11    |    1    | 9-10 |   22.0      | 1.52421 | 1.79183|   1.4e-05 |     0.26762      |        0.26762    |
+--------------+--------------+------------------+---------+------+-------------+---------+--------+-----------+------------------+-------------------+
|20180111-26296|    26296     |    2018-01-11    |    1    | 10-11|   22.0      | 1.79183 | 2.12494|   1.4e-05 |     0.33311      |        0.33311    |
+--------------+--------------+------------------+---------+------+-------------+---------+--------+-----------+------------------+-------------------+

by defining a model called ``RawDataModel``:

.. code-block:: python
	
	#filename: staff/range_calibration/models.py
	
	...

	# Raw data model to store the raw staff readings in the same way as the table shown above
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

AdjustedDataModel
-----------------

Adjustment results are stored like this:

.. figure:: adjustment_table.png
	:align: center

by defining a model called ``AdjustedDataModel``:

.. code-block:: python
	
	#filename: staff/range_calibration/models.py
	
	...

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

HeightDifferenceModel
---------------------

This model will store the adjusted height differences and the measurement uncertainties between the pins, which looks like this in a pdf report:

.. figure:: height_difference_table.png
	:align: center

This is achieved by defining a model called ``HeightDifferenceModel``:

.. code-block:: python
	
	#filename: staff/range_calibration/models.py
	
	...

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

Note that the ``unique_index`` and ``observation_date`` are not shown in the pdf report but are stored in the table as key parameters. 


RangeParameters
---------------

``RangeParameters`` consists of the final range values or the height differences between the pins calculated for each month from January to December. These values will be updated every time a new measurement set is loaded and processed. The table looks like this:

.. figure:: range_parameter_table.png
	:align: center

This is done by defining a modell called ``RangeParameters`` as shown below:

.. code-block:: python
	
	#filename: staff/range_calibration/models.py
	
	...

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

