Building URLs, Views, and Templates
===================================

Overview
--------

The records added to the models through the admin site before will need to be presented to users or clients in the form of web pages. After determining the information that needs to be displayed on a web page, django data flow requires the following components:

* **URL** mappers to forward the supported URLs (and any information encoded in the URLs) to the appropriate view functions
* **View** functions to get the requested data from the models, create HTML pages that display the data, and return the pages to the user to view in the browser.
* **Templates** to use when rendering data in the views.


Defining the resource URLs
--------------------------

For the Staff Calibration website, users will be able to see their list of instruments (e.g., staves, digital levels), add new instruments and update their details (if required) for the **staffs** application. To do this functions, the following URLs are defined:

* ``staffs/`` - the staffs application home page (index page) showing the list of staves
* ``staffs/stafftype`` - the staffs application home page showing the list of staff types
* ``staffs/levels`` - the staffs application home page showing the list of digital levels
* ``staffs/staff_create/`` - view for inserting new staff records 
* ``staffs/stafftype_create/`` - view for inserting new staff type records  
* ``staffs/levels_create/`` - view for inserting new digital level records  
* ``staffs/stafftype/<id>/update/`` - update view for staff types with the primary key of ``<id>``
* ``staffs/levels/<id>/update/`` - update view for digital levels with the primary key of ``<id>``
* ``staffs/<id>/update/`` - update view for staves with the primary key of ``<id>``

The first three pages will present a list of staves, staff types and digital levels. The view function will fetch the data from the respective models and pass them onto the templates for display. No additional information is provided apart from rendering the list. 

The middle three pages are used for creating or adding new records through the ``form.py``, which will be explained later in more detail. 

The final three pages with ``<id>`` presents detailed information on the *stafftype*, *digital level*, and the staff. The ``<id>`` represents the identity of the individual item to display and also acts like a form to edit the fields. The URL mapper will extract the encoded information (``<id>``) and pass it to the view and the view will dynamically determine what information to get from the database. 

Creating an index (home) page with a list view of staves
--------------------------------------------------------

The home page of the **staffs** application (http://127.0.0.1:8000/staffs/ or simply denoted as ``staffs/``) will be a list of all the levelling staves created by the user including their details in the form of a table. To make this work, it requires a URL mapping, a view, and a template.    

URL Mapping
***********

1. The application (i.e., **staffs**) URL mapping has already been added to the project - **staff/staff/urls.py**
	
	.. code-block:: python

		# filename: staff/urls.py

		from django.contrib import admin
		from django.urls import path, include        # 'include' added
		from django.conf import settings             # added
		from django.conf.urls.static import static   # added

		urlpatterns = [
		    path('admin/', admin.site.urls),
		    path('staffs/', include('staffs.urls')),  # added
		]

		urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)    # added 

2. Create a new python file called ``urls.py`` in **staff/staffs/** and add the following lines:

	.. code-block:: python

		#filename: staff/staffs/urls.py

		from django.urls import path

		urlpatterns = [
			path('', StaffListView.as_view(), name='staff-home'),

		] 

	``StaffListView`` is a python class defined in the ``views.py`` for creating a list view. The ``name`` parameter is a unique identifier for this particular URL mapping and can be used in the templates to dynamically point to the resource URL. For example, one can simply add the name to the pointer as shown in red color below:

	.. parsed-literal::

		<a href="{% url 'staff-home' %}">Home</a>

View (class-based)
******************

A view is a function that processes an HTTP request, fetches the required data from the database, renders the data in an HTML page using an HTML template, and then returns the generated HTML in an HTTP response to display the page to the user. Django has built-in class-based views which can automatically perform these tasks. The only thing it requires is the ``model`` and a template name (if its different from its usual naming convention). 

Open the **staffs/views.py** and add the lines below. Note that it has already imported the ``render()`` function, which is used to generate an HTML file using the template and data. This is not required for a class-based view and will be compensated by the ``ListView`` imported from ``django.views.generic``:
	
.. code-block:: python

	from django.views.generic import ListView

	from .models import Staff, StaffType             # import the models
	# Create your views here.

	class StaffListView(ListView):
		model=Staff                                  # define the specific model

		template_name = 'staffs/staff_list.html'     # define the template. The default template name will be "staffs_list.html"

The data from the model (i.e., **Staff**) will be passed to the html template as ``self.object_list``, which is a list of objects representing the individual staff records. 

Template
********

Templates define the structure or layout of a file (such as an HTML page) and it uses placeholders to represent actual content. Django applications created using **startapp** will look for templates in a subdirectory named **templates** in the application (i.e., **/staffs/templates**). For convenience, templates are placed in a subdirectory named **staffs** in the **templates** directory - **/staffs/templates/staffs/**). If no templates are provided when accessing the resource URL, it will raise a ``TemplateDoesNotExist`` error and other details. For the templates to work properly, the following points must be noted:

1. In the project ``settings.py``, add the templates directory (``DIRS``) in the ``TEMPLATES`` section.
	
	.. code-block:: python

		'DIRS': [os.path.join(BASE_DIR), 'templates'],     # import os at the top

2. For web applications such as this, templates are main html pages. Hence, it is important to understand the basics of html, css, and javascript to make the pages presentable to the users. The location of css/javascript and/or other static files (such as logo images) put in a folder in the main project directory (in this project - **staff/assets/**)and its path is defined:
	
	* ``settings.py`` as:

	.. code-block:: python

		# Static files (CSS, JavaScript, Images)
		STATIC_URL = '/static/'
		STATICFILES_DIRS = [os.path.join(BASE_DIR, 'assets'),]
	
	* ``urls.py`` as:

	.. code-block:: python

		from django.conf import settings             # added
		from django.conf.urls.static import static   # added

		urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # added

3. Here is how a **staffs** template directory looks like:

	.. parsed-literal::

		staff/                                <- main website folder
		└──staffs/                            <- application folder
			└──templates
				├──base_generic.html          <- base html template
				└──staffs/                    <- application specific templates
					├──staff_list.html
					├──levels_lst.html
					├──staff_create.html
					├──levels_create.html
					└──staff_update.html
					... more ...
		├── assets                             <- static files folder
			 ├──images/                        <- images 
			 ├──style.css                      <- css file
			 └──script.js                      <- java script file
4. The ``base_generic.html`` is a base template defining the basic layout of the html page and may contain - 
	* title, navigation menu, sidebar, footer, logos, etc
	* links to css/javascript and other files through ``load static``
	* sections with ``block`` and ``endblock`` tags for rendering contents of other pages

5. The template files inside **/templates/staffs/** will employ the ``base_generic.html`` by using the ``extends`` tag  to render the contents inside the ``block`` codes. 


Example - Base Template
***********************

A simple ``base_generic.html`` can look like this:

.. code-block:: html 

	<!DOCTYPE html>
	<html lang="en">
	<head>
	  <title>Staff Calibration Online</title>
	  <meta charset="utf-8">
	  <meta name="viewport" content="width=device-width, initial-scale=1">
	  {% load static %}
	  <link rel="stylesheet" href="{% static 'styles.css' %}">
	</head>
	<body>
	  <div class="container-fluid">
	    <div class="row">
	      <div class="col-sm-2">
	      {% block sidebar %}
	        <ul class="sidebar-nav">
	          <li><a href="{% url 'staff-home' %}">Home</a></li>
	          <li><a href="#">Digital Levels</a></li>
	          <li><a href="#">Add a new staff</a></li>
	        </ul>
	     {% endblock %}
	      </div>
	      <div class="col-sm-10 ">
	      	{% block content %}

	      	{% endblock %}
	      </div>
	    </div>
	  </div>
	</body>
	</html>

It has a title, sidebar navigation, link to css through ``load static`` and ``static`` template tags, ``url`` tag linking to the ``staff-home`` resource URL, and two ``blocks``. 

Home page (``staff_list.html``) template
****************************************
In order to create the home page or any other HTML pages with the same outlook as the ``base_generic.html``, it is now just a matter of inserting the required texts or data inside the ``content`` block. Create a new HTML file staff_list.html in /staff/staffs/templates/staffs/ and paste the following code in the file. This code extends the ``base_generic.html`` base template, and then replaces the default ``content`` block for the template. 

.. code-block:: html

	{% extends 'base_generic.html' %}                /* imports the base template */
	{% block content %}                              /* insert all required texts/data inside this block*/

		<article class="post">
			<header class="post-header">
				<h1 class="post-title text-center">List of staves</h1>
			</header>

			<div class="post-content">
				{% if object_list %}
					<table>
						<tr>
							<th>Staff Number</th>
		        			<th>Staff Type</th>
		        			<th>Staff Length</th>
		        			<th>Correction Factor</th>
		        			<th>Standard Temperature</th>
		        			<th>Last Calibrated</th>
						</tr>
					{% for staff in object_list %}
						<tr style="text-align:center">
							<td> {{ staff.staff_number }} </td>
							<td>{{ staff.staff_type }} </td>
							<td>{{ staff.staff_length }}</td>
							<td>{{ staff.correction_factor|floatformat:7 }}</td>
							<td>{{ staff.standard_temperature|floatformat:1 }}</td>
							<td>
								{{ staff.calibration_date }}
							</td>
						</tr>
					{% endfor %}
					</table>
				{% else %}
					<p> There are currently no staves listed </p>
				{% endif %}
			</div>
		</article>
	{% endblock %}

In the above **list-view** template, the following must be noted:

1. *View context*: The class-based view passes the context (list of staves) by default as ``object_list``. The template receives the ``object_list`` as a list of objects.

2. *Conditional execution*: Like python or any other programming languages, django html templates use ``if``, ``else``, and ``endif`` template tags to check the ``object_list``- to check if any records exists inside the object. In the above html template, if ``object_list`` is empty, the ``else`` clause will display the text - *"There are currently no staves listed"*. Otherwise, it iterates through the lists to display the fields of each staff. 

	.. code-block:: html

		{% if object_list %}
		  <!-- code here to list the staves -->
		{% else %}
		  <p> There are currently no staves listed </p>
		{% endif %}

3. *For Loops*: The template also uses the ``for`` and ``endfor`` template tags to iterate through the ``object_list`` as shown below:
	
	.. code-block:: html
	
		{% for staff in object_list %}
  			<li> <!-- code here get information from each staff item --> </li>
		{% endfor %}

4. *Accessing variables/items*: Each ``staff`` object in the ``for`` loop can be accessed with its model **field** names using a **dot** notation - e.g., ``staff.staff_number``. It is also possible to call functions that sit inside the models, e.g., ``get_absolute_urls()`` to get URLs to display details on a different HTML template.

5. *Table*: Tables are a convenient way to present list information to the users. The above template HTML table template tags (``<table>...</table>``) to present the list of staves. The field names are hardcoded in the headers (``<th>...</th>``) and the list items are displayed in the rows (``<tr>...</tr>``) below under each appropriate column (``<td>...</td>``). 

How does the home page look like?
*********************************

Using the ``base_generic.html`` designed for this Staff Calibration project, the home page looks like this:

.. figure::  homepage.png
   :align:   center

   First home (index) page showing the list of staves registered in the project

