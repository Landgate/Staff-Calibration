from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from range_calibration.models import RangeParameters
import numpy as np
def homepage(request):
    # Get data
    isChart = False
    param = RangeParameters.objects.all()
    if param.exists():
        param = param.values_list('pin','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')
        # Figure
        labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        param = np.array(param)[:,1:].astype(float)
        tmp = np.nansum(param, axis=0)
    
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
        context = {'labels': labels,
                   'data': data,
                   'isChart': isChart}
        return render(request, 'home_page.html', context)
    else:
        return render(request, 'home_page.html')
