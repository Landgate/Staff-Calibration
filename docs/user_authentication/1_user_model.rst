Setting up the Custom User Model
================================

Overview
--------

The authentication has been set up automatically by django when the skeleton website (or project) was created, i.e., when executing the ``django-admin startproject staff`` command. The database tables for users and model permissions were then created after the ``python mananage.py migrate`` was run for the first time. The authentication configuration are set up in:

1. In the ``settings.py``: 
	
	.. code-block:: python

		INSTALLED_APPS = [
		    'django.contrib.admin',                  # admin interface
		    'django.contrib.auth',                   # core authentication framework
		    'django.contrib.contenttypes',           # content type system for setting permissions
		    'django.contrib.sessions',
		    'django.contrib.messages',
		    ...
	
	And the following lines associated to the above applications. 

	.. code-block:: python

		MIDDLEWARE = [
		    'django.middleware.security.SecurityMiddleware',
		    'django.contrib.sessions.middleware.SessionMiddleware',
		    'django.contrib.auth.middleware.AuthenticationMiddleware',
		    'django.contrib.messages.middleware.MessageMiddleware',
		    ...
		]

2. In the project (**staff/**) ``urls.py``:
	
	.. code-block:: python

		from django.contrib import admin

		urlpatterns = [
			path('admin', admin.site.urls),         # URL configuration to the admin site
		]

After running the ``python mananage.py migrate``, Django allows us to create the ``superuser`` using the ``python manage.py createsupersuer`` command. It requires a **username**, **email address**, and a **password** to register, which can be used to log into the **admin** interface or page (e.g., http://127.0.0.1:8000/admin/).   

``superuser`` has all the permissions to create **users**, **Groups** and **Permissions** that sit under **AUTHENTICATION AND AUTHORISATION** section. It is the quickest way to add/update/delete records including the users/groups/permissions. Try to click on each one of them to see how they work. 

Custom User model
-----------------

While the default Django authentication system has everything required for the Staff Calibration website, it still requires a **username** to sign up and log into the website. So it takes a few extra steps to get rid of the *username* and apply the normal practice of using **email** for authentication. There are four very important steps that should be followed:

1. Create a custom **User** model and a **Manager**
2. Update the *settings.py* file
3. Customise the ``UserCreationForm`` and ``UserChangeForm`` forms
4. Update the *admin.py* file

Now let us follow these steps and create a ``CustomUser`` model a ``CustomUserManager``: 

1. Open command prompts > activate the virtual environment > Navigate to the project directory (**staffs/**).

2. Create a new application called **accounts** and add it to ``INSTALLED_APPS`` in ``settings.py``:
	
	(a) Create the **accounts** application

	.. parsed-literal::

		python manage.py startapp accounts

	(b) Add the accounts app to project settings

	.. code-block:: python

		#filename: staff/staff/settings.py

		INSTALLED_APPS = [
			...,
			accounts,
			...
		]

3. Add a custom Manager by subclassing ``BaseUserManager``, in order to use email as the unique identifier instead of a default *username*. 

	Create a **managers.py** file in the *accounts* app (**staff/accounts/managers.py**) and add the following lines:

	.. code-block:: python

		filename: staff/accounts/managers.py

		from django.contrib.auth.base_user import BaseUserManager
		from django.utils.translation import ugettext_lazy as _
		from django.contrib.auth.models import Group


		class CustomUserManager(BaseUserManager):
		    """
		    Custom user model manager where email is the unique identifiers
		    for authentication instead of usernames.
		    """
		    def create_user(self, email, password, **extra_fields):
		        """
		        Create and save a User with the given email and password.
		        """
		        if not email:
		            raise ValueError(_('The Email must be set'))
		        email = self.normalize_email(email)
		        user = self.model(email=email, **extra_fields)
		        user.set_password(password)
		        user.save()
		        return user

		    def create_superuser(self, email, password, **extra_fields):
		        """
		        Create and save a SuperUser with the given email and password.
		        """
		        extra_fields.setdefault('is_staff', True)
		        extra_fields.setdefault('is_superuser', True)
		        extra_fields.setdefault('is_active', True)

		        if extra_fields.get('is_staff') is not True:
		            raise ValueError(_('Superuser must have is_staff=True.'))
		        if extra_fields.get('is_superuser') is not True:
		            raise ValueError(_('Superuser must have is_superuser=True.'))
		        return self.create_user(email, password, **extra_fields)

4. Next, in the **models.py** file, create a *CustomUser* model by subclassing ``AbstractBaseUser`` from django model class. Import ``CustomUserManager`` from *managers.py* and ``PermissionMixin`` by subclassing the django auth models. Add the required fields and set the ``USERNAME_FIELD`` to ``email``. See below: 

	.. code-block:: python

		filename: staff/accounts/models.py

		from django.db import models
		from django.contrib.auth.models import Group
		from django.contrib.auth.models import AbstractBaseUser
		from django.contrib.auth.models import PermissionsMixin
		from django.utils.translation import gettext_lazy as _
		from django.utils import timezone

		from .managers import CustomUserManager

		# Create your models here.
		class Authority(models.Model):
		    authority_abbrev = models.CharField(max_length=20)
		    authority_name = models.CharField(max_length=200)
		    
		    def __str__(self):
		        return self.authority_name

		class CustomUser(AbstractBaseUser, PermissionsMixin):
		    email = models.EmailField(_('email address'), unique=True)
		    first_name = models.CharField(max_length=100)
		    last_name = models.CharField(max_length=100)
		    authority = models.ForeignKey(Authority, on_delete=models.CASCADE, default=1, blank=True, null=True) # to allow for a blank/null value if Authority table is blank
		    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
		    is_staff = models.BooleanField(default=False)
		    is_superuser = models.BooleanField(default=False)
		    is_active = models.BooleanField(default=True)
		    date_joined = models.DateTimeField(default=timezone.now)

		    USERNAME_FIELD = 'email'
		    REQUIRED_FIELDS = []

		    objects = CustomUserManager()

		    def __str__(self):
		        return self.email

	A new ``Authority`` class is created to store the user's company name and abbreviation, which is being passed to the **CustomUser** model as a ``ForeignKey``.  

5. Update the *settings.py* in the project so that Django can use the new ``CustomUser`` model:

	.. code-block:: python

		filename: staff/staff/settings.py

		...

		AUTH_USER_MODEL = 'accounts.CustomUser'

		...

6. Create and apply migrations

	a) Before applying the CustomUser model, the database will have the default ``auth`` **User** model and other detault groups and permissions. Open a new command prompt window, navigate to the project diretory, and run > ``sqlite3 db.sqlite3`` and ``.tables`` to see all the tables as below:

	.. code-block:: python

		auth_group                  django_content_type
		auth_group_permissions      django_migrations
		auth_permission             django_session
		auth_user                   staffs_digitallevel
		auth_user_groups            staffs_staff
		auth_user_user_permissions  staffs_stafftype
		django_admin_log

	b) Apply migrations to incorporate the new *CustomUser* model and *CustomUserManager* as follows:

		.. code-block:: python

			python manager.py makemigrations
			python manage.py migrate

		A new migration file - *accounts\migrations\0001_initial.py* is created. Open the file and see what it is like. The sqilte3 database command for creating the *CustomUser* table looks like this:

		.. code-block:: python 

			# In the command prompts window run > sqlite3 db.sqlite3. Type > .tables to see the tables and type > .schema accounts_customuser to see the results below: 

			CREATE TABLE IF NOT EXISTS "accounts_customuser" (
				"id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
				"password" varchar(128) NOT NULL, 
				"last_login" datetime NULL, 
				"email" varchar(254) NOT NULL UNIQUE, 
				"first_name" varchar(100) NOT NULL, 
				"last_name" varchar(100) NOT NULL, 
				"is_staff" bool NOT NULL, 
				"is_superuser" bool NOT NULL, 
				"is_active" bool NOT NULL, 
				"date_joined" datetime NOT NULL, 
				"authority_id" integer NOT NULL REFERENCES "accounts_authority" ("id") DEFERRABLE INITIALLY DEFERRED); 

	c) Open the django admin page (http://127.0.0.1:8000/admin) in the internet browser and check if it asks for the email address instead of a username. 

	.. figure::  admin_interface.png
	   :align:   center

	   Admin user login interface with email address as login.

Next, we will need to customise the forms to accept the **CustomUser** model. 