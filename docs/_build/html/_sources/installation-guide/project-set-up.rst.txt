Creating the Staff Calibration website
======================================

Overview
--------

For this Staff Calibration website, the website and the project folder is named *staff* and includes four applications named: (1) *accounts*, (2) *staffs*, (3) *range_calibration*, and (4) *staff_calibration* with the following structure:

.. parsed-literal::
	staff/                             <- main website folder
	├──manage.py                      <- script to run django tools
	├──staff/                         <- website/project folder
	├──accounts/                      <- application folder
	├──staffs/                        <- application folder
	├──range_calibration/             <- application folder
	└──staff_calibration/             <- application folder

The general logics are:

1. Use ``django-admin`` to generate the main website/project folder

2. Use ``manage.py`` to create *applications*

3. Register the new applications to include them in the project via ``settings.py`` and ``url.py`` found inside the project folder


Creating the project
--------------------

Like the *mytestsite*, **staff** website/project can be created as follows:

1. In the command prompts, navigate to the main directory (e.g., *django_projects*). Also activate the virtual environment for the Django to work. 
2. Create the project and navigate into the folder as shown

.. parsed-literal::
	django-admin startproject staff
	cd staff

3. The folder structure will look like this:

.. parsed-literal::
	staff/
	├──manage.py               <- main engine - create applications, run servers, work with databases, and more
	└──staff/
	   ├──settings.py         <- contains all the website settings, app registrations, database configurations &   location   
	   ├──urls.   y             <- URL mappings including urls to the other application   
	   ├──__init__.py         <- empty file telling Python to treat it as a director   
	   ├──wsgi.py             <- Web server interface 
	   └──asgi.py             <- Asynchronous server interface compatible with WSGI

Creating the *staffs* application
---------------------------------

Follow the instructions below to create the *staffs* application. The rest of the applications can be created in the same way. 

1. In the same command prompts, run the following:

.. parsed-literal::
	python manage.py startapp staffs

2. This will create a new folder called *staffs* with the number of *.py* files and a folder called *migrations*. The updated project directory will look like below:

.. parsed-literal::
	staff/
	├──manage.py
	├──staff/
	└──staffs/                   <- application folder
	   ├──admin.py              <- settings used for the admin site
	   ├──apps.py               <- speficying the application
	   ├──models.py             <- create models for this application
	   ├──tests.py
	   ├──views.py              <- create views for this application
	   ├──__init__.py           <- empty file for django to recognise as a python package
	   └──migrations/		      <- folder to store migration files required to update the database

Registering the *staffs* application
------------------------------------

All new applications created by ``manage.py startapp`` as registered under ``INSTALLED_APPS`` inside the ``settings.py``. Open the ``settings.py`` in the project folder *staff* and add the application ``staffs`` to the ``INSTALLED_APPS`` list:

.. parsed-literal::

	# Application definition
	INSTALLED_APPS = [
	    'django.contrib.admin',
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.messages',
	    'django.contrib.staticfiles',
	    **'staffs'**,
	]

This added line will link with ``apps.py`` inside the *staffs* folder. 

Specifying the database
-----------------------

The database is configured in the ``settings.py`` as shown below. This SQLite database is configured automatically by django for development purposes but will need to be configured to a diffrent database for production (see, https://docs.djangoproject.com/en/3.1/ref/databases/ for other database connections)

.. parsed-literal::

	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.sqlite3',
	        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
	    }
	}

URL mappings
------------

The project folder contains a URL mapper file (``url.py``). This file can be used to manage all URL mappings for the website. However, urls associated with the applications are stored in a separate ``urls.py`` inside the application (e.g., *staffs*) and connected to the project ``urls.py`` using the django ``include`` function. 

1. Open **staff/staff/urls.py**. The ``url.py`` file has a set of instructions and followed by:

.. code-block:: Python
	
	# filename - staff/staff/urls.py

	from django.contrib import admin
	from django.urls import path

	urlpatterns = [
	    path('admin/', admin.site.urls),
	]

2. The applications (e.g., *staff*) are mapped like this:

.. code-block:: Python

	# filename - staff/staff/urls.py

	from django.contrib import admin
	from django.urls import path, include              # add include

	urlpatterns = [
	    path('admin/', admin.site.urls),
	    path('staffs/', include('staffs.url')),        # new line inserted
	]

3. The *staffs* application can now be accessed at ``127.0.0.1:8000/staffs/``. 

4. Application specific URLs are mapped by creating a file called ``urls.py`` in the application folder. For the *staffs* application, the ``urls.py`` might look like this:

.. code-block:: Python

	# filename - staff/staffs/urls.py

	from django.urls import path
	from . import views                                                # import views

	urlpatterns = [ 
	    path('.', views.staff_list, name="staff_list""),               # mapping the staff_list from views function
	    path('levels/', views.levels_list, name="levels_list"),        # mapping the list_list from views function
	    ....
	    ....
	]

Templates
---------

Templates are html files defining the structure of the presentation in web browsers. It uses placeholders to represent the actual content. Templates are usually stored in a folder called **templates** in the main project directory or inside the application and are called by the ``views.py``.

.. parsed-literal::
	
	staff/                                   <- project folder
	├──templates/                           <- general templates folder (e.g., base template)
	|	└──base.html                        <- base template for use in other templates
	└──staffs/                              <- application folder
	   └──templates/                       <- templates folder for the application
	   	  └──staffs/                      <- application name
	   	  	 ├──staff_list.html          <- application specific templates
	         └──level_list.html          <- ''  

The following code snippet is a sample base template from a **base_generic.html** file. This base template is being modifed and inserted into all the other templates for the staff calibration project. 

.. code-block:: html

	<!DOCTYPE html>                                                 
	<html lang="en">
	<head>
	  {% block title %}<title>Staff Calibration</title>{% endblock %}
	</head>
	<body>
	  {% block sidebar %}<!-- insert default navigation text for every page -->{% endblock %}
	  {% block content %}<!-- default content text (typically empty) -->{% endblock %}
	</body>
	</html>

This **base_generic.html** template is inserted into other templates using a ``extends`` template tag at the top line. The contents are inserted inside the ``block content`` element. An example home page for the staff calibration project may be written as:

.. code-block:: html

	{% extends "base_generic.html" %}

	{% block content %}
	  <h1>Staff calibration online</h1>
	  <p>Welcome to Landgate's online staff calibration page, an web application developed by <em>Survey Services, Landgate</em></p>
	{% endblock %} 

For more information on templates, refer to https://docs.djangoproject.com/en/3.1/topics/templates/. If the view function cannot find the required template, the browser will through in the message ``TemplateDoesNotExist`` with other information. 


Other settings - CSS/JavaScript/Images
--------------------------------------

CSS and JavaScripts are integral for a website. Django templates are customised and styled using CSS and Javascripts that sits inside the main project/website folder and mapped in the following way:

1. Create two folders called **assets** and **images** inside the main project/website folder and copy all the relevant files into the newly created folders.

.. parsed-literal::
	assets/
	├──style.css
	└──script.js
	
	images/
	└──logo.png

2. In the ``settings.py``, add the following lines:
	
.. code-block:: Python

	# Static files (CSS, JavaScript, Images)
	# https://docs.djangoproject.com/en/3.1/howto/static-files/
	STATIC_URL = '/static/'
	STATICFILES_DIRS = [os.path.join(BASE_DIR, 'assets'),]

3. Update the project ``urls.py`` with the following lines:

.. code-block:: Python

	# filename - staff/staff/urls.py

	from django.conf import settings                  # import settings
	from django.conf.urls.static import static        # import static
	from django.contrib import admin
	from django.urls import path, include              

	urlpatterns = [
	    path('admin/', admin.site.urls),
	    path('staffs/', include('staffs.url')),        
	]

	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # connect to the STATIC_URL in settings.py

Testing the Django website framework
------------------------------------

With the above settings and configurations, the **staff** project/website now has the following:

1. ``settings.py`` with a *staffs* application registered, SQLite database, a pointer to the static file locations
2. ``urls.py`` with a Administration url mapping, *staffs* application, and connections to the static file locations
3. *staffs* application with a ``urls.py`` listed with two *views*

The website can be run but does not do anything yet. To check if everything is working as expected, run through the following instructions:

1. Run the data migrations - Django maps model definitions in the model code (``models.py``) to the data structure used by the database and keeps track of the changes in the migration folder (**/staff/staffs/migrations/**) in the form of python scripts. Django automatically adds a number of models for use by the *adminstrator* including users, groups, permissions, sessions, etc. To add these models, run the following commands in the command prompt. Re-run them every time a field is added or removed from the ``models.py`` file. 

.. code-block::Python
	python manage.py makemigrations                    # maps all the model definitions to data structures
	python manage.py migrate                           # apply the migrations  

2. Run the **staff** website using the *runserver* command:
	
.. parsed-literal::
	python manage.py runserver

		Watching for file changes with StatReloader
		Performing system checks...

		System check identified no issues (0 silenced).

		You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
		Run 'python manage.py migrate' to apply them.
		December 07, 2020 - 15:05:35
		Django version 3.1, using settings 'staff.settings'
		Starting development server at http://127.0.0.1:8000/
		Quit the server with CTRL-BREAK.

3. By navigating to ``http://127.0.0.1:8000/staffs/`` in the web browser, it will give a *page not found* error. This shows that it has a url pointing to it but the page does not yet exist. The link to this page will have to created from ``staff/staffs/views.py`` and the *html* template defined in the view shoud be connected to the ``urls.py``. 