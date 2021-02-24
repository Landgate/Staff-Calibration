Django application framework
----------------------------

Django web framework follows the MVT or Model View Template architechture which is based on the MVC or Model View Controller architechture. Django itself acts as the controller (i.e., the business logic or rules) to interact between the model and the view. A brief description of the MVT architechture is provided below:

* **MODEL** - A *model* is a Python class that helps to handle database by providing access to the database. The Python class object contains all the required fields and behaviors of the data that is being stored. Models help developers to create, read, update, and delete objects (CRUD operations) in the database. Models also contain the business logic, custom methods, properties, and other things related to data manipulation.

* **VIEW** - The *view* executes the business logic by interacting with the model(s) and renders the data to the template(s). Apart from interacting with the model and rendering the data to the templates, the view also accepts HTTP requests, applies business logic provided by Python classes and methods, and provides HTTP responses to the client requests.

* **TEMPLATE** - The *template* is the presentation layer (i.e., the front-end) that handles the user interface. Templates are files written in HTML and also renders the data passed by the view.

The figure below shows how each of the above elements work together to form a web application. The template is the front-end that interacts with the view and the model is the back-end that interacts with the database. The view has access to both the model and the templates and finally maps it to a **URL**. The **Manager** acts as the interface between the *model* and the database. 

.. figure::  django_model.jpg
   :align:   center

   The django web framework.



How does django application look like?
--------------------------------------


Sending the request to the right view (urls.py)
***********************************************

A URL mapper is stored in a file called **urls.py**. In the example below, the mapper (``urlpatterns``) defines a list of mappings between routes (specific URL patterns) and corresponding view functions. If an HTTP Request is received that has a URL matching a specified pattern, then the associated view function will be called and passed to the request.

.. code-block:: Python

	urlpatterns = [
	    path('admin/', admin.site.urls),
	    path('staff/<int:id>/', views.staff_details, name='staff_detail'),
	    path('staff/', include('staff.urls')),
	]

The ``urlpatterns`` object is a list of ``path()`` and/or ``re_path()`` functions (Python lists are defined using square brackets, where items are separated by commas and may have an optional trailing comma. For example: ``[item1, item2, item3,]``). The first argument defines the route (pattern) that will be matched. The second argument, for example ``views.staff_detail`` is the function that is being called to render the defined route. ``staff_detail()`` is found in the ``views.py``. 

Handling the request (views.py)
*******************************

Views are the heart of Django web application, receiving HTTP requests from web clients and returning HTTP responses. In the process, views interact with models and templates and facilitate all the tasks in between. Views are usually stored in a file called ``views.py``.

The example below shows a minimal view function ``index()``, which could have been called by our URL mapper in the previous section. The view receives a ``HttpRequest`` object as a parameter (``request``) and returns an ``HttpResponse`` object. Here, nothing is done with the request, and the response simply returns a text field. 

.. code-block:: Python

	# filename: views.py (Django view functions)

	from django.http import HttpResponse

	def index(request):
	    # Get an HttpRequest - the request parameter
	    # perform operations using information from the request.
	    # Return HttpResponse
	    return HttpResponse('Hello from Django!')

Defining data models (models.py)
********************************

Django web applications manage and query data through Python class objects referred to as **models**. Models define the structure of data being stored, including the field types and their maximum size, default values, selection list options, help text for documentation, label text for forms, etc. The model is independent of the underlying database and therefore, can choose one of several existing databases as part of the project settings. 

As an example, a very simple Django model called ``DigitalLevel`` is defined below. The ``DigitalLevel`` class is derived from the django class ``models.Model``. It defines the ``level_number`` and ``level_model`` as character fields and specifies a maximum number of characters to be stored for each record. The ``level_make`` can be one of several values, so we define it as a choice field and provide a mapping between choices to be displayed and data to be stored, along with a default value. 

.. code-block:: Python

	# filename: models.py

	from django.db import models 

	class DigitalLevel(models.Model): 
	    level_number = models.CharField(max_length=40) 
	    
	    level_make = (
	        ('LEI', 'LEICA'),
	        ('TRIM', 'TRIMBLE'),
	        ('SOK', 'SOKIA'),
	        ...  #list other makes
	    )

	    level_model = models.CharField(max_length=40) 

Querying data (views.py)
************************

The code snippet below shows a view function for displaying all our Trimble digital levels by using the model query (``filter``) and render the list to a ``staff_list.html`` template. 

.. code-block:: Python

	## filename: views.py

	from django.shortcuts import render
	from .models import Team 

	def index(request):
	    list_levels = DigitalLevels.objects.filter(level_make__exact="TRIM")
	    context = {'list_levels': list_levels}
	    return render(request, '/staff/staff_list.html', context)

The ``render()`` function creates a HttpResponse that is sent back to the browser. It renders the HTML file by integrating the HTML template with the data provided through the ``context`` python object.

Rendering data (HTML templates)
*******************************

The **template** specifies the structure of an output document, using placeholders for data that will be filled in when a page is generated. Templates are often used to create HTML, but can also create other types of document. 

The code snippet shows what the HTML template called by the ``render()`` function in the previous section might look like. This template has been written under the assumption that it will have access to a list variable called ``list_levels`` when it is rendered (this is contained in the ``context`` variable inside the ``render()`` function above). Inside the HTML skeleton we have an expression that first checks if the list_levels variable exists, and then iterates it in a ``for`` loop. On each iteration the template displays level details in an ``<li>`` element.

.. parsed-literal:: 
	## filename: staff/templates/staff/level_list.html

	<!DOCTYPE html>
	<html lang="en">
	<head>
	  <meta charset="utf-8">
	  <title>Home page</title>
	</head>
	<body>
	  {% if list_levels %}
	    <ul>
	      {% for level in list_levels %}
	        <li>Level Number: {{ level.level_number }}</li>
	        <li>Level Make: {{ level.level_make }}</li>
	        <li>Level Model: {{ level.level_model }}</li>
	      {% endfor %}
	    </ul>
	  {% else %}
	    <p>No levels are found at the moment. You can add your digital level by logging in.</p>
	  {% endif %}
	</body>
	</html>

Other Django features
*********************

Additionally, Django framework includes many functions and interfaces including:

* **Forms**: HTML Forms are used to collect user data for processing on the server. Django simplifies form creation, validation, and processing.
* **User authentication, permissions and groups**: Django includes a robust user authentication and permission system that has been built with security in mind. 
* **Caching**: Creating content dynamically is much more computationally intensive (and slow) than serving static content. Django provides flexible caching so that you can store all or part of a rendered page so that it doesn't get re-rendered except when necessary.
* **Administration site**: The Django administration site is included by default when you create an app using the basic skeleton. It makes it trivially easy to provide an admin page for site administrators to create, edit, and view any data models in your site.
* **Serialising data**: Django makes it easy to serialise and serve your data as XML or JSON. This can be useful when creating a web service (a website that purely serves data to be consumed by other applications or sites, and doesn't display anything itself), or when creating a website in which the client-side code handles all the rendering of data.

