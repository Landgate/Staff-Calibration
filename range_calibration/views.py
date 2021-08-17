from django.http import HttpResponse #JsonResponse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.views import generic
from django.db.models import Avg
from datetime import date
from django.conf import settings
from django.core.files.storage import FileSystemStorage
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
from staffs.models import StaffType, Staff, DigitalLevel#, Surveyors

import os
import pandas as pd
import numpy as np
from datetime import datetime



FORMS = [("prefill_form", RangeForm1),
         ("upload_data", RangeForm2),
        ]         

TEMPLATES  = {"prefill_form": "range_calibration/staff_data_form_1.html",
             "upload_data": "range_calibration/staff_data_form_2.html",
             }

def IsNumber(value):
    "Checks if string is a number"
    try:
        float(value)
        check = True
    except:
        check = False
    return(check)

def handle_uploaded_file(f):
    root_dir = os.path.join(settings.UPLOAD_ROOT, 'range_data')
    file_path = os.path.join(root_dir, f.name)
    # file_path = "/range_data/"+f.name
    if not os.path.exists(file_path):
        with open(file_path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
    return file_path

def Process_File(file_path):
    with open(file_path, 'r') as f: 
        fileType = None
        for line in f:
            if "BFOD" in line:
                fileType = "BFOD"
            elif "Level Type" in line:
                fileType = "DNA03"
                break
    if fileType == "BFOD":
        return ImportBFOD_v18(file_path)
    elif fileType == "DNA03":
        return ImportDNA(file_path)
            
def ImportBFOD_v18(file_path):
    with open(file_path, 'r', newline='') as f:
    # # Start reading the level run and store them in blocks
        readerLines = f.readlines()# .decode('UTF-8')
        Blocks = []; block = []
        for line in readerLines:# f:
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
        #----------------------------------------------------------------------
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
    # return data
    return new_staff_reading

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

# Correct staff readings
def rawdata_to_table(dataset, T1, T2, staff_atrs):
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
###############################################################################
######################### SessionWizardView ###################################
###############################################################################
class RangeCalibrationWizard(LoginRequiredMixin, SessionWizardView):
    # get the template names and their steps
    def get_template_names(self):				
        return [TEMPLATES[self.steps.current]]
    
    def perm_check(self):
        if not self.request.user.has_perm("monitorings.manage_perm", self.monitoring):
            raise PermissionDenied()

    # directory to store the ascii files
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, '/uploads')) #

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
###############################################################################
###################### Least Squares Adjustment ###############################
###############################################################################
# Unique list
def unique_list(dataset):
    ulist = []
    for d in dataset:
        # get the list of pins from the second column
        if d[1] in ulist:
            pass
        else:
            ulist.append(d[1])
    return ulist

# adjustment
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
                for j in range(len(W)):
                    output_adj.append([interval, '{:.5f}'.format(adjusted_hdiff), '{:.5f}'.format(W[j]), '{:.5f}'.format(residual[j]),
                                 '{:.2f}'.format(obs_std_dev[j]*1000), '{:.2f}'.format(stdev_residual[j]*1000), 
                                 '{:.1f}'.format(std_residual[j])])
                output_hdiff.append([interval, '{:.5f}'.format(adjusted_hdiff), '{:.2f}'.format(uncertainty), len(dato)])
    return output_hdiff, output_adj

# adjust view
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
###############################################################################
# Compute Annual Cycle
###############################################################################
@login_required(login_url="/accounts/login")
def range_parameters(request):
    # Table
    isChart = False
    # rows & columns
    p_list = ['1-2','2-3','3-4','4-5','5-6','6-7','7-8','8-9','9-10','10-11','11-12','12-13','13-14','14-15','15-16','16-17','17-18','18-19','19-20','20-21']
    labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    
    # check if there are new calibrations not included in the range parameter
    staff = Calibration_Update.objects.filter(update_table__isnull=True)
    if staff.exists():
        staff = staff.values_list('update_index', 'observation_date')
        staff = np.array(staff, dtype=object)
        monthlist = [[x.strftime('%b'), x.month] for x in staff[:,1]]
        # staff = np.append(staff,np.array(monthlist).T, axis=1)
        staff = np.append(staff,np.c_[monthlist], axis=1)
        monthlist, indices  = np.unique(staff[:,-1], return_index=True)
        month_text = staff[indices,2]
        for i in range(len(monthlist)):
            m_number = monthlist[i]
            m_text = month_text[i]
            ht_diff = HeightDifferenceModel.objects.filter(observation_date__month=m_number).values_list(
                                'pin','adjusted_ht_diff','uncertainty')   
            ht_diff = np.array(ht_diff, dtype=object)
            if len(ht_diff)>=1:
                for p in p_list:
                    diff = ht_diff[ht_diff[:,0]==p][:,1]
                    if RangeParameters.objects.filter(pin=p):
                        if len(diff)==1:
                            RangeParameters.objects.filter(pin=p).update(**{m_text: round(diff[0],5)})
                        elif len(diff) == 2:
                            mdiff = diff.mean()
                            RangeParameters.objects.filter(pin=p).update(**{m_text: round(mdiff,5)})
                        elif len(diff) > 2:
                            mdiff = diff.mean()
                            mad = np.sum(abs(diff-mdiff))/len(diff)
                            if mad == 0:
                                mdiff2 = diff.mean()
                            else:
                                madev = 0.6745*(abs(diff-mdiff))/mad
                                ind = madev.argsort()[:2]
                                mdiff2 = diff[ind].mean()
                            RangeParameters.objects.filter(pin=p).update(**{m_text: round(mdiff2,5)})
                    else:
                        if len(diff)==1:
                            obj, created = RangeParameters.objects.update_or_create(pin=p, **{m_text: round(diff[0],5)})
                        elif len(diff) == 2:
                            mdiff = diff.mean()
                            obj, created = RangeParameters.objects.update_or_create(pin=p, **{m_text: round(mdiff,5)})
                        elif len(diff) > 2:
                            mdiff = diff.mean()
                            mad = np.sum(abs(diff-mdiff))/len(diff)
                            if mad == 0:
                                mdiff2 = diff.mean()
                            else:
                                madev = 0.6745*(abs(diff-mdiff))/mad
                                ind = madev.argsort()[:2]
                                mdiff2 = diff[ind].mean()
                            obj, created = RangeParameters.objects.update_or_create(pin=p, **{m_text: round(mdiff2,5)})
    
            messages.info(request, "Updated values for "+m_text+" on "+date.today().strftime('%Y-%m-%d')+"") 
        # update calibration table
        for update_index in staff[:,0]:
            Calibration_Update.objects.filter(update_index=update_index).update(update_table=True)
        return redirect('range_calibration:range-parameters')
    else:  
        param = RangeParameters.objects.all()
        if param.exists():
            param = param.values_list('pin','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')
            parameters = {'headers': ['Pin','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], 'data': param}
            
            # Figure
            param = np.array(param)[:,1:].astype(float)
            tmp = np.nansum(param, axis=0)
            # get total
            total = ["Sum"]
            for t in tmp:
                if t == 0:
                    total.append('null')
                else:
                    total.append(t)
            tmp[tmp==0] = np.nan
            if np.sum(~np.isnan(tmp)) > 1:
                tmp = (tmp-np.nanmean(tmp))
                tmp[np.isnan(tmp)] = 0
                
                isChart = True
            data = []
            for t in tmp:
                if t == 0:
                    data.append('null')
                else:
                    data.append(t*1000)
            context = {'param': parameters,
                       'labels': labels,
                       'data': data,
                       'total': total,
                       'isChart': isChart}
            return render(request, 'range_calibration/range_parameters.html', context)
        else:
            messages.warning(request, "You do not have any range calibration records.")
            return redirect('range_calibration:range-home')

@login_required(login_url="/accounts/login")    
def update_range_param(request):
    p_list = ['1-2','2-3','3-4','4-5','5-6','6-7','7-8','8-9','9-10','10-11','11-12','12-13','13-14','14-15','15-16','16-17','17-18','18-19','19-20','20-21']
    staff = Calibration_Update.objects.filter(update_table__isnull=True)
    if staff.exists():
        staff = staff.values_list('update_index', 'observation_date')
        staff = np.array(staff, dtype=object)
        monthlist = [[x.strftime('%b'), x.month] for x in staff[:,1]]
        # staff = np.append(staff,np.array(monthlist).T, axis=1)
        staff = np.append(staff,np.c_[monthlist], axis=1)
        monthlist, indices  = np.unique(staff[:,-1], return_index=True)
        month_text = staff[indices,2]
        for i in range(len(monthlist)):
            m_number = monthlist[i]
            m_text = month_text[i]
            ht_diff = HeightDifferenceModel.objects.filter(observation_date__month=m_number).values_list(
                                'pin','adjusted_ht_diff','uncertainty')   
            ht_diff = np.array(ht_diff, dtype=object)
            if len(ht_diff)>=1:
                for p in p_list:
                    diff = ht_diff[ht_diff[:,0]==p][:,1]
                    if RangeParameters.objects.filter(pin=p):
                        if len(diff)==1:
                            RangeParameters.objects.filter(pin=p).update(**{m_text: round(diff[0],5)})
                        elif len(diff) == 2:
                            mdiff = diff.mean()
                            RangeParameters.objects.filter(pin=p).update(**{m_text: round(mdiff,5)})
                        elif len(diff) > 2:
                            mdiff = diff.mean()
                            mad = np.sum(abs(diff-mdiff))/len(diff)
                            madev = 0.6745*(abs(diff-mdiff))/mad
                            ind = madev.argsort()[:2]
                            mdiff2 = diff[ind].mean()
                            # print(mdiff2)
                            RangeParameters.objects.filter(pin=p).update(**{m_text: round(mdiff2,5)})
                    else:
                        if len(diff)==1:
                            obj, created = RangeParameters.objects.update_or_create(pin=p, **{m_text: round(diff[0],5)})
                        elif len(diff) == 2:
                            mdiff = diff.mean()
                            obj, created = RangeParameters.objects.update_or_create(pin=p, **{m_text: round(mdiff,5)})
                        elif len(diff) > 2:
                            mdiff = diff.mean()
                            mad = np.sum(abs(diff-mdiff))/len(diff)
                            madev = 0.6745*(abs(diff-mdiff))/mad
                            ind = madev.argsort()[:2]
                            mdiff2 = diff[ind].mean()
                            obj, created = RangeParameters.objects.update_or_create(pin=p, **{month_text: round(mdiff2,5)})
    
            messages.info(request, "Updated values for "+m_text+" on "+date.today().strftime('%Y-%m-%d')+"") 
        # update calibration table
        for update_index in staff[:,0]:
            Calibration_Update.objects.filter(update_index=update_index).update(update_table=True)
        return redirect('range_calibration:range-parameters')
    else:
        messages.warning(request, "This table is already up-to-date!")
        return redirect('range_calibration:range-parameters')

###############################################################################
# print report
###############################################################################        
@login_required(login_url="/accounts/login")
def range_report(request, update_index):
    # Range measurement attributes
    staff_number = Calibration_Update.objects.get(update_index=update_index).staff_number.staff_number
    level_number = Calibration_Update.objects.get(update_index=update_index).level_number
    observation_date = datetime.strptime(update_index.split('-')[0],'%Y%m%d').strftime('%d-%m-%Y')

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

###############################################################################
# delete report
###############################################################################
@login_required(login_url="/accounts/login")
def delete_report(request, update_index):
    # index = Calibration_Update.objects.exclude(update_index=update_index)
    # raw_data = RawDataModel.objects.exclude(update_index=update_index)
    # ht_diff = HeightDifferenceModel.objects.exclude(update_index=update_index) 
    # adj_data = AdjustedDataModel.objects.exclude(update_index=update_index)
    
    # Delete records corresponding to the selected update_index
    Calibration_Update.objects.filter(update_index=update_index).delete()
    RawDataModel.objects.filter(update_index=update_index).delete()
    HeightDifferenceModel.objects.filter(update_index=update_index).delete()
    AdjustedDataModel.objects.filter(update_index=update_index).delete()
    
    # reset range parameters by deleting
    RangeParameters.objects.all().delete()

    # rows & columns
    p_list = ['1-2','2-3','3-4','4-5','5-6','6-7','7-8','8-9','9-10','10-11','11-12','12-13','13-14','14-15','15-16','16-17','17-18','18-19','19-20','20-21']
    
    # Compute the calibration range values
    index = Calibration_Update.objects.all()
    if index.exists():
        index = index.values_list('update_index', 'observation_date')
        index = np.array(index, dtype=object)
        monthlist = [[x.strftime('%b'), x.month] for x in index[:,1]]
        # staff = np.append(staff,np.array(monthlist).T, axis=1)
        index = np.append(index,np.c_[monthlist], axis=1)
        monthlist, indices,ncounts  = np.unique(index[:,-1], return_index=True, return_counts=True)
        month_text = index[indices,2]
        for i in range(len(monthlist)):
            m_number = monthlist[i]
            m_text = month_text[i]
            n_count = ncounts[i]
            ht_diff = HeightDifferenceModel.objects.filter(observation_date__month=m_number).values_list(
                                'pin','adjusted_ht_diff','uncertainty')   
            ht_diff = np.array(ht_diff, dtype=object)
            if len(ht_diff)>=1:
                for p in p_list:
                    diff = ht_diff[ht_diff[:,0]==p][:,1]
                    if RangeParameters.objects.filter(pin=p):
                        if len(diff)==1:
                            RangeParameters.objects.filter(pin=p).update(**{m_text: round(diff[0],5)})
                        elif len(diff) == 2:
                            mdiff = diff.mean()
                            RangeParameters.objects.filter(pin=p).update(**{m_text: round(mdiff,5)})
                        elif len(diff) > 2:
                            mdiff = diff.mean()
                            mad = np.sum(abs(diff-mdiff))/len(diff)
                            if mad == 0:
                                mdiff2 = diff.mean()
                            else:
                                madev = 0.6745*(abs(diff-mdiff))/mad
                                ind = madev.argsort()[:2]
                                mdiff2 = diff[ind].mean()
                            RangeParameters.objects.filter(pin=p).update(**{m_text: round(mdiff2,5)})
                    else:
                        if len(diff)==1:
                            obj, created = RangeParameters.objects.update_or_create(pin=p, **{m_text: round(diff[0],5)})
                        elif len(diff) == 2:
                            mdiff = diff.mean()
                            obj, created = RangeParameters.objects.update_or_create(pin=p, **{m_text: round(mdiff,5)})
                        elif len(diff) > 2:
                            mdiff = diff.mean()
                            mad = np.sum(abs(diff-mdiff))/len(diff)
                            if mad == 0:
                                mdiff2 = diff.mean()
                            else:
                                madev = 0.6745*(abs(diff-mdiff))/mad
                                ind = madev.argsort()[:2]
                                mdiff2 = diff[ind].mean()
                            obj, created = RangeParameters.objects.update_or_create(pin=p, **{m_text: round(mdiff2,5)})
    
            messages.info(request, "Updated range parameters for "+m_text+" using "+str(n_count)+" of observation sets") 
    else:
        messages.warning(request, "Nothing to display.") 
    return redirect('range_calibration:range-home')

###############################################################################
######################### PRINT REPORT ########################################
###############################################################################
from django_xhtml2pdf.utils import generate_pdf
@login_required(login_url="/accounts/login")
def print_report(request, update_index):
    resp = HttpResponse(content_type='application/pdf')
    
    # Range measurement attributes
    staff_number = Calibration_Update.objects.get(update_index=update_index).staff_number.staff_number
    level_number = Calibration_Update.objects.get(update_index=update_index).level_number
    observation_date = datetime.strptime(update_index.split('-')[0],'%Y%m%d').date()

    observer = Calibration_Update.objects.get(update_index=update_index).surveyor
    if observer.first_name:
        observer_name = f"{observer.last_name}, {observer.first_name}"
    else:
        observer_name = observer.email

    # Get the staff readings from RawDataModel
    raw_data = RawDataModel.objects.filter(update_index=update_index)
    average_temperature = RawDataModel.objects.filter(update_index=update_index).aggregate(Avg('temperature'))
    # print(raw_data)
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
###############################################################################
###################### HOME AND GUIDELINE VIEWS ###############################
###############################################################################
class HomeView(generic.ListView):
    model = Calibration_Update
    paginate_by = 25
    template_name = 'range_calibration/range_calibration_home.html'

    ordering = ['-observation_date']
    
@login_required(login_url="/accounts/login")
def guide_view(request):
    return render(request, 'range_calibration/range_calibration_guide.html')
###############################################################################
