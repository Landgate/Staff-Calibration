Staff Calibration
=================

This is the primary objective of this web application, i.e., to calibrate digital levelling staves using calibrated range measurements on the Boya Staff Calibration Range. It will also enable a more robust system of calibration by taking into account the possible seasonal anomaly.

The general field procedure and data processing will be as follows:

1. Landgate carries out regular measurements of the Boya Range using a calibrated invar staff to update the range parameters.
2. Any Surveyor or any one wishing to calibrate their levelling staff are required to do at least one set of observation on the Range. This involves setting up the digital level on Pillar A (MV 83) and recording several rounds of staff readings at each pins from Pin 1 to Pin 21 depending on the length of the staff.  
3. Download the observation set and prepare them into a csv/ascii file. 
4. Submit the data and generate the calibration report. 

To achieve step (4), we will create a separate application called **staff_calibration** using the ``manage.py startapp``. The application will have the following outlook: 

.. parsed-literal::

	staff/                                      <- application root folder
	│
	├──staff_calibration/                       <- application name
	│  ├──migrations/                          
	│  │  ├──0001_initial.py
	│  │  └──__init__.py	
	│  ├──templates                             
	│  │  └── staff_calibration
	│  │  	  ├──staff_calibrate.html           <- form
	│  │  	  ├──staff_calibration_guide.html   <- guide
	│  │  	  ├──staff_calibration_home.html    <- homepage
	│  │  	  ├──staff_calibration_report.html  <- calibration report in html format
	│  │  	  ├──pdf_staff_report.html          <- calibration pdf report template
	│  │  	  ├──staff_calibration_completion_email.html <- email notification of new staff calibration update
	│  │  	  └──user_staff_lists.html          <- list of calibration reports
	│  ├──admin.py
	│  ├──apps.py
	│  ├──forms.py
	│  ├──models.py
	│  ├──tests.py
	│  ├──urls.py
	│  ├──views.py
	│  └──__init__.py

.. toctree::
   :maxdepth: 4

   0_settings
   1_models
   2_URLs
   3_forms
   4_views
   5_other_pages





   
