Initial data migrations
=======================

Overview
--------

Range measurement and calibration forms the core of the Staff Calibration application. The range calibration consists of more than two years of monthly range measurements at the Boya Staff Calibration Range. These monthly measurements are adjusted and averaged to give one set of range value for each month of the year (i.e., monthly mean). 
Therefore, we need an approach to pre-load all the existing range measurements and avoid the manual task of repeating the process through the ``SessionWizardView``. As explained, this can done by creating a new migration file in the folder called **migrations** (i.e., **staff/range_calibration/migration/**) through ``manage.py``.


Data migrations
---------------

1. Create a new migration file like this:

	.. parsed-literal::

		python manage.py makemigrations --empty range_calibration

	A new migration file with a .py format will be created under **staff/range_calibration/migrations/** and should have a sequence number greater than 1 as ``0001_initial.py`` is generated during the initial migration. For demonstration purposes, here is how the folder looks like:

	.. parsed-literal:: 
	
		staff/
		└──range_calibrations/
			└──migrations/
				├──__init__.py
		  	 	├──0001_initial.py
		  	 	└──0002_auto_20201113_1350.py       # new migration file created

2. **0002_auto_20201113_1350.py** will be run only after *0001_initial.py* and all the data migrations required. The migration intially looks like this:

	.. code-block:: python

		from django.db import migrations

		class Migration(migrations.Migration):

		    dependencies = [
		        ('range_calibration', '0001_initial'),
		    ]

		    operations = [
		    ]	

	So, we need to add the other dependencies and python functions to load, read, and process range information and update the database. This can be done by copying all the relevant functions from **views.py** to **0002_auto_20201113_1350.py** and tweaking them to fit the purpose. Let us first update the ``Migration`` class with the following:

	.. code-block:: python

		# filename: 0002_auto_20201113_1350.py
		'''
			dependencies: 0001_initial - create models and tables
			              0002_auto_20201112_1023 - landgate staff data migrations under staff/staffs/migrations
			upload_range_data: read, process and update range data
			reverse_func: reverse the process by deleting all the data
		'''

		from django.db import migrations

		class Migration(migrations.Migration):

	    dependencies = [
	        ('range_calibration', '0001_initial'),       # initial migration
	        ('staffs', '0002_auto_20201112_1023'),       # data migration in staffs
	    ]

	    operations = [
	    		migrations.RunPython(upload_range_data, reverse_func),
	    ]


``upload_range_data()``
-----------------------

This function sits above the ``Migration`` class and is the combination of functions - load, read, and process raw files and update the database. It is also dependent on the number of functions that are laid above the function itself. 

.. code-block:: python
	
	from django.db import migrations
	import os
	import pandas as pd
	import numpy as np
	import csv
	from datetime import datetime
	from django.db import IntegrityError, transaction

	def upload_range_data(apps, schema_editor):  
	    Staff = apps.get_model("staffs", "Staff")
	    DigitalLevel = apps.get_model("staffs", "DigitalLevel")

	    Calibration_Update = apps.get_model("range_calibration", "Calibration_Update")
	    RawDataModel = apps.get_model("range_calibration", "RawDataModel")
	    AdjustedDataModel = apps.get_model("range_calibration", "AdjustedDataModel")
	    HeightDifferenceModel = apps.get_model("range_calibration", "HeightDifferenceModel")
	    RangeParameters = apps.get_model("range_calibration", "RangeParameters")

		# Starting to read the files
	    root_dir = "data/range_data"
	    # Reading the temperature record
	    if os.path.exists(os.path.join(root_dir, 'temperatures.csv')):
	        with open(os.path.join(root_dir, 'temperatures.csv'), 'r', newline='') as f:
	            csv_reader = csv.reader(f, delimiter=',')
	            next(csv_reader)
	            temperatures = []
	            for row in csv_reader:
	                observation_date = datetime.strptime(row[0], '%d/%m/%Y').date()
	                staff_number = row[1].strip()
	                level_number = row[2].strip()
	                start_temperature1 = float(row[3])
	                end_temperature1 = float(row[4])
	                start_temperature2 = float(row[5])
	                end_temperature2 = float(row[6])
	                
	                temperatures.append([observation_date,
	                                    staff_number,
	                                    level_number,
	                                    start_temperature1,
	                                    end_temperature1,
	                                    start_temperature2,
	                                    end_temperature2])
	            temperatures = np.array(temperatures, dtype=object)
	    # reading thef older    
	    k = 0
	    for root, dirs, files in os.walk(root_dir):
	        for filename in files:
	            if filename.endswith(('.ASC', '.asc')):
	                file_path = os.path.join(root, filename).replace('\\','/')
	                #print(file_path.split('/')[2].split('-')[0])
	                #try:
	                observation_date = datetime.strptime(file_path.split('/')[2].split('-')[0], '%Y%m%d').date()
	                staff_number = Staff.objects.get(staff_number = file_path.split('/')[2].split('-')[1])
	                update_index = observation_date.strftime('%Y%m%d')+'-'+staff_number.staff_number
	                filter_staff = temperatures[(temperatures[:,0]==observation_date) & (temperatures[:,1] == staff_number.staff_number)]
	                if len(filter_staff)>0:
	                    # k +=1
	                    level_number = DigitalLevel.objects.get(level_number = filter_staff[0][2])
	                    Set_1_AvgT = (filter_staff[0][3]+filter_staff[0][4])/2
	                    Set_2_AvgT = (filter_staff[0][5]+filter_staff[0][6])/2
	                    # read the file
	                    staff_reading = Process_File(file_path)
	                    Staff_Attributes = {'dCorrectionFactor': 3.81*10**-6, 
	                                        'dStdTemperature': 19.8,
	                                        'dThermalCoefficient':0.81*10**-6}
	                    range_measurement = rawdata_to_table(staff_reading, Set_1_AvgT, Set_2_AvgT, Staff_Attributes)
	                    
	                    data = np.array(range_measurement['data'], dtype=object)
	                    # switch columns = move standard deviation to end
	                    data[:,[5, 7]] = data[:,[7, 5]]
	                    this_ulist = unique_list(data)
	                    output_ht_diff, output_adjustement = adjustment(data, this_ulist)
	                    
	                    # Update Calibration_Update Model
	                    if Calibration_Update.objects.filter(update_index=update_index).count() == 0:
	                        Calibration_Update.objects.create(
	                                                        update_index = update_index,
	                                                        staff_number=Staff.objects.get(staff_number=staff_number.staff_number),
	                                                        level_number = DigitalLevel.objects.get(level_number=level_number.level_number), 
	                                                        observation_date = observation_date)
	                        k+=1
	                        # print(k)
	                    
	                        
	            
	                        # Insert raw data
	                        if RawDataModel.objects.filter(update_index=update_index):
	                            RawDataModel.objects.filter(update_index=update_index).delete()
	                        # re-insert
	                        for key, value in range_measurement.items():
	                            if key == 'data':
	                                for items in value:
	                                    RawDataModel.objects.create(
	                                                    update_index = update_index,
	                                                    staff_number =staff_number.staff_number, 
	                                                    observation_date = observation_date, 
	                                                    obs_set = items[0], 
	                                                    pin = items[1],
	                                                    temperature = items[2], 
	                                                    frm_pin = items[3],
	                                                    to_pin = items[4],
	                                                    standard_deviation = items[5], 
	                                                    observed_ht_diff = items[6], 
	                                                    corrected_ht_diff = items[7])
	                        # Insert the height differences
	                        if HeightDifferenceModel.objects.filter(update_index=update_index):
	                            HeightDifferenceModel.objects.filter(update_index=update_index).delete()
	                        # re-insert
	                        for pin, d, u, c in output_ht_diff:
	                            HeightDifferenceModel.objects.create(observation_date= observation_date,
	                                                                  update_index = update_index,
	                                                                  pin=pin, 
	                                                                  adjusted_ht_diff=d, 
	                                                                  uncertainty=u, 
	                                                                  observation_count=c)
	                        # Save the adjustments
	                        if AdjustedDataModel.objects.filter(update_index=update_index):
	                            AdjustedDataModel.objects.filter(update_index=update_index).delete()
	                        # re-insert
	                        for pin, adj, obs, resd, ostd, sdevr, stdres in output_adjustement:
	                            AdjustedDataModel.objects.create(observation_date = observation_date,
	                                                              update_index = update_index,
	                                                              pin = pin, 
	                                                              observed_ht_diff = obs, 
	                                                              adjusted_ht_diff = adj, 
	                                                              residuals = resd, 
	                                                              standard_deviation = ostd, 
	                                                              std_dev_residual = sdevr, 
	                                                              standard_residual =stdres)
	                                
	    # Update the range parameters
	    p_list = ['1-2','2-3','3-4','4-5','5-6','6-7','7-8','8-9','9-10','10-11','11-12','12-13','13-14','14-15','15-16','16-17','17-18','18-19','19-20','20-21']

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
	        # update calibration table
	        for update_index in staff[:,0]:
	            Calibration_Update.objects.filter(update_index=update_index).update(update_table=True)

Reading the files
-----------------

The following must be noted while reading the files:

1. The input data in ``root_dir`` contains **temperature.csv** file containing the most of the field metadata and a folder called **range_data/** containing the ascii files. 

2.The staff number and observation date are combined to generate a primary key (called ``update_index``). The primary key links the metadata in the csv with the folder names containing the ascii files

3. The function first reads the csv and generates an array (``temperatures = np.array(temperatures, dtype=object)``). This makes it easier to filter them while linking them with the ascii files. 

4. The ascii files are ready one by one and linked to the appropriate metadata contained in the ``temperatures`` array, i.e., through ``filter_staff = temperatures[(temperatures[:,0]==observation_date) & (temperatures[:,1] == staff_number.staff_number)]``.


Dependencies
------------

The dependencies are provided below and generally sits above the above function:

.. code-block:: python

	def IsNumber(value):
	    "Checks if string is a number"
	    try:
	        float(value)
	        check = True
	    except:
	        check = False
	    return(check)

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
	    
	def calculate_length(data, cf, alpha, t_0, t, oset):
	    from math import sqrt
	    data_table = []
	    # if data is array:
	    for i in range(len(data)-1):
	        pini, obsi, nmeasi, stdi= data[i] 
	        pinj, obsj, nmeasj, stdj = data[i+1]
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
	def rawdata_to_table(dataset, T1, T2, staff_atrs): # cf, alpha, T_o):
	    dCorrectionFactor = staff_atrs['dCorrectionFactor']
	    dThermalCoefficient = staff_atrs['dThermalCoefficient']
	    dStdTemperature = staff_atrs['dStdTemperature']
	    rawReportTable = []

	    for key, value in dataset.items():
	        if key.startswith("Set1"):
	            obs_set = 1
	            #print(value.values)
	            set1 = calculate_length(value.values, dCorrectionFactor, dThermalCoefficient, dStdTemperature, T1, obs_set)
	        elif key.startswith("Set2"):
	            obs_set = 2
	            #print(value)
	            set2 = calculate_length(value.values, dCorrectionFactor, dThermalCoefficient, dStdTemperature, T2, obs_set)
	    # rawReportTable  = pd.DataFrame(rawReportTable, columns=['SET','PIN','TEMPERATURE','FROM','TO', 'STD_DEVIATION', 'MEASURED', 'CORRECTED'])
	    rawReportTable = {'headers': ['SET','PIN','TEMPERATURE','FROM','TO', 'STD_DEVIATION', 'MEASURED', 'CORRECTED'], 'data': set1+set2}
	    return rawReportTable# .to_dict()

	# Unique list
	def unique_list(dataset):
	    ulist = []
	    for d in dataset:
	        if d[1] in ulist:
	            pass
	        else:
	            ulist.append(d[1])
	    return ulist

	# adjust
	def adjustment(dataset, uniquelist):
	    from math import sqrt
	    dataset = np.array(dataset)
	    # output
	    output_adj = []
	    output_hdiff = []
	    for i in range(len(uniquelist)):
	        x = uniquelist[i]
	        if x in dataset[:,1]:
	            dato = dataset[dataset[:,1]==x].tolist()
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
	            elif len(dato) > 1:
	                interval = dato[0][1]
	                dato = np.array(dato, dtype=object)
	                # Perform Least squares - Refer to J.Klinge & B. Hugessen document on Calibration of Barcode staffs
	                W = dato[:,-2].astype(np.float); P = np.diag(1/(dato[:,-1].astype(np.float))**2); A = np.ones(len(W))
	                adjusted_hdiff = (np.matmul(np.transpose(A), np.matmul(P, W)))/(np.matmul(np.transpose(A), np.matmul(P, A)))
	                residual = np.array(adjusted_hdiff  - W, dtype=float)
	                obs_std_dev = np.sqrt(1./np.sqrt(np.diag(P).astype(float))**2)
	                stdev_residual = np.sqrt(1./np.sqrt(np.diag(P).astype(float))**2 - 1./sqrt(np.matmul(np.transpose(A), np.matmul(P, A)))**2)
	                uncertainty = (sqrt(1/np.matmul(np.transpose(A), np.matmul(P, A)))*1000*1.96)
	                std_residual = np.round_(residual/stdev_residual,1)
	                for j in range(len(W)):
	                    output_adj.append([interval, '{:.5f}'.format(adjusted_hdiff), '{:.5f}'.format(W[j]), '{:.5f}'.format(residual[j]),
	                                 '{:.2f}'.format(obs_std_dev[j]*1000), '{:.2f}'.format(stdev_residual[j]*1000), 
	                                 '{:.1f}'.format(std_residual[j])])
	                output_hdiff.append([interval, '{:.5f}'.format(adjusted_hdiff), '{:.2f}'.format(uncertainty), len(dato)])
	    return output_hdiff, output_adj

``reverse_func()``
------------------

The reverse function here simply deletes all range data uploaded in the database:

.. code-block:: python

	def reverse_func(apps, schema_editor):
	    Calibration_Update = apps.get_model("range_calibration", "Calibration_Update")
	    RawDataModel = apps.get_model("range_calibration", "RawDataModel")
	    AdjustedDataModel = apps.get_model("range_calibration", "AdjustedDataModel")
	    HeightDifferenceModel = apps.get_model("range_calibration", "HeightDifferenceModel")
	    RangeParameters = apps.get_model("range_calibration", "RangeParameters")
		
	    Calibration_Update.objects.all().delete()
	    RawDataModel.objects.all().delete()
	    AdjustedDataModel.objects.all().delete()
	    HeightDifferenceModel.objects.all().delete()
	    RangeParameters.objects.all().delete()

migrate
-------

Once everything is complete and the class ``Migration`` has all the elements to run the function ``RunPython``, it is now time to migrate them. This is again done in the command prompts by running the ``migrate`` command:

.. parsed-literal::

	python manage.py migrate

It can take some time to understand the migration errors and try to fix them in order them to run it successfully.

Once the migration is successfull, you will see that all the tables in the **range_calibration** app will be updated. 