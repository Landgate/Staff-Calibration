URL Mapping
===========

Overview
--------

Let's create a file called **urls.py** in the **staff_calibration** app to map a number of ``view`` functions that will be defined next. The URL paths defined below will map each view function to one or multiple templates.

1. ``staff-home`` renders the **staff_calibration** home page
2. ``staff_guide`` renders a template containing a guideline for calibrating levelling staves on Boya Range
3. ``range-calibrate`` renders a form for submitting and processing the calibration
4. ``generate-report`` renders the staff calibration report in a pdf format  

URLs
----

.. code-block:: python

	#filename: staff/staff_calibration/urls.py

	from django.urls import path
	from . import views

	app_name = 'staff_calibration'

	urlpatterns = [
	    path('', views.homeview, name="staff-home"),
	    path('staff_guide/', views.guideview, name="staff-guide"),
	    path('staff_calibrate/', views.calibrate, name="staff-calibrate"),
	    path('generate_report/<update_index>/', views.generate_report_view, name='generate-report'),
	    path('<update_index>/delete', views.user_staff_delete, name = 'user-staff-delete'),
	]


