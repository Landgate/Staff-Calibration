Django admin site
=================

Overview
--------

Django provides an ``admin`` application by default. The Admin site can use the *models* to automatically build a site, which can ``create``, ``view``, ``update``, and ``delete`` records in the database. However, access to this admin site should be restricted just for use by the system adminstrators and/or concerned people (e.g., geodetic team).

All the configuration required to include the admin application in the website was done automatically when the project was first created. This includes:

1. In the ``settings.py``:

	.. code-block:: python

		INSTALLED_APPS = [
		    'django.contrib.admin',
		    'django.contrib.auth',
		    'django.contrib.contenttypes',
		    'django.contrib.sessions',
		    ...,
		]
2. In the project ``urls.py``:
	
	.. code-block:: python

		urlpatterns = [
		    path('admin/', admin.site.urls),
		]

To access the models in the admin site, it needs to be *registered* using the ``admin.py`` found in the application folder (in this case, **/staffs/staff/**). 


Registering the models
----------------------

1. Open the ``admin.py`` in the *staffs* application (**/staff/staffs/admin.py**). The ``django.contrib.admin`` has been already imported here and has all the admin functions to give access to the models.

	.. code-block:: python

		from django.contrib import admin

		# Register your models here

2. Import the *staffs* models and register them using the ``admin.site.register`` function
	
	.. code-block:: python

		from django.contrib import admin
		from .models import Staff, StaffType, DigitalLevel    # import the models

		# Register your models here
		admin.site.register(Staff)
		admin.site.register(StaffType)
		admin.site.register(DigitalLevel)

Creating a ``superuser``
------------------------

In order to access the Admin site and get access to the models, the Admin site requires a *user account* who has the permission/authority to manage all objects in the site. In django, it can be achieved by creating a **superuser** via the ``manage.py`` in the command prompt. The *superuser* will have full access to the site and the required permissions to create, view, update and delete the objects and/or records. To create a superuser, 

1. In the command prompt, type:

	.. parsed-literal::
		
		python manage.py createsuperuser

2. It will ask for a username, email address, and a password. After inputting these information, restart the server to log into the site.
	
	 .. parsed-literal::
		
		python manage.py runserver


Logging into the Admin site
---------------------------

To access the admin site, open the */admin* URL (e.g., http://127.0.0.1:8000/admin) and enter the new superuser credentials (userid and password). Once logged in, the site will display all the models grouped by the installed applications. The ``superuser`` is found in the ``Users`` under **Authentication and Authorization**. Click on each model to view, update, create, or delete the records. 

.. figure::  django_admin_site.png
   :align:   center

   Django adminstration site. 


Model layout on Admin site
--------------------------

Create a couple of records in one of the models (e.g., DigitalLevel) by clicking on the model and clicking the *ADD DIGITAL LEVEL* button on the right. Using the methods in the ``models.py`` for the **DigitalLevel** model as

.. code-block:: Python
	
	# file name - models.py

	class DigitalLevel(models.Model):
		...

		def __str__(self):
			return f'{self.level_number} ({self.level_model})'  # level_number(level_model)


the admin site will display the list of digital levels as shown in the diagram below:


.. figure::  django_site_list_initial.png
   :align:   center

   Admin site showing the list of digital levels. 

To change how a model is displayed in the admin site, a ``ModelAdmin`` class (which describes the layout) should be defined and register it with the model in the ``admin.py``. For the example above, the list view can be improved by using the ``list_display`` inside the ``ModelAdmin`` as shown. Also, an ``ordering`` is added display the list in the order of ``level_make``. 

.. code-block:: python
	
	# filename - admin.py

	# Define the admin class
	class DigitalLevelAdmin(admin.ModelAdmin):
		list_display = ('level_number', 'level_make', 'level_model')
		ordering = ('level_make',)

	# Register the admin class and the model
	admin.site.register(DigitalLevel, DigitalLevelAdmin)

The list view now has the following look:

.. figure::  django_site_list_final.png
   :align:   center

   Admin site showing the list of digital levels after re-configurating the list view. 

When records get crowded, it is also useful to be able to filter the items by fields using the ``list_filter`` attribute. This is added similar to ``list_display`` and ``ordering`` with or without them. A **FILTER** functionality will be added in the admin site for the registered model. 

.. code-block:: python
	
	# Define the admin class
	class DigitalLevelAdmin(admin.ModelAdmin):
		list_display = ('level_number', 'level_make', 'level_model')
		ordering = ('level_make',)
		list_filter=('level_make',)
		
.. figure::  filter_added_admin_site.png
   :align:   center

   Admin site showing the list of digital levels after adding the ``list_filter`` attribute. 

Summary
-------

The list views of the other two models can configured in the same manner. The admin site list view will only display the fields included in the ``list_display`` and it is not necessary to include every field in the model. The other two models can be configured in the same way. 

Each application will have its own ``admin.py`` making it very convienent to manage the admin views specific to the application. For more information, refer to https://docs.djangoproject.com/en/3.1/ref/contrib/admin/. 
  