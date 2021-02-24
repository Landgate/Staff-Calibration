Home Page and Guide
===================

Overview
--------

We will now add a home page for this application so that users are automatically re-directed to this page after signing/logging in. 

A step-by-step guide is also added to provide a general instruction to the users on how staff calibration is done.  


Home page
---------

1. **URL Mapping**: Let's create a function-based view called ``homeview()`` and name it ``staff-home`` in the **urls.py**:

	.. code-block:: python

		#filename: staff/staff_calibration/urls.py

		... 

		urlpatterns = [
    		path('', views.homeview, name="staff-home"),
    		...

    	]

2. **View**: ``homeview()`` redirects the home page to the project home page (i.e., http:127.0.0.1:8000):

	.. code-block:: python

		...

		def homeview(request):
    		return redirect('/')

Step-by-step guide page
-----------------------

1. **URL Mapping**: Let's create a function-based view called ``guideview()`` and name it ``staff-guide`` in the **urls.py**:

	.. code-block:: python

		#filename: staff/staff_calibration/urls.py

		... 

		urlpatterns = [
			...
    		path('', views.guideview, name="staff-guide"),
    		...

    	]

2. **View**: ``guideview()`` renders the HTML template **staff_calibration_guide.html**:

	.. code-block:: python

		...

		def guideview(request):
    		return render(request, 'staff_calibration/staff_calibration_guide.html')

3. **Template**: The step-by-step guide template is a standard HTML document containing instructions on staff calibration. It looks like this:

	.. figure:: staff_calibration_guide.png
		:align: center

