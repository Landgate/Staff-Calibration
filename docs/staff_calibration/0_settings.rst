Settings
========

Project settings
----------------

1. project **staff/staff/settings.py**:

	.. code-block:: python

		#filename: staff/staff/settings.py

		... 

		INSTALLED_APPS = [
			...
			'staff_calibration',           # this application
		]

2. project **staff/staff/urls.py**: 
	
	.. code-block:: python

		urlpatterns = [
		    ...
		    path('staff_calibration/', include('staff_calibration.urls')),
		]


