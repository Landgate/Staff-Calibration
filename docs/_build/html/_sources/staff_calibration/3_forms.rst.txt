Forms
=====

Overview
--------

Before going to the ``view``, we will need to design a form to submit/upload the range measurements carried out at the Boya Range. The form should have the following elements:

1. Select the levelling instruments - staves and digital levels
2. Date picker to select the observaton date. Raise validation errors if a future date is selected or if the date selected is earler than Jan 2018.
3. File uploader to upload the raw range measurements
4. Field to enter start and end temperture for each of the two observation sets


``StaffForm``
-------------

Let us create a new python file called **forms.py** under *staff/staff_calibration/* and create a ``ModelForm`` subclass called ``StaffForm``. The model form will contain ``staff_number``, ``level_number``, ``calibration_update`` from the ``uCalibrationUpdate`` model, data entry for observed temperatures (``start_temperature``, ``end_temperature``), and a file loader (``document``) to load the staff reading (as csv/txt file) as shown below:  

.. code-block:: python

	#filename- staff/staff_calibration/forms.py

	from django import forms

	# import the relevant models
	from .models import uCalibrationUpdate
	from staffs.models import Staff, DigitalLevel

	# make your forms
	class StaffForm(forms.ModelForm):

	    def __init__(self, *args, **kwargs):
	    	# Get the user 
	        user = kwargs.pop('user', None)
	        super(StaffForm, self).__init__(*args, **kwargs)
	        self.fields['staff_number'].queryset = Staff.objects.filter(user__authority = user.authority)
	        self.fields['level_number'].queryset = DigitalLevel.objects.filter(user__authority = user.authority)

	    class Meta:
	        model = uCalibrationUpdate
	        fields = ['staff_number', 'level_number', 'calibration_date', 'start_temperature', 'end_temperature', 'document']
	        widgets = {
	            'staff_number': forms.Select(),
	            'level_number': forms.Select(),
	            'calibration_date': forms.DateInput(format=('%d-%m-%Y'), attrs={'placeholder':'Select a date', 'type':'date'}),
	            }
	    start_temperature = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder':'Enter 0-45'}))
	    end_temperature = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder':'Enter 0-45'}))
	    document = forms.FileField(widget=forms.FileInput(attrs={'accept' : '.csv, .txt'}))


