from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib import messages
# from django.views import generic
from .models import (
    Staff,
    StaffType,
    DigitalLevel,
    #Surveyors
    )
from .forms import (
    StaffTypeForm,
    StaffForm,
    StaffUpdateForm,
    DigitalLevelForm,
    DigitalLevelUpdateForm,
    #SurveyorsForm,
    )
from range_calibration.models import Calibration_Update
from staff_calibration.models import uCalibrationUpdate

# Create your views here.
def index(request):
    # return HttpResponse('homepage');
    return render(request, 'home_page.html')

@login_required(login_url="/accounts/login")
def staff_list(request):
    user = request.user
    if user.is_staff:
        staff_list = Staff.objects.all().order_by('user__authority', '-calibration_date')
    else:
        staff_list = Staff.objects.filter(user__authority = user.authority).order_by('-calibration_date')

    context = {
        'staff_lists': staff_list
        }
    return render(request, 'staffs/staff_list.html', context)

@login_required(login_url="/accounts/login")   
def staff_detail(request, id):
    staff = Staff.objects.get(id=id)
    context = {
        'staff': staff
        }
    return render(request, 'staffs/staff_detail.html', context)

@login_required(login_url="/accounts/login")
def staff_create(request):
    form = StaffForm(request.POST or None)
    if form.is_valid():
        this_staff = form.save(commit=False)
        this_staff.user = request.user
        this_staff.save()
        if 'next' in request.POST:
            return redirect(request.POST.get('next'))
        else:
            return redirect ('/staffs')
    context = {
        'form': form
        }
    return render(request, 'staffs/staff_create.html', context)

@login_required(login_url="/accounts/login")
def staff_update(request, id):
    staff = get_object_or_404(Staff, id=id)
    form = StaffUpdateForm(request.POST or None, user=request.user,instance = staff)
    if form.is_valid():
        form.save()
        return redirect ('staffs:staff-list')
    context = {
        'form': form,
        'staff_id': staff.id,
        }
    return render(request, 'staffs/staff_update.html', context)


def staff_delete(request, id):
    try:
        staff = Staff.objects.get(user=request.user, id=id)
        if staff:
            print(staff.user)
            if (Calibration_Update.objects.filter(staff_number__staff_number = staff.staff_number).count()>0) or \
            (uCalibrationUpdate.objects.filter(staff_number__staff_number = staff.staff_number).count()>0):
                messages.warning(request, "Staff number "+ staff.staff_number+" cannot be deleted! But you can update them.")
            else:
                staff.delete()
                messages.success(request, "Successfully deleted staff: "+ staff.staff_number)
            return redirect('staffs:staff-list')
        else:
            messages.error(request, "This action cannot be performed!")
            return redirect('staffs:staff-list')
    except:
        messages.error(request, "This action cannot be performed! This staff does not belong to you.")
        return redirect('staffs:staff-list')

################################################################################
@login_required(login_url="/accounts/login")
def stafftype_create(request):
    form = StaffTypeForm(request.POST or None)
    if form.is_valid():
        form.save()
        if 'next' in request.POST:
            return redirect(request.POST.get('next'))
        else:
            return redirect ('staffs:stafftype-list')
    context = {
        'form': form
        }
    return render(request, 'staffs/stafftype_create.html', context)

@login_required(login_url="/accounts/login")
def stafftype_list(request):
    stafftype_list = StaffType.objects.all()

    context = {
        'stafftype_lists': stafftype_list
        }
    return render(request, 'staffs/stafftype_list.html', context)

@login_required(login_url="/accounts/login")
def stafftype_detail(request, id):
    stafftype = StaffType.objects.get(id = id)
    context = {
        'stafftype': stafftype
        }
    return render(request, 'staffs/stafftype_detail.html', context)

@login_required(login_url="/accounts/login")
def stafftype_update(request, id):
    stafftype = StaffType.objects.get(id=id)
    form = StaffTypeForm(request.POST or None, instance = stafftype)
    if form.is_valid():
        form.save()
        return redirect ('staffs:stafftype-list')
    context = {
        'form': form
        }
    return render(request, 'staffs/stafftype_update.html', context)

@staff_member_required
def stafftype_delete(request, id):
    try:
        stafftype = StaffType.objects.get(id=id)
        stafftype.delete()
        return redirect('staffs:stafftype-list')
    except ObjectDoesNotExist:
        return redirect('/staffs')
###############################################################################
@login_required(login_url="/accounts/login")
def level_list(request):
    user = request.user
    if user.is_staff:
        level_list = DigitalLevel.objects.all()
    else:
        level_list = DigitalLevel.objects.filter(user__authority = user.authority).order_by('level_number')[:10]
    context = {
        'level_lists': level_list
        }
    return render(request, 'staffs/level_list.html', context)

@login_required(login_url="/accounts/login")    
def level_detail(request, id):
    level = DigitalLevel.objects.get(id=id)
    context = {
        'level': level
        }
    return render(request, 'staffs/level_detail.html', context)

@login_required(login_url="/accounts/login")
def level_create(request):
    form = DigitalLevelForm(request.POST or None)
    if form.is_valid():
        this_level = form.save(commit=False)
        this_level.user = request.user
        this_level.save()
        if 'next' in request.POST:
            return redirect(request.POST.get('next'))
        else:
            return redirect ('staffs:level-list')

    return render(request, 'staffs/level_create.html', {'form': form})

@login_required(login_url="/accounts/login")
def level_update(request, id):
    level = get_object_or_404(DigitalLevel, id=id)
    form = DigitalLevelUpdateForm(request.POST or None, user=request.user, instance = level)
    if form.is_valid():
        form.save()
        return redirect ('staffs:level-list')
    context = {
        'form': form,
        'level_id': level.id
        }
    return render(request, 'staffs/level_update.html', context)

@login_required(login_url="/accounts/login")
def level_delete(request, id):
    try:
        level = DigitalLevel.objects.get(user=request.user, id=id)
        if level: 
            if (Calibration_Update.objects.filter(level_number__level_number= level.level_number).count()>0) or \
            (uCalibrationUpdate.objects.filter(level_number__level_number=level.level_number).count()>0):
                messages.warning(request, "Level number "+ level.level_number+" cannot be deleted!")
            else:
                level.delete()
                messages.success(request, "Successfully deleted level: "+ level.level_number+"("+level.level_make+")")
            return redirect('staffs:level-list')
        else:
            messages.error(request, "This action cannot be performed!")
            return redirect('staffs:level-list')
    except:
        messages.error(request, "This action cannot be performed! This staff does not belong to you.")
        return redirect('staffs:level-list')
###############################################################################
# def surveyor_list(request):
#     surveyor_list = Surveyors.objects.all()
#     context = {
#         'surveyor_lists': surveyor_list
#         }
#     return render(request, 'staffs/surveyor_list.html', context)

# def surveyor_detail(request, id):
#     surveyor = Surveyors.objects.get(id=id)
#     context = {
#         'surveyor': surveyor
#         }
#     return render(request, 'staffs/surveyor_detail.html', context)

# def surveyor_create(request):
#     form = SurveyorsForm(request.POST or None)
#     if form.is_valid():
#         form.save()
#         if 'next' in request.POST:
#             return redirect(request.POST.get('next'))
#         else:
#             return redirect ('staffs:surveyors')
#     context = {
#         'form': form
#         }
#     return render(request, 'staffs/surveyor_create.html', context)

# def surveyor_update(request, id):
#     surveyor = Surveyors.objects.get(id=id)
#     form = SurveyorsForm(request.POST or None, instance = surveyor)
#     if form.is_valid():
#         form.save()
#         return redirect ('staffs:surveyors')
#     context = {
#         'form': form
#         }
#     return render(request, 'staffs/surveyor_update.html', context)

# def surveyor_delete(request, id):
#     surveyor = Surveyors.objects.get(id=id)
#     surveyor.delete()
#     return redirect('staffs:surveyors')
# ###############################################################################
