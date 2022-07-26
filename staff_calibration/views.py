from django.shortcuts import render, redirect
from django.contrib import messages
import os, csv, io, numpy as np
from math import sqrt
from .forms import StaffForm
from .models import uCalibrationUpdate, uRawDataModel
from staffs.models import Staff, StaffType
from range_calibration.models import RangeParameters
from datetime import date
from django.contrib.auth.decorators import login_required 
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from staffs.models import Staff
from django.db.models import Q
from django.conf import settings
from django.db import IntegrityError
#from accounts.models import CustomUser
# Create your views here.

def homeview(request):
    return redirect('/')

def guideview(request):
    return render(request, 'staff_calibration/staff_calibration_guide.html')

# Staff lists
@login_required(login_url="/accounts/login")
def user_staff_lists(request):
    if request.user.is_staff:
        staff_lists = uCalibrationUpdate.objects.all().order_by('-processed_date')[:10]
    else:
        staff_lists = uCalibrationUpdate.objects.filter(staff_number__staff_owner = request.user.authority).order_by('-processed_date')[:10]
    context = {
        'staff_lists': staff_lists}
    return render(request, 'staff_calibration/user_staff_lists.html', context=context)

# delete staffs
def user_staff_delete(request, update_index):
    try: 
        if uCalibrationUpdate.objects.filter(user= request.user).exists():
            # Delete Calibration update
            user_staff = uCalibrationUpdate.objects.get(user= request.user, update_index=update_index)
            user_staff.delete()
            messages.success(request, 'Calibration record deleted.')
            # Delete raw data
            user_staff_data = uRawDataModel.objects.filter(user= request.user, update_index=update_index)
            user_staff_data.delete()
            messages.success(request, 'Raw data record deleted.')
            # return to the registry list
            return redirect('staff_calibration:user-staff-lists')
        else:
            messages.warning(request, 'This staff belongs to another person. You cannot delete it.')
            return redirect('staff_calibration:user-staff-lists')
    except:
        messages.error(request, 'This action cannot be performed. Contact Landgate.')
        return redirect('staff_calibration:user-staff-lists')

# Check if its number 
def isnumber(x):
    try:
        return type(int(x)) == int
    except ValueError:
        return False

# handle data file
def handle_uploaded_file(f):
    root_dir = os.path.join(settings.UPLOAD_ROOT, 'client_data')
    file_path = os.path.join(root_dir, f.name[:-4]+'-'+date.today().strftime('%Y%m%d')+'.csv')
    # file_path = "data/client_data/"+f.name
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path

# Preprocess staff readings to calculate the height differences between pins
def preprocess_staff(data_set):
    data_set = np.array(data_set, dtype=object)
    observation_set = []
    for i in range(len(data_set)-1):
        pini, obsi, nmeasi, stdi = data_set[i] 
        pinj, obsj, nmeasj, stdj = data_set[i+1]
        if float(stdi) == 0:
            stdi = 10**-5
        if float(stdj) == 0:
            stdj = 10**-5
        dMeasuredLength = float(obsj)- float(obsi)
        dStdDeviation = sqrt(float(stdi)**2 + float(stdj)**2)
        observation_set.append([str(pini)+'-'+str(pinj), 
                            '{:.5f}'.format(float(obsi)), '{:.5f}'.format(float(obsj)), 
                            '{:.5f}'.format(dMeasuredLength), 
                            '{:.7f}'.format(dStdDeviation)])
    return observation_set

# generate correction factor from below
def generate_correction_factor(uncorrected_scale_factor, staff_meta):
    list_scale_factors = []
    start_temperature = 0.
    end_temperature = 40.
    interval = 2.
    while start_temperature <= end_temperature:
        scale_factor = (((start_temperature-staff_meta['dObsTemperature'])*staff_meta['dThermalCoefficient'])+1)*uncorrected_scale_factor
        correction = (scale_factor-1)*1000.
        list_scale_factors.append([str(int(start_temperature)), '{:.6f}'.format(scale_factor), '{:.2f}'.format(correction)])
        
        start_temperature += interval
    return list_scale_factors

# Calculate the correction factor
def process_correction_factor(data_set, reference_set, meta):
    data_set = np.array(data_set, dtype=object)
    reference_set = np.array(reference_set, dtype=object)

    # order of pins
    order = reference_set[:,0]
    
    # Find common pin numbers
    arr, ref_ind, dat_ind = np.intersect1d(reference_set[:,0], data_set[:,0], return_indices=True)
    reference_set = reference_set[ref_ind,:]
    data_set = data_set[dat_ind,:]

    # order them as per pin numbers
    ref_set2 = []
    dat_set2 = []
    for row in order:
        try:
            ref_set2.append(reference_set[reference_set[:,0]==row][0].tolist())
            dat_set2.append(data_set[data_set[:,0]==row][0].tolist())
        except:
            pass
    del reference_set
    del data_set
    # array them
    reference_set = np.array(ref_set2,dtype=object)
    data_set = np.array(dat_set2,dtype=object)
    # output tables
    adjusted_corrections = []
    #allocate arrays
    W = np.zeros([len(data_set)])
    A = np.ones([len(data_set)])
    sum_sq_diff = np.zeros([len(data_set)])
    variance = np.zeros([len(data_set)])
    j = 0
    for i in range(len(W)):
        j+=1
        pin, frm, to, diff, std = data_set[i]
        if pin in reference_set[:,0]:
            known_length = reference_set[reference_set[:,0]==pin][0][1]
            measured_length = float(diff) #* (((meta['dObsTemperature']-meta['dStdTemperature'])*meta['dThermalCoefficient'])+1)
            corrected_length = float(diff) * (((meta['dObsTemperature']-meta['dStdTemperature'])*meta['dThermalCoefficient'])+1)
            correction = float(known_length) - float(measured_length)
            # squared differences
            sum_sq_diff[j-1,] = (float(known_length) - measured_length)**2
            # Variance
            variance[j-1,] = float(std)
            # Scale factor
            W[j-1] = float(known_length) / float(measured_length)
            # Table 1
            adjusted_corrections.append([pin, frm, to, known_length, '{:.5f}'.format(measured_length),'{:.5f}'.format(correction)])
    # Now do the least squares adjustment
    P = np.diag(1/variance**2)
    dCorrectionFactor1 = (np.matmul(np.transpose(A), np.matmul(P, W)))/(np.matmul(np.transpose(A), np.matmul(P, A)))
    dCorrectionFactor1 = round(dCorrectionFactor1, 8)
    # Correction Factors
    dCorrectionFactor0 = (((meta['dStdTemperature']-meta['dObsTemperature'])*meta['dThermalCoefficient'])+1)*dCorrectionFactor1
    # dCorrectionFactor0 = round(dCorrectionFactor1/(((meta['dStdTemperature'] - meta['dObsTemperature'])*
    #                              meta['dThermalCoefficient'])+1), 8)            # at 25degC           
    alt_temperature = round((1+dCorrectionFactor1*(meta['dObsTemperature']*meta['dThermalCoefficient']-1))
                            /(meta['dThermalCoefficient']*dCorrectionFactor1),1)                             # Correction Factor = 1
    # Graduation Uncertainty at 95% Confidence Interval
    graduation_uncertainty = sqrt(np.sum(sum_sq_diff)/(len(W)-1))*1.96
    # tables 1
    adjusted_corrections = {'headers': ['PIN','FROM','TO', 'REFERENCE', 'MEASURED', 'CORRECTIONS'], 
                            'data': adjusted_corrections}
    # tables 2
    list_factors_corrections = {'headers': ['Temperature','Correction Factor','Correction/metre [mm]'], 
                                'data': generate_correction_factor(dCorrectionFactor1, meta)}
    return dCorrectionFactor0, graduation_uncertainty, adjusted_corrections, dCorrectionFactor1, alt_temperature, list_factors_corrections   
  
# Staff form 
@login_required(login_url="/accounts/login")     
def calibrate(request):
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            data = form.cleaned_data
            
            # Staff Attributes from Form
            staff_number = data['staff_number'].staff_number
            level_number = data['level_number'].level_number
            observation_date = data['calibration_date']
            if data['last_name']:
                observer = data['last_name'] + ', ' + data['first_name']
            elif request.user.last_name:
                observer = request.user.last_name + ', '+ request.user.first_name
            else:
                observer = request.user.email
            if request.user.authority:
                authority =  request.user.authority.authority_name
            else:
                authority = 'Langate'

            update_index = data['calibration_date'].strftime('%Y%m%d')+'-'+data['staff_number'].staff_number
            st_tmp = data['start_temperature']; end_tmp = data['end_temperature']
            ave_temperature = (float(st_tmp)+float(end_tmp))/2
            
            # Ge staff attributes from model
            this_staff = Staff.objects.get(staff_number=staff_number)
            Staff_Attributes = {'dObsTemperature': ave_temperature, 
                            'dStdTemperature': this_staff.standard_temperature,
                            'dThermalCoefficient': this_staff.staff_type.thermal_coefficient*10**-6}
            month = observation_date.strftime('%b')
            # Getting the range 
            range_value = RangeParameters.objects.values_list('pin', month)
            # if range_value.exists():
            if range_value[0][1]:
                # read file and data
                # thisFile = request.FILES['document']
                thisFile = handle_uploaded_file(data['document'])                                # path to uploaded csv
                # if thisFile.name.endswith('.csv') or thisFile.name.endswith('.txt'):
                #     io_string = io.StringIO(thisFile.read().decode('utf-8'))
                if thisFile.endswith('.csv') or thisFile.endswith('.txt'):
                    has_header = True
                    with open(thisFile, 'r') as f:
                        # read csv
                        csv_reader = csv.reader(f, delimiter=',', quotechar="|")
                        staff_reading = []
                        for row in csv_reader:
                            if isnumber(row[0]):
                                staff_reading.append(row)
                # save raw data to model
                if uRawDataModel.objects.filter(update_index=update_index).count()<1:
                    for pin_number, reading, no_of_readings, stdev in staff_reading:
                        uRawDataModel.objects.create(
                                                user = request.user,
                                                staff_number=staff_number,
                                                calibration_date=observation_date,
                                                pin_number=pin_number,
                                                staff_reading = reading,
                                                number_of_readings = no_of_readings,
                                                standard_deviations=stdev)
                # preprocess data        
                staff_reading2 = preprocess_staff(staff_reading)
                
                # compute scale factor
                try:
                    CF, GradUnc, StaffCorrections, CF0, T_at_CF_1, Correction_Lists = process_correction_factor(staff_reading2, 
                                                                                                            range_value, 
                                                                                                            Staff_Attributes)
                    # update calibration_update table
                    if not uCalibrationUpdate.objects.filter(update_index=update_index):
                        uCalibrationUpdate.objects.create(
                                        user = request.user,
                                        staff_number=data['staff_number'], 
                                        level_number=data['level_number'], 
                                        calibration_date = observation_date, 
                                        observer = observer,
                                        processed_date = date.today(), 
                                        correction_factor = round(CF,6), 
                                        observed_temperature = ave_temperature,
                                        correction_factor_temperature = this_staff.standard_temperature)

                        this_staff.calibration_date = observation_date
                        this_staff.correction_factor = round(CF,6)
                        this_staff.save()
                    # Prepare to populate data
                    context = {
                        'update_index': update_index,
                        'observation_date': observation_date.strftime('%d/%m/%Y'),
                        'staff_number': staff_number,
                        'staff_length': Staff.objects.get(staff_number=staff_number).staff_length,
                        'staff_type': StaffType.objects.get(staff__staff_number=staff_number).staff_type,
                        'thermal_coefficient':StaffType.objects.get(staff__staff_number=staff_number).thermal_coefficient*10**-6,
                        'level_number': level_number,
                        'observer': observer,
                        'authority': authority,
                        'average_temperature': ave_temperature,
                        'ScaleFactor': CF,
                        'GraduationUncertainty': GradUnc,
                        'StaffCorrections': StaffCorrections,
                        'ScaleFactor0': CF0,
                        'Temperatre_at_1': T_at_CF_1,
                        'CorrectionList': Correction_Lists,
                    }
                    return render(request, 'staff_calibration/staff_calibration_report.html', context)
                except IntegrityError:
                    messages.warning(request, '** Processing error! Please check your csv file to confirm with the requirements.')
                    return render(request, 'staff_calibration/staff_calibrate.html', {'form':form})
                #return redirect('staff_calibration:staff-guide')
            else:
                messages.warning(request, 'No range measurements exist for the month of '+month+'. Please try again later or contact Landgate')
                return render(request, 'staff_calibration/staff_calibrate.html', {'form':form})
    else:
        form = StaffForm(user=request.user)
    return render(request, 'staff_calibration/staff_calibrate.html', {'form':form})

# Generating a pdf report
from django_xhtml2pdf.utils import generate_pdf
from django.http import HttpResponse
def generate_report_view(request, update_index):
    resp = HttpResponse(content_type='application/pdf')
    # Fetch data from database
    raw_data = uRawDataModel.objects.filter(update_index = update_index)
    ave_temperature = uCalibrationUpdate.objects.get(update_index= update_index).observed_temperature
    staff_number = uCalibrationUpdate.objects.get(update_index=update_index).staff_number.staff_number
    staff_owner = uCalibrationUpdate.objects.get(update_index=update_index).staff_number.staff_owner
    level_number = uCalibrationUpdate.objects.get(update_index=update_index).level_number
    observation_date = uCalibrationUpdate.objects.get(update_index= update_index).calibration_date

    # define the staff attributes
    Staff_Attributes = {'dObsTemperature': ave_temperature, 
                        'dStdTemperature': Staff.objects.get(staff_number=staff_number).standard_temperature,
                        'dThermalCoefficient': StaffType.objects.get(staff__staff_number=staff_number).thermal_coefficient*10**-6}
    
    # Find the range value from the range database
    month = observation_date.strftime('%b')
    range_value = RangeParameters.objects.values_list('pin', month)

    if range_value.exists():
        # extract data
        staff_reading = raw_data.values_list(
                            'pin_number','staff_reading','number_of_readings','standard_deviations')
        staff_reading = [list(x) for x in staff_reading]
        # preprocess data        
        staff_reading2 = preprocess_staff(staff_reading)

        # compute scale factor
        CF, GradUnc, StaffCorrections, CF0, T_at_CF_1, Correction_Lists = process_correction_factor(staff_reading2, 
                                                                                                    range_value, 
                                                                                                    Staff_Attributes)
        # Observer
        observer = uCalibrationUpdate.objects.get(update_index=update_index)
        #print(observer.observer)
        if observer.observer is None or observer.observer == '' or observer.observer == ',':
            try:
                if request.user.last_name:
                    observer = request.user.last_name + ', '+ request.user.first_name
                else:
                    observer = request.user.email
            except:
                observer = request.user.email
        else:
            observer = observer.observer
        #print(Correction_Lists)
        context = {
                    'update_index': update_index,
                    'observation_date': observation_date.strftime('%d/%m/%Y'),
                    'staff_number': staff_number,
                    'staff_length': Staff.objects.get(staff_number=staff_number).staff_length,
                    'staff_type': StaffType.objects.get(staff__staff_number=staff_number).staff_type,
                    'authority': staff_owner,
                    'thermal_coefficient':StaffType.objects.get(staff__staff_number=staff_number).thermal_coefficient*10**-6,
                    'level_number': level_number,
                    'observer': observer,
                    'average_temperature': ave_temperature,
                    'ScaleFactor': CF,
                    'GraduationUncertainty': GradUnc,
                    'StaffCorrections': StaffCorrections,
                    'ScaleFactor0': CF0,
                    'Temperatre_at_1': T_at_CF_1,
                    'CorrectionList': Correction_Lists,
                    'today': datetime.now().strftime('%d/%m/%Y  %I:%M:%S %p'),
                }
    
        result = generate_pdf('staff_calibration/pdf_staff_report.html', file_object=resp, context=context)
        return  result
    else:
        #print("Not range exists")
        messages.warning(request, 'No range measurements exist for the month of '+month+'. Use the values as shown on the left or try again later.')
        return redirect('staff_calibration:user-staff-lists')
    # return render(request, 'staff_calibration/staff_calibration_report.html', context)
