Range Calibration
=================

This application will manage the various tasks required to do the range calibration: including uploading and storing range measurements, calculations, and preparing html/pdf reports. The general procedure is:

1. A Landgate Surveyor (from Survey Services) will carry out regular measurements of the Boya Staff Calibration Range using a calibrated invar staff.  
2. The new range measurements are uploaded to the Staff Calibration website to update the range parameters (i.e., height differences between the existing pins in consecutive pairs: ``1-2, 2-3, 3-4, ..., 20-21``).
3. The web application will perform all the necessary computations required to update the range parameters and be able to calculate them and display them dynamically on button clicks.

The data processing flow is as follows:

* Each measurement is loaded and processed separately to determine the height differences between the pillars based on the repeat observations.
* Each measurement set consists of two sets of observations on a 3 metre Invar staff: i) At Pillar A (SSM MV 83) - From Pin 1 to Pins 2, 3,..., 15, and (ii) At Pillar B - From Pin 7 to Pins 8, 9,..., 21. Thus, there are two sets of observations for Pins 7, 8, ..., 15.    
* These staff readings (backsight, intermediate and foresights) are reduced to height differences between the Pins. 
* Repeat height differences (between Pins 7-8, 8-9,..., 14-15) are processed via weighted least squares method to determine the average height difference and their assocaited standard residuals to identify potential gross and systematic errors. 
* Temperature corrections are applied to each height difference to account for the temperature correction. 
* The adjustment results is stored by its staff number and date of measurement, e.g., YYYYMMDD_staffnumber. 
* As the Range is being rapidly monitored since 2018, we have at least two sets of measurements for each month (from Jan - December). And it will be continued to be monitored to determine any anomolous shifts in height differences and/or its established seasonal cycle. 
* Finally, the adjustment results are further processed to obtain an average height difference set for each month, which will be the reference dataset (referred here as *range parameters*) for calibrating other staves.   

In order to achieve the above requirements and procedures, the Range Calibration application will need:

1. **models** to store raw staff readings and adjustment results including foreign keys to the **accounts** and **staffs** application.
2. **forms** to upload range measurements and other metadata.
3. **views** to process range measurements and liaise between models and templates.
4. **URLs** to map the views to templates.
5. **templates** to render the views and adjustment results.
6. **initial migrations** to pre-load historical range measurement data.  

With the knowledge of how Django works and how models, views, URLs and templates are constructed, as well as the initial data migrations, its time to add the **Range Calibration** application to the website/project. As many of the features have been already explained when creating **staffs** and **accounts** app, this will be kept relatively short and will have the following file structure.

.. parsed-literal::

	staff/                                      <- application root folder
	│
	├──range_calibration/                       <- application name
	│  ├──migrations/                          
	│  │  ├──0001_initial.py
	│  │  ├──0002_auto_20201113_1350.py         <- pre-load historical range observations
	│  │  └──__init__.py	
	│  ├──templates                             <- html templates for sign up, login, and others
	│  │  └── range_calibration
	│  │  	  ├──staff_data_form_1.html
	│  │  	  ├──staff_data_form_2.html
	│  │  	  ├──adjustment_report.html
	│  │  	  ├──pdf_range_report.html
	│  │  	  ├──range_calibration_guide.html
	│  │  	  ├──range_calibration_home.html
	│  │  	  ├──range_parameters.html
	│  │  	  └──range_reading_report.html
	│  ├──admin.py
	│  ├──apps.py
	│  ├──forms.py
	│  ├──managers.py
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
   5_data_migrations





   
