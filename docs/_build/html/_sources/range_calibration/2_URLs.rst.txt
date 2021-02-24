URL Mapping
===========

Overview
--------

Let's create a file called **urls.py** in the **range_calibration** app to map a number of ``view`` functions that will be defined next. The URL paths defined below will map each view function to one or multiple templates.

1. ``range-home`` renders the **range_calibration** home page
2. ``range_guide`` renders a template containing a guideline for calibrating the Boya Range
3. ``range-calibrate`` renders a class-based two-page form for processing the range measurements
4. ``range-adjust`` adjusts the range measurements
5. ``range-report`` renders the adjustment report it to a template  
6. ``print-report`` prints the adjustment report in a pdf format
7. ``range-parameters`` calculates the average monthly range values using all the adjusted measurement sets and renders the result in the form of a table and a bar chart to a template 
8. ``range_param_update`` updates the ``RangeParameters`` model when a new observation set is submitted/loaded and updates the ``range-parameter`` template. 

URLs
----

.. code-block:: python

	#filename: staff/range_calibration/urls.py

	from django.urls import path
	from . import views                                  # not defined yet
	from .forms import (                                 # not defined yet
	        RangeForm1,
	        RangeForm2,
	    )

	app_name = 'range_calibration'

	FORMS = [("prefill_form", RangeForm1),
	         ("upload_data", RangeForm2),
	        ]         

	urlpatterns = [
	    path('', views.HomeView.as_view(), name='range-home'),
	    path('guide', views.guide_view, name='range-guide'),
	    path('range_calibrate/', views.RangeCalibrationWizard.as_view(FORMS), name='range-calibrate'),
	    path('range_adjust/<update_index>/', views.range_adjust, name='range-adjust'),
	    path('range_report/<update_index>/', views.range_report, name='range-report'),
	    path('print_report/<update_index>/', views.print_report, name='print-report'),
	    path('range_parameters/',views.range_parameters, name='range-parameters'),
	    path('range_param_update/',views.update_range_param, name='range_param_update'),
	    
	    ]


