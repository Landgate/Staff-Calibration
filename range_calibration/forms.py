from django import forms
from .models import Calibration_Update
from staffs.models import Staff, DigitalLevel

# make your forms
class RangeForm1(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(RangeForm1, self).__init__(*args, **kwargs)
        self.fields['staff_number'].queryset = Staff.objects.filter(user__authority = user.authority,
                                                                    staff_type__staff_type__exact = "Invar")
        self.fields['level_number'].queryset = DigitalLevel.objects.filter(user__authority = user.authority)
    
    class Meta:
        model = Calibration_Update
        fields = ['staff_number', 'level_number', 'observation_date']
        widgets = {
            'staff_number': forms.Select(),
            'level_number': forms.Select(),
            'observation_date': forms.DateInput(format=('%d-%m-%Y'), attrs={'class':'django-forms', 'placeholder':'Select a date', 'type':'date'}),
            }

class RangeForm2(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(RangeForm2, self).__init__(*args, **kwargs)

    start_temperature_1 = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder':'Enter 0-45'}))
    end_temperature_1 = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder':'Enter 0-45'}))
    
    start_temperature_2 = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder':'Enter 0-45'}))
    end_temperature_2 = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder':'Enter 0-45'}))
    
    document = forms.FileField(widget=forms.FileInput(attrs={'accept' : '.asc'}))
    #document = forms.FileField()
