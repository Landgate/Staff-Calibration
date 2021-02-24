Installing Python & Django
==========================

Installing Python
-----------------

Django web applications can run on any operating system (e.g., Windows, macOS, Linux/Unix, Solaris, among others) that can run Python.

1. On the Window's OS, install Python from their official link https://www.python.org/downloads/ or using package managers such as *anaconda* (https://www.python.org/downloads/). 
2. Install it on ``C:/Data/Software``.
3. Be sure to check the box labeled ``Add Python to PATH``.
4. Python comes with a ``pip`` (package manager) by default that is used to install various python modules.
5. Check the list of installed packages by typing ``pip list`` in command prompt (or cmd). 

Installing the virtual environment
----------------------------------

After installing python, create a virtual environment to only have the packages required to run the Django web application (i.e., Staff calibration). This is done by:

1. Install the ``virtualenv`` using ``pip``. Open the ``Command Prompt`` in Windows Desktop and type:

.. parsed-literal::
	pip install virtualenv

2. Go to the working directory, for example, by typing in the ``Command Prompt``: 

.. parsed-literal::
	cd C:\\Data\\Development\\django_projects

3. Create a new virtual environment with the ``virtualenv`` command. Name it ``venv`` or by any other name. 

.. parsed-literal::
	virtualenv venv

	| (venv) (base) C:\\Data\\Development\\django_projects>virtualenv venv
	| created virtual environment CPython3.8.3.final.0-64 in 1887ms
  	| creator CPython3Windows(dest=C:\Data\Development\django_projects\venv, clear=False, global=False)
  	| seeder FromAppData(download=False, pip=bundle, setuptools=bundle, wheel=bundle, via=copy, app_data_dir=C:\\Users\\Likxx00\\AppData\\Local\pypa\\virtualenv)
  	| added seed packages: pip==20.2.1, setuptools==49.2.1, wheel==0.34.2
  	| activators BashActivator,BatchActivator,FishActivator,PowerShellActivator,PythonActivator,XonshActivator

4. If successfull, a new folder called **venv** can be seen in the same directory and ``(venv)`` appears alongside ``(base)`` in the command prompt saying that the virtual environment is now active. This is where all packages related to the Staff Calibration is installed including ``Django``. For example, type ``pip install django`` and enter to install django.
5. Type ``deactivate`` to exit from the virtual environment. 
6. **Note**: Always remember to ``activate`` the virtual environment to run the Django web application. In the Command Prompts, type and enter the following lines:

.. parsed-literal::
	cd C:\\Data\\Development\\django_projects
	.\\venv\\Scripts\\activate

Installing Django
-----------------

Remember to install ``django`` in the virtual environment. See (6) above to activate it if not active. 

.. parsed-literal::
	pip install django

Check the django version

.. parsed-literal::
	python -m django --version

Testing the Django installation
-------------------------------

Its now time to see if Django is working. To check this, create a new folder with a name **django_test** and follow the instructions below. 

1. In the command prompt, activate the virtual environment and navigate the the django_test folder

.. parsed-literal::
	cd C:\\Data\\Development\\django_projects                   <- go to the main directory
	.\\venv\\Scripts\\activate                                  <- activate the virtual environment
	cd django_test                                              <- go to the test directory

2. Create a skeleton project called *mytestsite* using ``django-admin`` and navigate into the folder

.. parsed-literal::
	django-admin startproject mytestsite
	cd mytestsite

3. Run the *web server* using the the ``manage.py`` as shown:

.. parsed-literal::
	python manage.py runserver

		Watching for file changes with StatReloader
		Performing system checks...

		System check identified no issues (0 silenced).

		You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
		Run 'python manage.py migrate' to apply them.
		December 07, 2020 - 10:45:38
		Django version 3.1, using settings 'mytestsite.settings'
		Starting development server at http://127.0.0.1:8000/
		Quit the server with CTRL-BREAK.

4. Now on the web browser (e.g., chrome, firefox), type ``http://127.0.0.1:8000/`` as shown in the command prompt. The django site looks like this:


.. figure::  django-web.png
   :align:   center

