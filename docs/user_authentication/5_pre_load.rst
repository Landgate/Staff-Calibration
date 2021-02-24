Loading user information during migration
=========================================

Overview
--------

For a data analytics application such as this Staff Calibration project, it is a requirement to pre-load a lot of the historical data into the database, which would otherwise take an enormous amount of time to populate them one by one. In Django, it is possible to provide initial data with ``migrations`` or ``fixtures``. 

For this project, for example, we will load all range measurements automatically during data ``migration``. We will also provide data for model ``Authority`` and ``StaffTypes`` and load the landgate staves and levels by default.

Initial Migrations
------------------

The "initial migrations" for an app are the migrations that create the first version of that app’s tables. Usually an app will have only one initial migration, but in some cases of complex model interdependencies it may have two or more. Initial migrations are marked with an ``initial = True`` class attribute on the migration class. If an ``initial`` class attribute is not given, a migration will be considered initial if it is the first migration in the app (i.e. if it has no dependencies on any other migration in the same application).

Let's look at the **accounts** app migration (**staff/accounts/migrations/**). Note that the migration files (*.py*) are generated during ``python manage.py makemigrations`` in command prompt. In this case, it has created two migration files: ``0001``- initial migration and ``0002`` - subsequent migration:

.. parsed-literal:: 
	
	staff/
	└──accounts/
		└──migrations/
			├──__init__.py
	  	 	├──0001_initial.py
	  	 	└──0002_auto_20201221_0943.py

The initial migration ``0001`` was created when ``makemigration`` was run for the first time and creates all the models, fields, and associated structures defined at that time. The ``makemigrations`` and ``migrate`` commands must be run everytime a change is made to a model or models and will automatically create subsequent migration files. In this case, the subsequent migration ``0002`` was created because ``blank==True`` and ``null=True`` was applied to the ``Authority`` model to allow blank and null values during the initial testing phase. 

Example Migration 
-----------------

The migration file for ``0002`` looks like this:

.. code-block:: python

	#filename: staff/accounts/migrations/0002_auto_20201221_0943.py   # it may have a different name after 0002

	from django.db import migrations, models
	import django.db.models.deletion


	class Migration(migrations.Migration):

	    dependencies = [
	        ('accounts', '0001_initial'),                # implies that this migration depends on the initial migration 0001  
	    ]

	    operations = [                                   # type of operation performed - AlterField to ForeignKey - Authority 
	        migrations.AlterField(
	            model_name='customuser',
	            name='authority',
	            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.authority'),
	        ),
	    ]

What Django looks for when it loads a migration file (as a Python module) is a subclass of ``django.db.migrations.Migration`` called ``Migration``. It then inspects this object for four attributes, only two of which are used most of the time:

* **dependencies** -  a list of migrations this one depends on.
* **operations** - a list of Operation classes that define what this migration does.

The operations are a set of declarative instructions which tell Django what schema changes need to be made. Django scans them and builds an in-memory representation of all of the schema changes to all apps, and uses this to generate the SQL which makes the schema changes.

That in-memory structure is also used to work out what the differences are between your models and the current state of your migrations; Django runs through all the changes, in order, on an in-memory set of models to come up with the state of your models last time you ran makemigrations. It then uses these models to compare against the ones in your **models.py** files to work out what you have changed.

It should be noted that the ``makemigrations`` must be always followed by ``migrate`` to apply the migrations to the database and ensure that they are working properly. For more information on migrations, refer to https://docs.djangoproject.com/en/3.1/topics/migrations/.


Data Migrations
---------------

Migrations that alter data are usually called **data migrations** and they are best written as separate migrations, sitting alongside your schema migrations. Django can’t automatically generate data migrations, as it does with schema migrations, but we can write them with ease. Migration files in Django are made up of **Operations**, and the main operation that needs to be used or data migrations is ``RunPython``.

In this **accounts** application, we will pre-load data for ``Authority`` from a csv file, create a ``superuser``, and create a some groups using ``Group`` from `django.auth``. 

Loading to the Authority model
******************************

Here is the ``Authority`` model from **models.py** consisting of two fields: ``authority__abbrev`` and ``authority_name``:

.. code-block::python

	class Authority(models.Model):
	    authority_abbrev = models.CharField(max_length=20)
	    authority_name = models.CharField(max_length=200)
	    
	    def __str__(self):
	        return self.authority_name

The csv file (named **authority.csv**) was created and stored under the ``STATIC`` folder directory **staff/assets/authority/**. The csv file looks like this:

+--------------------+--------------------------------+
| AUTHORITY_ABBREV   |     AUTHORITY_NAME             |
+====================+================================+
|     Other          | Other                          |
+--------------------+--------------------------------+
|     LG             | Landgate                       |
+--------------------+--------------------------------+
|     35             | 35 Degrees South               |
+--------------------+--------------------------------+
|     AW&P           | A.R. Williams & Partners       |
+--------------------+--------------------------------+
|     A1             | A1 Minerals Limited            |
+--------------------+--------------------------------+
|     AAS            | AA Surveys                     |
+--------------------+--------------------------------+
|     AAMG           | AAM Group                      |
+--------------------+--------------------------------+
|     AAMHATCH       | AAMHatch Pty Ltd               |
+--------------------+--------------------------------+
|     ABAXA          | Abaxa                          |
+--------------------+--------------------------------+
|  **more below**    | **more below**                 |
+--------------------+--------------------------------+

To start, create an empty migration file using the command ``python manage.py makemigrations --empty app_name`` in the command prompt. ``app_name`` here is our **accounts** app. Django will put the file in the right place.

.. parsed-literal::

	python manage.py makemigrations --empty accounts

This will create a new migration file called **0003_auto_20201224_1015.py** in the migrations folder under **accounts**. The filename may be different in each case but the sequence will follow consecutive order (in this case, its ``0003``). 

.. parsed-literal::
	
	Migrations for 'accounts':
  		accounts/migrations/0003_auto_20201224_1015.py

The new migration file will look like this:

.. code-block:: python
	
	#filename: accounts/migrations/0003_auto_20201224_1015.py

	from django.db import migrations

	class Migration(migrations.Migration):

	    dependencies = [
	        ('accounts', '0002_auto_20201221_0943'),
	    ]

	    operations = [
	    ]

Now, all we need to do is create a new function and have ``RunPython`` use it. ``RunPython`` expects a function that takes in two arguments: **apps registry** (denoted by ``apps``) and a **SchemaEditor** (denoted by ``schema_editor``). The app registry contains the historical versions of all the models loaded into it to match where in your history the migration sits, and the SchemaEditor is used to manually effect database schema changes. 

Let's create a function called **load_authority** to read the csv file (do not forget to ``import csv``) and load it to the ``Authority`` model and add it to the ``operations`` list to run with ``RunPython``. 

.. code-block:: python
	
	#filename: accounts/migrations/0003_auto_20201224_1015.py

	import csv                               
	from django.db import migrations

	def load_authority(apps, schema_editor):

		# import the model
		Authority = apps.get_model("accounts", "Authority")

		# open and read the csv file 
		with open("assets/authority/authority_names.csv", 'r') as f: 
			reader = csv.reader(f)
			header = next(reader)                  # skip the header

			# get each row and assign the columns to the appropriate field
			# for example: first one (row[0]) corresponds to ``authority_abbrev`` and so on
			for row in reader:
				authority = Authority.objects.create(authority_abbrev = row[0], authority_name = row[1])

	class Migration(migrations.Migration):

	    dependencies = [
	        ('accounts', '0002_auto_20201221_0943'),
	    ]

	    operations = [
	    	migrations.RunPython(load_authority),
	    ]

Save it and run ``python manage.py migrate`` to apply the data migration. It will look like this if its successful:

.. parsed-literal::

	python manage.py migrate

		Operations to perform:
		  Apply all migrations: accounts, admin, auth, contenttypes, sessions, staffs
		Running migrations:
		  Applying accounts.0003_auto_20201224_1015... OK 

Next, log in the **admin** page (http://127.0.0.1:8000/admin) or open the default sqlite database in the project folder to find out if the data has been loaded or not. It should be all under the ``authority`` table. 

.. figure:: data_migrations_authority_table.png
	:align: center

	List of authorities added to the Authority model via migration

Creating groups and superuser
*****************************

Similarly, we can generate another empty migration in the **accounts** and copy the following lines to create groups and a superuser. Three groups are created: Landgate, Geodesy, and Others so that we can add different levels of permissions to them. It is possible to create ``superuser`` through the console (command prompt) and it can be created in a migration file as well. 

Copy the following lines in the new migration file (here it is calle **0004_auto_20201224_1049.py**): 

.. code-block:: python
	
	#filename: staff/accounts/migrations/0004_auto_20201224_1049.py

	from django.db import migrations
	# import the required models
	from accounts.models import CustomUser, Authority

	def forwards_func(apps, schema_editor):
		# import Group from django.auth
	    Group = apps.get_model("auth", "Group")
	    db_alias = schema_editor.connection.alias

	    # create groups
	    Group.objects.using(db_alias).bulk_create([
	        Group(name='Landgate'),
	        Group(name='Geodesy'),
	        Group(name='Others'),
	    ])

	    # create superuser
	    CustomUser.objects.create_superuser(
	    	email='geodesy@landgate.wa.gov.au',  
	    	password='landgate.geodetic',
	        authority= Authority.objects.get(authority_abbrev='LG')   # Gives an authority from Authority
	    	)

	# Reverses the action performed above by deleting everything, if migration needs to be revesed
	def reverse_func(apps, schema_editor):
		Group = apps.get_model("auth", "Group")
		Group.object.all().delete()

		CustomUser.objects.all().delete()

	class Migration(migrations.Migration):

	    dependencies = [
	        ('accounts', '0002_auto_20201110_0811'),             # previous migration
	    ]

	    operations = [
		    migrations.RunPython(
		            forwards_func, reverse_func                  # actions performed
		        ),
	    ]

Note that a ``reverse_func`` has been added to the migration file so that the custom migration can be reversed with ``migrate`` if required. The reverse migration is performed by passing the sequence number of previous migration, e.g., to reverse this migration ``accounts.004``, we can just run ``python manage.py migrate accounts.0003``. 

If the custom migration does not have the reverse function, it cannot be reversed. 


