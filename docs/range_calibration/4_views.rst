Views & Templates
=================

Overview
--------

In this application, we will use the ``SessionWizardView`` subclass from ``formtools`` to render the two-step form as well as process form data, and insert & update the database via the various models defined previously. This **WizardView** class will need to handle a lot of external and internal functions to store and read files, pre-process and post-process the staff readings and simultaneously update the database tables. 

Multiple views & templates have been designed to perform simple computations and least squares adjustments, display and print range calibration reports specific to users by authority (or use company) and for administrators (i.e., geodesy@landgate.wa.gov.au and others who have access to this email group). 


SessionWizardView
-----------------

The two-step form is managed using the ``SessionWizardView`` from ``formtolls.wizard.views``. The ``SessionWizardView`` is defined in **views.py** and has a method called ``done()``, which specifies what should happen when the data from the list of forms are submitted and validated. Please see the example below from the official ``formtools`` document.

1. **forms.py**: 
	.. code-block:: python

		#filename: forms.py

		from django import forms

		class ContactForm1(forms.Form):
		    subject = forms.CharField(max_length=100)
		    sender = forms.EmailField()

		class ContactForm2(forms.Form):
		    message = forms.CharField(widget=forms.Textarea)

2. **views.py**: 
	.. code-block:: python
		
		# filename: views.py

		from django.shortcuts import render
		from formtools.wizard.views import SessionWizardView

		class ContactWizard(SessionWizardView):
		    def done(self, form_list, **kwargs):
		        return render(self.request, 'done.html', {
		            'form_data': [form.cleaned_data for form in form_list],
		        }) 

3. **templates**: The templates expect a wizard object with the following tags: 

	* form – The Form or BaseFormSet instance for the current step (either empty or with errors).
	* steps – A helper object to access the various steps related data:
	* step0 – The current step (zero-based).
	* step1 – The current step (one-based).
	* count – The total number of steps.
	* first – The first step.
	* last – The last step.
	* current – The current (or first) step.
	* next – The next step.
	* prev – The previous step.
	* index – The index of the current step.
	* all – A list of all steps of the wizard.

	See this example from their official document:

	.. code-block:: HTML

		#filename: done.html

		{% extends "base_generic.html" %}
		{% load i18n %}

		{% block content %}
			<p>Step {{ wizard.steps.step1 }} of {{ wizard.steps.count }}</p>
			<form action="" method="post">{% csrf_token %}
				<table>
					{{ wizard.management_form }}
					{% if wizard.form.forms %}
					    {{ wizard.form.management_form }}
					    {% for form in wizard.form.forms %}
					        {{ form }}
					    {% endfor %}
					{% else %}
					    {{ wizard.form }}
					{% endif %}
				</table>
				{% if wizard.steps.prev %}
					<button name="wizard_goto_step" type="submit" value="{{ wizard.steps.first }}">{% trans "first step" %}</button>
					<button name="wizard_goto_step" type="submit" value="{{ wizard.steps.prev }}">{% trans "prev step" %}</button>
				{% endif %}
				<input type="submit" value="{% trans "submit" %}"/>
			</form>
		{% endblock %}

4. **URL**: The wizard's ``as_view()`` method takes a list of your Form classes as an argument during instantiation: 
	
	.. code-block:: python

		#filename: urls.py

		from django.path import path

		from myapp.forms import ContactForm1, ContactForm2
		from myapp.views import ContactWizard

		urlpatterns = [
		    path('contact/', ContactWizard.as_view([ContactForm1, ContactForm2])),
		]

5. **Handling files**: To handle ``FileField`` within any step form of the wizard, we have to add a ``file_storage`` to the ``SessionWizardView`` subclass. The ``file_storage`` attribute can be defined as shown in the example below:

	.. code-block:: python

		#filename: views.py

		from django.conf import settings
		from django.core.files.storage import FileSystemStorage

		class CustomWizardView(WizardView):
		    ...
		    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'photos')) # create folder called photos and make it media root folder.
		    
	For the **range_calibration** app, we will store the ascii files like this:

	.. code-block:: python

		file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'range_data/uploads'))



RangeCalibrationWizard - Form View
----------------------------------

Let's create a ``SessionWizardView`` called ``RangeCalibrationWizard`` to handle the range calibration data, processing, model integration, and required template displays. 

.. code-block:: python

	#filename: staff/range_calibration/views.py

	from django.contrib import messages
	from django.shortcuts import render, redirect, get_object_or_404
	from django.core.exceptions import ObjectDoesNotExist
	from django.views import generic
	from django.db.models import Avg, Sum
	from datetime import date
	from django.conf import settings
	from django.core.files.storage import DefaultStorage, FileSystemStorage
	from django.contrib.auth.mixins import LoginRequiredMixin
	from django.contrib.auth.decorators import login_required
	from formtools.wizard.views import SessionWizardView

	from .forms import (
	        RangeForm1,
	        RangeForm2,
	    )

	from .models import (Calibration_Update, 
	                     RawDataModel,
	                     AdjustedDataModel,
	                     HeightDifferenceModel,
	                     RangeParameters,
	                     )

	from staffs.models import (StaffType, 
								Staff, 
								DigitalLevel)

	import os
	import pandas as pd
	import numpy as np
	from datetime import datetime

	FORMS = [("prefill_form", RangeForm1),
	         ("upload_data", RangeForm2),
	        ]         

	TEMPLATES  = {"prefill_form": "range_calibration/staff_data_form_1.html",
	             "upload_data": "range_calibration/staff_data_form_2.html",

	class RangeCalibrationWizard(LoginRequiredMixin, SessionWizardView):
		# get the template names and their steps
	    def get_template_names(self):				
	        return [TEMPLATES[self.steps.current]]
	    
	    def perm_check(self):
	        if not self.request.user.has_perm("monitorings.manage_perm", self.monitoring):
	            raise PermissionDenied()

	    # directory to store the ascii files
	    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'range_data/uploads')) #
	    
	    # get the user
	    def get_form_kwargs(self, step=1):
	        kwargs = super(RangeCalibrationWizard, self).get_form_kwargs(step)
	        kwargs['user'] = self.request.user
	        return kwargs
	        
	  
	    def done(self, form_list, **kwargs):
	        # get the data from the form in a key value format
	        data = {k: v for form in form_list for k, v in form.cleaned_data.items()}
	        
	        ## Update Calibration_Update Model ##
	        # generate the primary id using date and staff_number
	        update_index = data['observation_date'].strftime('%Y%m%d')+'-'+ data['staff_number'].staff_number

	        # check if the index exists in Calibration_Update table - 
	        if Calibration_Update.objects.filter(update_index=update_index).count() == 0:
	        	# if no - proceed and add the fields shown below
	            Calibration_Update.objects.create(staff_number=Staff.objects.get(staff_number=data['staff_number'].staff_number), 
	                                            level_number = DigitalLevel.objects.get(level_number=data['level_number'].level_number), 
	                                            surveyor = self.request.user,
	                                            observation_date = data['observation_date'])

	            # Retrieve temperatures and compute the average
	            Set_1_AvgT = (data['start_temperature_1']+data['end_temperature_1'])/2
	            Set_2_AvgT = (data['start_temperature_2']+data['end_temperature_2'])/2
	            
	            # Extract the parameters for the staff_number       
	            Staff_Attributes = {'dCorrectionFactor': Staff.objects.get(staff_number=data['staff_number'].staff_number).correction_factor*10**-6, 
	                                'dStdTemperature': Staff.objects.get(staff_number=data['staff_number'].staff_number).standard_temperature,
	                                'dThermalCoefficient': StaffType.objects.get(staff_type=data['staff_number'].staff_type).thermal_coefficient*10**-6}
	            
	            # Get the ascii file and read it to a table
	            data_file_path = handle_uploaded_file(data['document'])                                # path to uploaded ascii
	            if data_file_path.endswith('.asc') or data_file_path.endswith('.ASC'):                 # set file type to upload
	                staff_reading = Process_File(data_file_path)                                       # get the staff readings a table format using Process_File
	                range_measurement = rawdata_to_table(staff_reading, Set_1_AvgT, Set_2_AvgT, Staff_Attributes) # get all the elements together
	            
	            
	            # check if this range is already loaded in RawDataModel table. if so delete it
	            if RawDataModel.objects.filter(update_index=update_index):
	                RawDataModel.objects.filter(update_index=update_index).delete()
	            
	            # Add the range readings to the RawDataModel
	            for key, value in range_measurement.items():
	                if key == 'data':
	                    for items in value:
	                        RawDataModel.objects.create(
	                                        update_index = update_index,
	                                        staff_number = data['staff_number'].staff_number, 
	                                        observation_date = data['observation_date'], 
	                                        obs_set = items[0], 
	                                        pin = items[1],
	                                        temperature = items[2], 
	                                        frm_pin = items[3],
	                                        to_pin = items[4],
	                                        standard_deviation = items[5], 
	                                        observed_ht_diff = items[6], 
	                                        corrected_ht_diff = items[7])

	            # Get the user name/email                           
	            observer = self.request.user
	            if observer.first_name:
	                observer_name  =observer.first_name +' ' + self.request.user.last_name
	            else:
	                observer_name = observer.email

	            # build the context to render to the template
	            context = {
	                    'update_index': update_index,
	                    'staff_number': data['staff_number'].staff_number,
	                    'level_number': data['level_number'],
	                    'observer': observer_name,
	                    'observation_date': data['observation_date'],
	                    'average_temperature': (Set_1_AvgT+Set_2_AvgT)/2,
	                    'range_measurement': range_measurement
	                }
	 
	            return render(self.request, 'range_calibration/range_reading_report.html',  context = context)
	        
	        # Otherwise display a message indicating the table is already up to date. 
	        else:
	            messages.error(self.request, 'File already uploaded.')
	            return redirect('/')

Handling & storing the uploaded ascii file
******************************************

.. code-block:: python
	
	#filename: staff/range_calibration/views.py

	def handle_uploaded_file(f):
		# directory to store the file
	    file_path = "data/range_data/uploads/"+f.name

	    # if file does not exisit, create a new one
	    if not os.path.exists(file_path):
	        with open(file_path, 'wb+') as destination:
	            for chunk in f.chunks():
	                destination.write(chunk)
	    return file_path

Pre-processing the ascii file
*****************************

.. code-block:: python
	
	#filename: staff/range_calibration/views.py
	
	def Process_File(file_path):
		# open the file
	    with open(file_path, 'r') as f: 
	    	# check the structure of ascii file
	        fileType = None
	        for line in f:
	            if "BFOD" in line:
	                fileType = "BFOD"
	            elif "Level Type" in line:
	                fileType = "DNA03"
	                break

	    # read the ascii based on their structure and format it into a table - ['SET', PIN','READING','COUNT','STD_DEVIATION']
	    if fileType == "BFOD":
	        return ImportBFOD_v18(file_path)
	    elif fileType == "DNA03":
	        return ImportDNA(file_path)

Leica digital level data are stored in a raw file called **.gsi** format. This can can be exported to a human readable ascii format (**.asc**). Depending on the Leica model, two different ascii formats have been used by Landgate - indicated by (i) ``ImportBFOD_v18`` and (ii) ``ImportDNA`` in the ``Process_File()``. See how the two file formats are read below:

1. **BFOD_v18**: 
	
	.. code-block:: python

		#filename: staff/range_calibration/views.py

		def ImportBFOD_v18(file_path):
		    with open(file_path, 'r', newline='') as f:
		        readerLines = f.readlines()
		        Blocks = []; block = []
		        for line in readerLines:
		            line = line.strip()
		            col = line.split('|')[1:]
		            
		            # Start level run 
		            if line.startswith('|---------|---------|---------|---------|------------'):
		                if block:
		                    Blocks.append(block)
		                    block = []
		            elif len(col) == 11:
		                block.append(col)
		        if block:
		            Blocks.append(block)  
		 
		        # Finally store the staff readings into a table/list format and store    
		        new_staff_reading = {}
		        j = 0
		        for i in range(len(Blocks)):
		            block = Blocks[i]
		            if len(block)>7:
		                j += 1
		                staff_data = []
		                for r in block:
		                    r = [x.strip() for x in r]
		                    if (IsNumber(r[0]) or IsNumber(r[1]) or IsNumber(r[2])):
		                        if IsNumber(r[0]):
		                            Pin = r[8]; Readings = r[0]; NoOfMeasurement = r[6]; Stdev = r[7]; 
		                        elif IsNumber(r[1]):
		                            Pin = r[8]; Readings = r[1]; NoOfMeasurement = r[6]; Stdev = r[7]; 
		                        elif IsNumber(r[2]):
		                            Pin = r[8]; Readings = r[2]; NoOfMeasurement = r[6]; Stdev = r[7]; 
		                        staff_data.append([Pin, float(Readings), NoOfMeasurement, float(Stdev)])
		                #print(i)
		                staff_data  = pd.DataFrame(staff_data, columns=['PIN','READING','COUNT','STD_DEVIATION'])
		                # Save to dictionary
		                new_staff_reading.update({'Set'+str(j):staff_data})
		        return new_staff_reading

2. **ImportDNA**: 
	
	.. code-block:: python

		#filename: staff/range_calibration/views.py

		def ImportDNA(file_path):
		    with open(file_path, 'r') as f: 
		        # Start reading the level run and store them in blocks
		        readerLines = f.readlines()# .decode('UTF-8')
		        Blocks = []; block = []
		        for line in readerLines:
		            line = line.strip()
		            col = line.split('|')[1:]
		            # Start level run 
		            if line.endswith('| MS |___DEV__|___________|'):
		                if block:
		                    Blocks.append(block)
		                    block = []
		            elif len(col) == 10:
		                block.append(col)
		        if block:
		            Blocks.append(block)      
		        #----------------------------------------------------------------------
		        # Finally store the staff readings into a table/list format and store
		        new_staff_reading = {}
		        j = 0
		        for i in range(len(Blocks)):
		            block = Blocks[i]
		            if len(block)>7:
		                j += 1
		                # Append items
		                Pin = []; Readings = []; Stdev = []; NoOfMeasurement = None
		                staff_data = []
		                for r in block:
		                    r = [x.strip() for x in r]
		                    if (IsNumber(r[0]) or IsNumber(r[1]) or IsNumber(r[2])):
		                        if IsNumber(r[0]):
		                            Pin = r[8]; Readings = r[0]; Stdev = r[7]; NoOfMeasurement = r[6]
		                        elif IsNumber(r[1]):
		                            Pin = r[8]; Readings = r[1]; Stdev = r[7];
		                        elif IsNumber(r[2]):
		                            Pin = r[8]; Readings = r[2]; Stdev = r[7];
		                        
		                        staff_data.append([Pin, float(Readings), NoOfMeasurement, float(Stdev)])
		                staff_data  = pd.DataFrame(staff_data, columns=['PIN','READING','COUNT','STD_DEVIATION'])
		                new_staff_reading.update({'Set'+str(j):staff_data})
		    return new_staff_reading

Checking for real values - ``IsNumber()``

.. code-block:: python
	
	#filename: staff/range_calibration/views.py

	def IsNumber(value):
	    "Checks if string is a number"
	    try:
	        float(value)
	        check = True
	    except:
	        check = False
	    return(check)

Calculate height differences from ``staff_reading``
***************************************************

Here, ``staff_reading = rawdata_to_table(...)`` (i.e., from, to table) are converted to height differences and temperature corrections are applied using their calibration parameters (or constants).

.. code-block:: python

	#filename: staff/range_calibration/views.py

	def rawdata_to_table(dataset, T1, T2, staff_atrs):
		# input - staff_reading, T1, T2, and calibration parameters

	    dCorrectionFactor = staff_atrs['dCorrectionFactor']
	    dThermalCoefficient = staff_atrs['dThermalCoefficient']
	    dStdTemperature = staff_atrs['dStdTemperature']
	    
	    rawReportTable = []
	    for key, value in dataset.items():
	        if key.startswith("Set1"):
	            obs_set = 1
	            set1 = calculate_length(value.values, dCorrectionFactor, dThermalCoefficient, dStdTemperature, T1, obs_set)
	        elif key.startswith("Set2"):
	            obs_set = 2
	            set2 = calculate_length(value.values, dCorrectionFactor, dThermalCoefficient, dStdTemperature, T2, obs_set)

	    rawReportTable = {'headers': ['SET','PIN','TEMPERATURE','FROM','TO', 'STD_DEVIATION', 'MEASURED', 'CORRECTED'], 'data': set1+set2}
	    return rawReportTable

The actual calculation is done here by ``calculate_length()``:

.. code-block:: python

	#filename: staff/range_calibration/views.py

	def calculate_length(dat, cf, alpha, t_0, t, oset):
		# dat - table data (values.values)
		# cf - dCorrectionFactor
		# alpha - dThermalCoefficient
		# t_0 - dStdTemperature
		# t - T1 or T2
		# oset - obs_set

	    from math import sqrt

	    data_table = []
	    for i in range(len(dat)-1):
	        pini, obsi, nmeasi, stdi= dat[i] 
	        pinj, obsj, nmeasj, stdj = dat[i+1]
	        if stdi == 0:
	            stdi = 10**-5
	        if stdj == 0:
	            stdj = 10**-5
	        dMeasuredLength = obsj- obsi
	        dCorrection = (1+cf)*(1+alpha*(float(t)-t_0))
	        cMeasuredLength = dMeasuredLength*dCorrection
	        dStdDeviation = sqrt(float(stdi)**2 + float(stdj)**2)
	        data_table.append([str(oset), pini+'-'+pinj, '{:.1f}'.format(float(t)),
	                                    '{:.5f}'.format(obsi), '{:.5f}'.format(obsj), '{:.6f}'.format(dStdDeviation),
	                                    '{:.5f}'.format(dMeasuredLength), '{:.5f}'.format(cMeasuredLength)])
	    return data_table

RangeCalibrationWizard - URL Mapper
-----------------------------------

The URL mapper (**urls.py**) for the ``RangeCalibrationWizard`` class looks like this:

.. code-block:: python

	#filename: staff/range_calibration/urls.py

	from django.urls import path
	from . import views
	from .forms import (
	        RangeForm1,
	        RangeForm2,
	    )

	app_name = 'range_calibration'

	FORMS = [("prefill_form", RangeForm1),
	         ("upload_data", RangeForm2),
	        ]         

	urlpatterns = [
	    ...
	    path('range_calibrate/', views.RangeCalibrationWizard.as_view(FORMS), name='range-calibrate'),
	    ...

	]

RangeCalibrationWizard - Template
---------------------------------

``RangeCalibrationWizard`` only renders one template (i.e., **range_reading_report.html**) that will have all the nicely formatted information produced by ``rawdata_to_table()`` from the data provided by ``Process_File()`` and other input parameters. The template has a ``Adjust`` button on the top right hand corner to do the least squares adjustment:

.. code-block:: HTML
	
	#filename: staff/range_calibration/templates/range_calibration/range_reading_report.html

	{% extends 'base_generic.html' %}

	{% if messages %}
	  {% for message in messages %}
	    <div>
	        <strong>{{message|safe}}</strong>
	    </div>
	  {% endfor %}
	  {% endif %}
	 
	{% block content %}
	<div class="page-content">
	  <div class="grid-2"> 
	    <div style="text-align:center">
	      <h1>Staff Calibration Report</h1>
	    </div>
	    <div style="text-align:right">
	      <a href="{% url 'range_calibration:range-adjust' update_index %}">
	        <button class="px-3 py-1 border border-transparent text-base leading-4 font-small rounded text-white bg-red-600 hover:bg-red-500 focus:outline-none focus:shadow-outline transition duration-150 ease-in-out" >Adjust&raquo;</button>
	      </a>
	    </div>
	  </div>
	  <hr>
	  <div class="grid-2">
	    <div>
	      <h2>This test information</h2>
	      <div>
	        Unique ID: {{ update_index }}
	      </div>
	      <div>
	        Observation Date: {{ observation_date }}
	      </div>
	      <br> <br>
	      <div>
	        Average Temperature: {{ average_temperature|floatformat:1 }}&#8451;
	      </div>

	    </div>
	    <div>
	      <h2>Level &amp; staff details </h2>
	      <div>
	        Staff Number: {{ staff_number }}
	      </div>
	      <div>
	        Level Number: {{ level_number}}
	      </div>
	      <br> <br>
	      <div>
	        Observer: {{ observer }}
	      </div>
	    </div>
	  </div>
	</div>  
	<hr>
	<div class="page-content">
	  <h1> Displaying range measurements</h1>
	  <table style="width:100%; margin-left:2em; border-collapse: collapse; "> 
	    <tr style="border-top:1px solid; border-bottom:1px solid">
	      {% for header in range_measurement.headers %}
	          <th> <h3> {{ header }} </h3> </th>
	      {% endfor %}
	    </tr>

	    {% for data in range_measurement.data %}
	      <tr style="text-align:center; border-bottom:1px solid">    
	        {% for value in data %}
	          <td>{{ value }}</td>
	        {% endfor %}
	      </tr>
	      {% endfor %}
	    </tr>
	  </table>
	  </div>
	{% endblock content %}


Adjustment of Staff Readings - ``range_adjust()``
-------------------------------------------------

The ``range_adjust()`` function in **views.py** will use ``request`` and ``update_index`` to do the least squares adjustment on the ``staff_reading`` stored in the model ``RawDataModel``. To trigger this function, users must click the ``Adjust`` button in the template described above. 

URL Mapper
**********

.. code-block:: python

	#filename: staff/range_calibration/urls.py

	...        

	urlpatterns = [
	    ...
	    path('range_adjust/<update_index>/', views.range_adjust, name='range-adjust'),
	    ...

	] 

Adjustment View - ``range_adjust()``
************************************

.. code-block:: python

	#filename: staff/range_calibration/views.py

	def range_adjust(request, update_index):
		# Extract the data from the RawDataModel for the requested update_index
	    dat = RawDataModel.objects.filter(update_index=update_index)

	    # process it if data exists
	    if len(dat)>=1:
	        dat = dat.values_list(
	                        'obs_set','pin','temperature','frm_pin','to_pin',
	                        'observed_ht_diff','corrected_ht_diff', 'standard_deviation')
	        
	        # get a unique list of pin-pin
	        this_ulist = unique_list(dat)

	        # do the adjustment for the readings supplied
	        output_ht_diff, output_adjustement = adjustment(dat, this_ulist)
	        
	        # Check the HeightDifferenceModel if record exists, if so delete them
	        if HeightDifferenceModel.objects.filter(update_index=update_index):
	            HeightDifferenceModel.objects.filter(update_index=update_index).delete()
	        
	        # Now add the records to the HeightDifferenceModel
	        for pin, d, u, c in output_ht_diff:
	            HeightDifferenceModel.objects.create(observation_date= datetime.strptime(update_index.split('-')[0],'%Y%m%d').date(),
	                                              update_index=update_index, 
	                                              pin=pin, 
	                                              adjusted_ht_diff=d, 
	                                              uncertainty=u, 
	                                              observation_count=c)
	        # Check the AdjustedDataModel if record exists, if so delete them
	        if AdjustedDataModel.objects.filter(update_index=update_index):
	            AdjustedDataModel.objects.filter(update_index=update_index).delete()
	        
	        # Now add the records to the AdjustedDataModel
	        for pin, adj, obs, resd, ostd, sdevr, stdres in output_adjustement:
	            AdjustedDataModel.objects.create(observation_date = datetime.strptime(update_index.split('-')[0],'%Y%m%d').date(),
	                                           update_index = update_index, 
	                                           pin = pin, 
	                                           observed_ht_diff = obs, 
	                                           adjusted_ht_diff = adj, 
	                                           residuals = resd, 
	                                           standard_deviation = ostd, 
	                                           std_dev_residual = sdevr, 
	                                           standard_residual =stdres)

	        # Success message and redirect to range_calibration home page
	        messages.success(request, f'Successfully adjusted the pin to pin height differences using this staff: { update_index }')
	        return redirect('/range_calibration/')
	    
	    # if data does not exist, return to the form page
	    else:
	         messages.error(request, "This observation set does not exist. Please upload again to proceed.")
	         return redirect("range_calibration:range-calibrate")

The adjustment is done using ``adjustment()`` below:

.. code-block:: python

	#filename: staff/range_calibration/views.py

	def adjustment(dataset, uniquelist):
	    from math import sqrt
	    dataset = np.array(dataset)
	    
	    output_adj = []; output_hdiff = []
	    for i in range(len(uniquelist)):
	        x = uniquelist[i]
	        if x in dataset[:,1]:
	            dato = dataset[dataset[:,1]==x].tolist()

	            # if there is only one observation - PIN 1-7 and PIN 15-21
	            if len(dato) == 1:
	                interval = dato[0][1]
	                adjusted_hdiff = '{:.5f}'.format(float(dato[0][-2]));
	                observed_hdiff = '{:.5f}'.format(float(dato[0][-2]));
	                residual = '{:.5f}'.format(0.0)
	                obs_std_dev = '{:.2f}'.format(float(dato[0][-1])*1000)
	                stdev_residual = '{:.2f}'.format(0.0)
	                std_residual = '{:.2f}'.format(0.0)
	                uncertainty = '{:.2f}'.format(float(dato[0][-1])*1000*1.96)
	                output_adj.append([interval, adjusted_hdiff, observed_hdiff, residual,
	                               obs_std_dev, stdev_residual, std_residual])
	                output_hdiff.append([interval, adjusted_hdiff, uncertainty, len(dato)])
	            
	            # if two or more observations exists, do the least squares adjustment - PIN 7-15
	            elif len(dato) > 1:
	                interval = dato[0][1]
	                dato = np.array(dato, dtype=object)

	                # Prepare the required arrays
	                W = dato[:,-2].astype(np.float); P = np.diag(1/(dato[:,-1].astype(np.float))**2); A = np.ones(len(W))

	                # Perform Least squares - Refer to J.Klinge & B. Hugessen document on Calibration of Barcode staffs
	                adjusted_hdiff = (np.matmul(np.transpose(A), np.matmul(P, W)))/(np.matmul(np.transpose(A), np.matmul(P, A))) # (A_T*P*A)^(-1)*A_T*P*W
	                residual = np.array(adjusted_hdiff  - W, dtype=float)
	                obs_std_dev = np.sqrt(1./np.sqrt(np.diag(P).astype(float))**2)
	                stdev_residual = np.sqrt(1./np.sqrt(np.diag(P).astype(float))**2 - 1./sqrt(np.matmul(np.transpose(A), np.matmul(P, A)))**2)
	                uncertainty = (sqrt(1/np.matmul(np.transpose(A), np.matmul(P, A)))*1000*1.96)
	                std_residual = np.round_(residual/stdev_residual,1)

	                # Prepare the outputs - 
	                						(i) adjusted height differences & uncertainties - output_hdiff
	                						(ii) adjustment results - output_adj
	                for j in range(len(W)):
	                    output_adj.append([interval, '{:.5f}'.format(adjusted_hdiff), '{:.5f}'.format(W[j]), '{:.5f}'.format(residual[j]),
	                                 '{:.2f}'.format(obs_std_dev[j]*1000), '{:.2f}'.format(stdev_residual[j]*1000), 
	                                 '{:.1f}'.format(std_residual[j])])
	                output_hdiff.append([interval, '{:.5f}'.format(adjusted_hdiff), '{:.2f}'.format(uncertainty), len(dato)])
	    return output_hdiff, output_adj

And the ``unique_list()``:

.. code-block:: python

	#filename: staff/range_calibration/views.py

	def unique_list(dataset):
	    ulist = []
	    for d in dataset:
	    	# get the list of pins from the second column
	        if d[1] in ulist:
	            pass
	        else:
	            ulist.append(d[1])
	    return ulist

Adjustment reports
******************

1. **URL mapper**:

	.. code-block:: python

		#filename: staff/range_calibration/urls.py

		...        

		urlpatterns = [
		    ...
		    path('range_report/<update_index>/', views.range_report, name='range-report'),
	    	path('print_report/<update_index>/', views.print_report, name='print-report'),
		    ...

		] 

2. **Views**: ``range_report()`` takes the ``request`` and ``update_index`` and extracts the required information from the relevant models to prepare the report and render it in a template called **adjustment_report.html**. 


	.. code-block:: python

		#filename: staff/range_calibration/views.py

		@login_required(login_url="/accounts/login")
		def range_report(request, update_index):
		    # Range measurement attributes
		    staff_number = Calibration_Update.objects.get(update_index=update_index).staff_number.staff_number
		    level_number = Calibration_Update.objects.get(update_index=update_index).level_number
		    observation_date = datetime.strptime(update_index.split('-')[0],'%Y%m%d').date(),

		    observer = Calibration_Update.objects.get(update_index=update_index).surveyor
		    if observer.first_name:
		        observer_name = f"{observer.last_name}, {observer.first_name}"
		    else:
		        observer_name = observer.email
		        
		    # Get the staff readings from RawDataModel
		    raw_data = RawDataModel.objects.filter(update_index=update_index)
		    average_temperature = RawDataModel.objects.filter(update_index=update_index).aggregate(Avg('temperature'))
		    
		    if len(raw_data)>=1:
		        raw_data = raw_data.values_list(
		                        'obs_set','pin','temperature','frm_pin','to_pin',
		                        'observed_ht_diff','corrected_ht_diff', 'standard_deviation')
		        raw_data = {'headers': ['SET','PIN','TEMPERATURE','FROM','TO','STD DEV','OBSERVED HEIGHT DIFF','CORRECTED_HEIGHT DIFF'], 'data': [list(x) for x in raw_data]} 
		    else:
		        messages.error(request, 'No staff information to display.')

		    # Get the adjusted height differences from HeightDifferenceModel
		    ht_diff = HeightDifferenceModel.objects.filter(update_index=update_index)   
		    if len(ht_diff)>=1:
		        ht_diff = ht_diff.values_list(
		                        'pin','adjusted_ht_diff','uncertainty','observation_count')
		        ht_diff = {'headers': ['PIN','HEIGHT DIFF','UNCERTAINTY(mm)','OBSERVATION COUNT'], 'data': [list(x) for x in ht_diff]}
		    else:
		        messages.error(request, 'No height differences can be displayed.')

		    # Get the adjustment results from AdjustedDataModel        
		    adj_data = AdjustedDataModel.objects.filter(update_index=update_index)
		    if len(adj_data)>=1:
		        adj_data = adj_data.values_list(
		                        'pin','adjusted_ht_diff','observed_ht_diff','residuals',
		                        'standard_deviation','std_dev_residual','standard_residual')
		        adj_data = {'headers': ['PIN','ADJ HEIGHT DIFF','OBS HEIGHT DIFF','RESIDUAL','STANDARD DEVIATION','STDEV RESIDUAL','STANDARD_RESIDUAL'], 'data':  [list(x) for x in adj_data]} 
		    else:
		        messages.error(request, f'No adjustments found for this staff: { update_index }')

		    # Prepare the context to be rendered
		    context = {
		            'update_index': update_index,
		            'observation_date': observation_date,
		            'staff_number': staff_number,
		            'level_number': level_number,
		            'observer': observer_name,
		            'average_temperature': average_temperature['temperature__avg'], # get the average observed temperature
		            'raw_data': raw_data,
		            'ht_diff_data': ht_diff,
		            'adj_data': adj_data
		            }
		    return render(request, 'range_calibration/adjustment_report.html', context)

	The HTML template is very similar to the shown the ``SessionWizardView`` with some tweats to accommodate the tables for adjusted height differences and adjustment results. 

	``print_report()`` renders the above report in a **pdf** format. While the core function is the same, it needs some additional Django tools to render it as a pdf format. First, we have to install ``django-xhtml2pdf`` and ``xhtml2pdf`` from the command prompt and import the ``generate_pdf`` function. The ``generate_pdf`` requires the pdf report template, file object describing its content type (i.e., pdf), and the context element to render. See below:

	.. code-block:: python

		#filename: staff/range_calibration/views.py

		from django_xhtml2pdf.utils import generate_pdf
		@login_required(login_url="/accounts/login")
		def print_report(request, update_index):
		    resp = HttpResponse(content_type='application/pdf')
		    
		    # Range measurement attributes
		    staff_number = Calibration_Update.objects.get(update_index=update_index).staff_number.staff_number
		    level_number = Calibration_Update.objects.get(update_index=update_index).level_number
		    observation_date = datetime.strptime(update_index.split('-')[0],'%Y%m%d').date(),

		    observer = Calibration_Update.objects.get(update_index=update_index).surveyor
		    if observer.first_name:
		        observer_name = f"{observer.last_name}, {observer.first_name}"
		    else:
		        observer_name = observer.email

		    # Get the staff readings from RawDataModel   
		    if len(raw_data)>=1:
		        raw_data = raw_data.values_list(
		                        'obs_set','pin','temperature','frm_pin','to_pin',
		                        'observed_ht_diff','corrected_ht_diff', 'standard_deviation')
		        raw_data = {'headers': ['SET','PIN','TEMPERATURE','FROM','TO','STD DEV','OBSERVED HEIGHT DIFF','CORRECTED_HEIGHT DIFF'], 'data': [list(x) for x in raw_data]} 
		    else:
		        messages.error(request, 'No staff information to display.')

		    # Get the adjusted height differences from HeightDifferenceModel
		    ht_diff = HeightDifferenceModel.objects.filter(update_index=update_index)   
		    if len(ht_diff)>=1:
		        ht_diff = ht_diff.values_list(
		                        'pin','adjusted_ht_diff','uncertainty','observation_count')
		        ht_diff = {'headers': ['PIN','HEIGHT DIFF','UNCERTAINTY(mm)','OBSERVATION COUNT'], 'data': [list(x) for x in ht_diff]}
		    else:
		        messages.error(request, 'No height differences can be displayed.')

		    # Get the adjustment results from AdjustedDataModel                   
		    adj_data = AdjustedDataModel.objects.filter(update_index=update_index)
		    if len(adj_data)>=1:
		        adj_data = adj_data.values_list(
		                        'pin','adjusted_ht_diff','observed_ht_diff','residuals',
		                        'standard_deviation','std_dev_residual','standard_residual')
		        adj_data = {'headers': ['PIN','ADJ HEIGHT DIFF','OBS HEIGHT DIFF','RESIDUAL','STANDARD DEVIATION','STDEV RESIDUAL','STANDARD_RESIDUAL'], 'data':  [list(x) for x in adj_data]} 
		    else:
		        messages.error(request, f'No adjustments found for this staff: { update_index }')

		    # Prepare the context to be rendered
		    context = {
		            'update_index': update_index,
		            'observation_date': observation_date,
		            'staff_number': staff_number,
		            'level_number': level_number,
		            'observer': observer_name,
		            'average_temperature': average_temperature['temperature__avg'],
		            'raw_data': raw_data,
		            'ht_diff_data': ht_diff,
		            'adj_data': adj_data,
		            'today': datetime.now().strftime('%d/%m/%Y  %I:%M:%S %p'),
		            }
		    result = generate_pdf('range_calibration/pdf_range_report.html', file_object=resp, context=context)
		    return result

Range Calibration - How it looks?
---------------------------------

1. Home View - ``Get started now`` button leads to the form page. Unique indices are hyperlinked to display pdf reports and the ``Report>>`` buttons will render the adjustment reports.

	.. figure:: home_page.png
		:align: center


2. Report View - This report template has a button at the top right to display the report as pdf.

	.. figure:: adjustment_report.png
		:align: center

3. PDF Report - This can generated either by clicking on the index hyperlink in the home page or by clicking the button on report template:

	.. figure:: pdf_report.png
		:align: center