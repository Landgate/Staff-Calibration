Building the models
===================

Overview
--------

Django web applications access and manage data through Python objects referred to as models. Models define the structure of stored data, including the field types and possibly also their maximum size, default values, selection list options, help text for documentation, label text for forms, etc. The definition of the model is independent of the underlying database (see ``settings.py``) and django officially supports *SQLite*, *PostgreSQL*, *MariaDB*, *MySQL*, and *Oracle* at the time of this writing (see details on https://docs.djangoproject.com/en/3.1/ref/databases/).

Designing the **staffs** models
-------------------------------

In this Staff Calibration project/website, the **staffs** application is designed to deal with all the functions related to the levelling instruments - inlcuding staves and digital levels. It will store all the relevant information required for calibrating a staff and is able to display/print the individual calibration results for each staff calibrated. With this in mind, the **staffs** model design is built according to the following diagram.

.. figure::  staffs_model.png
   :align:   center

   Design of the **staffs** models. 

The **staffs** application is made up of three models (i.e., ``Staff``, ``StaffType``, and ``DigitalLevel``) and the ``Staffs`` and ``DigitalLevel`` are linked to the **User** using the ``ForeignKey`` method. 

Defining the models
-------------------

Models are usually defined in an application's ``models.py`` file, which is automatically generated when the **staffs** application was created via ``manage.py startapp staffs``. Models can include fields, methods, and metadata. Excluding the User model, the above model design is implemented in the ``staff/staffs/models.py`` as follows:

.. code-block:: python

	from django.db import models
	from django.urls import reverse
	from django.core.validators import MaxValueValidator, MinValueValidator
	
	# Create your models here.

	class StaffType(models.Model):
	    staff_type = models.CharField(max_length=25,help_text="e.g., Invar, Fibre glass", unique=True)
	    thermal_coefficient = models.FloatField(help_text="Staff coefficient in ppm")
	    
	    def get_absolute_url(self):
	        return reverse('staffs:stafftype-detail', args=[str(self.id)])

	    def __str__(self):
	        return self.staff_type
	    
	class Staff(models.Model):
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

	class DigitalLevel(models.Model):
	    level_number = models.CharField(max_length=15, help_text="Enter the instrument serial number", unique=True)
	    level_make = models.CharField(max_length=15, help_text="e.g., Leica")
	    level_model = models.CharField(max_length=15, help_text="e.g., LS15 or DNA03")

	    class Meta:
	        ordering = ['level_number','level_make']
	    
	    def get_absolute_url(self):
	        return reverse('staffs:level-detail', args=[str(self.id)])
	    
	    def __str__(self):
	        return f'{self.level_number} ({self.level_model})'   

Model Fields
------------

A model can have any number of fields, of any type. Each field represents a column in a database table and the values are stored as records (or rows). For example, ``staff_number`` field is defined as

.. code-block:: Python

	staff_number = models.CharField(max_length=15, 
	                                help_text="Staff serial number", 
	                                unique=True)

``staff_number`` is a *string field* defined by the ``models.CharField`` and will contain strings of alphanumeric characters. The field type has the following arguments:

* ``max_length=20`` - maximum length of 20 characters
* ``help_text="Staff Serial Number"`` - a text label to display to help users know what to provide
* ``unique=True`` - indicating that it will only hold one record for that staff_number

Other field arguments include:

* ``verbose_name`` - a human-readable name for the field used in field labels
* ``default`` - a default value for the field
* ``null`` - if ``True``, django will store blank values as ``NULL``
* ``blank`` - if ``True``, the field is allowed to be blank in forms. 
* ``choices`` - a set of choices for this field
* ``primary_key`` - if ``True``, sets the field as primary key for the model. If not specified, django will automatically add a field for this purpose.

Model field types commonly include:

* ``TextField`` - used for large arbitary-length string. 
* ``IntegerField`` - used for integer values 
* ``DateField`` and ``DateTimeField`` - used for dates and date/time. Additional parameters include ``auto_now=True`` (set to current date/time, ``auto_now_add`` (set the date the model was first created), and default (set a default date))
* ``EmailField`` - used for emails
* ``FileField`` and ``ImageField`` - used for files and images respectively
* ``ForeignKey`` - used to specify one-to-many relationship to another database model (e.g., a staff may be of any type - invar, fibreglass, steel)

For more information, refer to https://docs.djangoproject.com/en/3.1/ref/models/fields/. 

Metadata
--------

Metadata in a django model is "anything that’s not a field", such as ordering options (``ordering``), database table name (``db_table``), or human-readable singular and plural names (``verbose_nam``e and ``verbose_name_plural``). This is done by adding a ``class Meta`` to the model but it is completely optional. The ``Staff`` model has a ``ordering`` option applied to the records to display them by staff_number (ascending order) and calibration date (latest date - descending order). 

.. code-block:: Python

	class Meta:
	        ordering= ['staff_number', '-calibration_date']    # order by staff number (ascending) and calibration date (latest date at the top)

Methods
-------

Models can have methods to add "row-level" functionality to the class object. For the ``DigitalLevel`` model, two methods are provided.

.. code-block:: python

	class DigitalLevel(models.Model):
		...

	    class Meta:
	        ...
	    
	    def get_absolute_url(self):
	        return reverse('staffs:level-detail', args=[str(self.id)])
	    
	    def __str__(self):
	        return f'{self.level_number} ({self.level_model})'   

1. ``get_absolute_url()`` returns the URL mapping for rendering the invidual model records in a html file
2. ``__str__`` returns a human-readable string for the class object. Without this method, it will be almost impossible to understand what the class object (or model) is about. 

Re-running the database migrations
----------------------------------

After creating the three models, it is time to add them to the database. This is done by running the migration commands

.. code-block:: python

	python manage.py makemigrations
	python manage.py migrate

Output of ``makemigrations``:

.. parsed-literal::
	Migrations for 'staffs':
	  staffs\migrations\0001_initial.py
	    - Create model DigitalLevel
	    - Create model StaffType
	    - Create model Staff

Output of ``migrate``:

.. parsed-literal::
	Operations to perform:
	  Apply all migrations: admin, auth, contenttypes, sessions, staffs
	Running migrations:
	  Applying contenttypes.0001_initial... OK
	  Applying auth.0001_initial... OK
	  Applying admin.0001_initial... OK
	  Applying admin.0002_logentry_remove_auto_add... OK
	  Applying admin.0003_logentry_add_action_flag_choices... OK
	  Applying contenttypes.0002_remove_content_type_name... OK
	  Applying auth.0002_alter_permission_name_max_length... OK
	  Applying auth.0003_alter_user_email_max_length... OK
	  Applying auth.0004_alter_user_username_opts... OK
	  Applying auth.0005_alter_user_last_login_null... OK
	  Applying auth.0006_require_contenttypes_0002... OK
	  Applying auth.0007_alter_validators_add_error_messages... OK
	  Applying auth.0008_alter_user_username_max_length... OK
	  Applying auth.0009_alter_user_last_name_max_length... OK
	  Applying auth.0010_alter_group_name_max_length... OK
	  Applying auth.0011_update_proxy_permissions... OK
	  Applying auth.0012_alter_user_first_name_max_length... OK
	  Applying sessions.0001_initial... OK
	  Applying staffs.0001_initial... OK

	  