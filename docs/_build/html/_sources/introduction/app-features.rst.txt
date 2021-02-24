The Staff Calibration Project
=================================

Project outlook
---------------

The staff calibration application must have the following features:

1. A login system for the users to manage levelling staves and calibration
2. An administrator account (``superuser``) system to manage the application (create, add, update and delete)
3. A staff account to manage the range calibration
4. A data migration plan to load all the existing information in order to avoid loading the data again and again through the portal. 

In brief, the user logs into the application, adds the levelling instruments (staves, levels), calibrate the staves, and generates the calibration report (as a pdf file). The user should be able to see all the level instruments and calibration details, including those entered by others working for the same company/firm. 

The staff account holder (Survey Services, Landgate) logs into the application and should have the added **Range Calibration** section to carry out range calibration and update the reference range measurement. 


Design of the staff calibration project
---------------------------------------

.. figure::  staff_calibration_project.png
   :align:   center

   Design of the staff calibration project.

In consideration of the above, the Staff Calibration Application has four modules (also called apps in django terms) as provided below and described in the figure above.

1. The "accounts" app manages the user accounts, registration, login and logouts. 

2. The "staffs" app manages and maintains the records of levelling staves and level instruments. Users must be logged in to add new records or update existing records. Landgate staves and levelling instruments having measurement records until September 30, 2020 and related to this project have been added automatically during data migration. 

3. The "range_calibration" app manages the range calibration dataset and the computations required to calculate the height differences between the consecutive pins. The module also computes and/or updates the height differences between the pins for each month (January to December) by averaging all the range observations conducted from January 2018. The updated range then becomes the reference data for calibrating the staves. The behaviour of the Boya Staff Calibration range is depicted by a chart in the home page. 

4. The "staff_calibration" app is the principle driver behind developing this application. Through a least squares adjustment of reference values (from 3) and staff readings (using their own staff) submitted by the user, the module computes scalar derivative called a scale factor, which is then applied as a multiplicative fator on the height differences meausred by that particular user staff. Additionally, the app also manages the staff calibration records.  

The app aministrator/manager can login into the admin page (...../landgate) to manage one or all of the backend components of the application. The app adminstrator/manager has the privilledge to add/update/delete one or all of the records related to the above. 

Staff Calibration - Django project design
-----------------------------------------

The staff calibration application with the name **staff** is set up as follows:

.. parsed-literal::
	staff/                                       <- application root folder
	├── manage.py
	├── staff/                                   <- application settings folder
	|  ├──asgi.py
	|  ├──passwordValidators.py
	|  ├──settings.py
	|  ├──urls.py
	|  ├──views.py
	|  ├──wsgi.py
	│  └──__init__.py
	├── accounts/                                <- accounts app with user custom model
	│	├── migrations/                          <- data migration with preload
	│	│	├── 0001_initial.py
	│	│	├──	0002_auto_20201110_0811.py
	│	│	├──	0003_auto_20201112_0820.py
	│	│	└──	__init__.py	
	│	├── templates                            <- html templates for sign up, login, and others
	│	│	└── accounts
	│	│		├── accounts_home.html
	│	│		├──	login.html
	│	│		├──	signup.html
	│	│		├──	user_list_view.html
	│	│		└──	user_profile.html
	│	├──	admin.py
	│	├──	apps.py
	│	├──	forms.py
	│	├──	managers.py
	│	├──	models.py
	│	├──	tests.py
	│	├──	token_generator.py
	│	├──	urls.py
	│	├──	views.py
	│	└──	__init__.py
	├── staffs/                                  <- staffs app - create, update, delete staves/other instruments
	│	├── migrations/                          <- data migration with preload of landgate instruments
	│	│	├── 0001_initial.py
	│	│	├──	0002_auto_20201112_1023.py
	│	│	├──	0003_auto_20201126_1507.py
	│	│	└──	__init__.py	
	│	├── templates                            <- html templates relating to staves/other levelling instruments
	│	│	└── staffs
	│	│		├── stafftype_create.html
	│	│		├──	stafftype_list.html
	│	│		├──	stafftype_update.html
	│	│		└── ... more...
	│	├──	admin.py
	│	├──	apps.py
	│	├──	forms.py
	│	├──	managers.py
	│	├──	models.py
	│	├──	tests.py
	│	├──	urls.py
	│	├──	views.py
	│	└──	__init__.py
	├── range_calibration                        <- range_calibration app - for calibrating the Boya Range
	│	├── migrations ....                      <- data migration with preload of range measurements
	│	├── templates ....
	│	└── more .... 
	├── staff_calibration                        <- staff_calibration app - for calibrating staves
	│	├── migrations ....
	│	├── templates ....
	│	└── ... more...
	├── assets                                   <- static files - css/js/images/data
	│	├── ..css/..js
	│	├── logo
	│	├── images
	│	└── ... more ...
	├── data                                     <- range data for preloaded
	│	└── range_data 
	├── templates                                <- general templates directory inlcuding base template and accounts
	│	├── registrations
	│	│	├──	activate_account.html
	│	│	├──	activation_sent.html
	│	│	├──	password_reset_complete.html
	│	│	├──	password_reset_confirm.html
	│	│	├──	password_reset_done.html
	│	│	├──	password_reset_email.html
	│	│	└──	password_reset_form.html
	│	├──	password_reset_email.htmlbase_generic.html
	│	└──home_page.html
	├── .gitignore                               <- git ignore list - list of files/folders to be ignored for production
	├── .venv                                    <- python virtual environement - holding modules only required for this
	├── docs                                     <- documentation
	│	└── ... more...              
	├── db.sqlite3                               <- database
	├── LICENSE      
	├── Procfile                                 <- list of commands executed by the app on startup - required for Heroku
	├── README.md
	├── requirements.txt                         <- list of python modules (i.e., those installed in the .venv)
	└── runtime.txt	                             <- text file specifying the python version