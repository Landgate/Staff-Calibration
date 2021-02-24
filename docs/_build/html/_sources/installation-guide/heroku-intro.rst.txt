Deploying the Staff Calibration Apps on Heroku 
==============================================

Once your site is finished (or finished "enough" to start public testing) you're going to need to host it somewhere more public and accessible than your personal development computer.

Up to now you've been working in a development environment, using the Django development web server to share your site to the local browser/network, and running your website with (insecure) development settings that expose debug and other private information. Before you can host a website externally you're first going to have to:

* Make a few changes to your project settings.
* Choose an environment for hosting the Django app.
* Choose an environment for hosting any static files.
* Set up a production-level infrastructure for serving your website

The good news when you're starting out is that there are quite a few sites that provide "evaluation", "developer", or "hobbyist" computing environments for "free". These are always fairly resource constrained/limited environments, and you do need to be aware that they may expire after some introductory period. They are however great for testing low traffic sites in a real environment, and can provide an easy migration to paying for more resources when your site gets busier. Popular choices in this category include Heroku, Python Anywhere, Amazon Web Services, Microsoft Azure, etc.

Many providers also have a "basic" tier that provides more useful levels of computing power and fewer limitations. Digital Ocean and Python Anywhere are examples of popular hosting providers that offer a relatively inexpensive basic computing tier (in the $5 to $10USD per month range).

Getting your website ready to publish
-------------------------------------

The Django skeleton website created using the django-admin and manage.py tools are configured to make development easier. Many of the Django project settings (specified in settings.py) should be different for production, either for security or performance reasons.

Tip: It is common to have a separate settings.py file for production, and to import sensitive settings from a separate file or an environment variable. This file should then be protected, even if the rest of the source code is available on a public repository.

The critical settings that you must check are:

``DEBUG``. This should be set as False in production (``DEBUG = False``). This stops the sensitive/confidential debug trace and variable information from being displayed.
``SECRET_KEY``. This is a large random value used for CSRF protection etc. It is important that the key used in production is not in source control or accessible outside the production server. The Django documents suggest that this might best be loaded from an environment variable or read from a server-only file.

.. parsed-literal::
	# Read SECRET_KEY from an environment variable
	import os
	SECRET_KEY = os.environ['SECRET_KEY']

	# OR

	# Read secret key from a file
	with open('/etc/secret_key.txt') as f:
	    SECRET_KEY = f.read().strip()

Let's change the LocalLibrary application so that we read our ``SECRET_KEY`` and ``DEBUG`` variables from environment variables if they are defined, but otherwise use the default values in the configuration file.

Open /locallibrary/settings.py, disable the original ``SECRET_KEY`` configuration and add the new lines as shown below in bold. During development no environment variable will be specified for the key, so the default value will be used (it shouldn't matter what key you use here, or if the key "leaks", because you won't use it in production).

.. parsed-literal::
	# SECURITY WARNING: keep the secret key used in production secret!
	# SECRET_KEY = "cg#p$g+j9tax!#a3cup@1$8obt2_+&k3q+pmu)5%asj6yjpkag"
	import os
	SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'cg#p$g+j9tax!#a3cup@1$8obt2_+&k3q+pmu)5%asj6yjpkag')

Then comment out the existing DEBUG setting and add the new line shown below.

.. parsed-literal::
	# SECURITY WARNING: don't run with debug turned on in production!
	# DEBUG = True
	DEBUG = os.environ.get('DJANGO_DEBUG', '') != 'False'

The value of the ``DEBUG`` will be True by default, but will only be False if the value of the ``DJANGO_DEBUG`` environment variable is set to False. Please note that environment variables are strings and not Python types. We therefore need to compare strings. The only way to set the DEBUG variable to False is to actually set it to the string False

You can set the environment variable to False by issuing the following command:

.. parsed-literal::
	export DJANGO_DEBUG=False

A full checklist of settings you might want to change is provided in Deployment checklist (Django docs). You can also list a number of these using the terminal command below:

.. parsed-literal::
	python3 manage.py check --deploy


Deploying Django apps on Heroku
-------------------------------

In order to execute your application Heroku needs to be able to set up the appropriate environment and dependencies, and also understand how it is launched. For Django apps we provide this information in a number of text files:

* **runtime.txt**: the programming language and version to use.
* **requirements.txt**: the Python component dependencies, including Django.
* **Procfile**: A list of processes to be executed to start the web application. For Django this will usually be the Gunicorn web application server (with a .wsgi script).
* **wsgi.py**: WSGI configuration to call our Django application in the Heroku environment.

In order to get our application to work on Heroku we'll need to put our Django web application into a git repository, add the files above, integrate with a database add-on, and make changes to properly handle static files.

Once we've done all that we can set up a Heroku account, get the Heroku client, and use it to install our website.