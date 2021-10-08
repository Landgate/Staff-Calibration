from django import forms
from datetime import date
# import models
from .models import uCalibrationUpdate
from staffs.models import Staff, DigitalLevel

# make your forms
class StaffForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(StaffForm, self).__init__(*args, **kwargs)
        if user.is_staff:
            self.fields['staff_number'].queryset = Staff.objects.all()
            self.fields['level_number'].queryset = DigitalLevel.objects.all()
        else:
            self.fields['staff_number'].queryset = Staff.objects.filter(staff_owner = user.authority)
            self.fields['level_number'].queryset = DigitalLevel.objects.filter(level_owner = user.authority)
    class Meta:
        model = uCalibrationUpdate
        fields = ['staff_number', 'level_number', 'calibration_date', 'first_name', 'last_name','start_temperature', 'end_temperature', 'document']
        widgets = {
            'staff_number': forms.Select(attrs={'required': 'true'}),
            'level_number': forms.Select(attrs={'required': 'true'}),
            'calibration_date': forms.DateInput(format=('%d-%m-%Y'), attrs={'placeholder':'Select a date', 'type':'date'}),
            }
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':'Enter first name'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':'Enter last name'}))
    start_temperature = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder':'Enter between 0 and 45'}))
    end_temperature = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder':'Enter between 0 and 45'}))
    document = forms.FileField(widget=forms.FileInput(attrs={'accept' : '.csv, .txt'}))

    def clean_calibration_date(self):
        calibration_date = self.cleaned_data['calibration_date']
        if calibration_date > date.today():
            raise forms.ValidationError("The observation date cannot be in the future!")
        return calibration_date


