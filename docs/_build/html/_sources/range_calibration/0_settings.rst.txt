Settings
========

Let's call this application **range_calibration**. 

Create it using the ``python manage.py startapp range_calibration``. 

Project settings
----------------

1. project **staff/staff/settings.py**:

	.. code-block:: python

		#filename: staff/staff/settings.py

		... 

		INSTALLED_APPS = [
			...
			'accounts',
			'staffs',
			'range_calibration',           # this application
		]

2. project **staff/staff/urls.py**: 
	
	.. code-block:: python

		urlpatterns = [
		    ...
		    path('range_calibration/', include('range_calibration.urls')),
		]


Historical range measurements
-----------------------------

As mentioned, we have many historical range measurements that must be pre-loaded during data migration. By pre-loading them we do not have to process them one by one and therefore, saves a lot of time. To enable pre-loading, we need to copy the range measurement files into the project folder and pre-process them to our convenience. 

In our case, we have all the range measurements stored in a directory (under Job No. 20172297) and each observation set is stored a directory named by date, and observer inside the main directory. The observation set consist of a fieldbook (a scanned pdf file), a raw observation file (e.g., **.raw**), and a converted **ASCII** version as shown below:

.. figure:: observation_directory.png
	:align: center

To enable pre-loading, copy these observation folders to a new directory called **data/range_data/20172297/** in the project directory (**staff/**). Edit the observation directory names to add the staff number as shown below:

.. parsed-literal::

	staff/                                      <- application root folder
	│
	├──data/                                    <- new folder
	│  ├──range_data/                          
	│  │  ├──20172297                           <- job folder
	│  │  │	 ├──20180111_26296_TC               <- observation set
	│  │  │	 ├──20180226_26296_TC               <- observation set
	│  │  │	 ├──20180327_26296_VU               <- observation set
	│  │  │	 ...   
	│  │  └──temperature.csv                    <- metadata



Create a csv file called **temperature.csv** inside the directory **range_data** and tabulate all the required fields from the scanned pdf field book. This includes date of observation, staff number, level number, and start and end temperatures. The table below shows the information from Jan 2018 to November 2020. 

.. figure:: temperature_table.png
	:align: center 	  

Each row in the csv file is linked to the observation directory by their observation date and staff number. This is exactly how the data submission form will be designed later on. Lets look at how each of the project components looks before we can load these observations. 

