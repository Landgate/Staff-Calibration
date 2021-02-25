from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token_generator import account_activation_token
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from .forms import CustomUserCreationForm, UserLoginForm, ProfileForm, AuthorityForm
from .models import CustomUser, Authority
# Create your views here.

def activation_sent_view(request):
    return render(request, 'registration/activation_sent.html')

@csrf_exempt
def signup_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('accounts:accounts_home')
    else:
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                user = form.save(commit=False)
                user.is_active=False
                # Populate and save the user authority if Other
                if user.authority.authority_name=="Other":
                    authority_name = request.POST['authority_name']
                    authority_abbrev = request.POST['authority_abbrev']
                    Authority.objects.update_or_create(
                        authority_name=authority_name,
                        authority_abbrev = authority_abbrev
                    )
                    user.authority = Authority.objects.get(authority_name__exact=authority_name)
                # save user
                user.save()
                # Get the group and assign them
                geodesy_group = ['kent.wheeler@landgate.wa.gov.au', 'khandu.k@landgate.wa.gov.au', 'khandu@landgate.wa.gov.au', 
                                'vanessa.ung@landgate.wa.gov.au', 'brendon.hellmund@landgate.wa.gov.au',
                                'tony.castelli@landgate.wa.gov.au', 'ireneusz.baran@landgate.wa.gov.au']
                geodesy = Group.objects.get(name='Geodesy')
                landgate = Group.objects.get(name='Landgate')
                others = Group.objects.get(name='Others')
                if 'landgate.wa.gov.au' in email:
                    user.groups.add(landgate)
                else:
                   user.groups.add(others)
                # More authority to geodesity group
                if email in geodesy_group:
                    user.groups.add(geodesy)
                    user.is_staff = True
                user.save()
                # Prepare to send activation code
                current_site = get_current_site(request)
                email_subject = 'Activate Your Account'
                message = render_to_string('registration/activate_account.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)), #.decode(),
                    'token': account_activation_token.make_token(user),
                })
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(email_subject, message, to=[to_email])
                email.send()
                # return HttpResponse('We have sent you an email, please confirm your email address to complete registration')
                return redirect('accounts:activation_sent')
            
            elif request.user.is_authenticated:
                return redirect('/')
        else:
            form = CustomUserCreationForm() # UserCreationForm()
        return render(request, 'accounts/signup.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # user.backend = 'django.contrib.auth.backends.ModelBackend'  
        # login(request, user)
        messages.success(request, 'Your account has been activated successfully. You can now log in.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'Your activation link appears to be invalid.')
        return redirect('accounts:signup')

# create a function to resolve email to username
def get_user(email):
    try:
        return CustomUser.objects.get(email=email.lower())
    except CustomUser.DoesNotExist:
        return None

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        # authenticate has username instead of email
        if form.is_valid():
            # Authenticate the user
            user = form.authenticate_via_email()
            # user = authenticate(username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if 'next' in request.POST:
                        return redirect(request.POST.get('next'))
                    else:
                        return redirect('staff_calibration:staff-home')
                else:
                    current_site = get_current_site(request)
                    email_subject = 'Please activate your account again.'
                    message = render_to_string('registration/activate_account.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)), #.decode(),
                        'token': account_activation_token.make_token(user),
                    })
                    to_email = form.cleaned_data.get('email')
                    email = EmailMessage(email_subject, message, to=[to_email])
                    email.send()
                    # return HttpResponse('We have sent you an email, please confirm your email address to complete registration')
                    return redirect('accounts:activation_sent')
    elif request.user.is_authenticated:
        return redirect('/')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('accounts:accounts_home')

@staff_member_required
def user_list_view(request):
    user_list = CustomUser.objects.all().exclude(is_superuser=True)
    if user_list.exists():
        context = {
            'user_list': user_list}
        return render(request, 'accounts/user_list_view.html', context=context)
    else:
        messages.warning(request, "You do not have any users at the moment.")
        return render(request, 'accounts/user_list_view.html', context=context)
        # return redirect('/')

@staff_member_required
def user_delete(request, email):
    try:
        this_user = get_object_or_404(CustomUser, email=email)
        this_user.delete()
    except ObjectDoesNotExist:
        messages.warning(request, 'This user cannot be deleted.')
    
    user_list = CustomUser.objects.all().exclude(is_superuser=True)
    if user_list.exists():
        return redirect('accounts:user_list')
    else:
        messages.warning(request, "You do not have any users at the moment.")
        return redirect('/')

@login_required(login_url="/accounts/login")
def user_profile_view(request, id):
    this_user = get_object_or_404(CustomUser, id=id)
    form = ProfileForm(request.POST or None, instance = this_user)
    if form.is_valid():
        form.save()
        return redirect ('/')
    context = {
        'form': form
        }
    return render(request, 'accounts/user_profile.html', context)

@login_required(login_url="/accounts/login")
def user_update_view(request, email):
    print(email)
    this_user = get_object_or_404(CustomUser, email=email)
    form = ProfileForm(request.POST or None, instance = this_user)
    if form.is_valid():
        obj= form.save(commit= False)
        obj.save()
        return redirect ('/')
    context = {
        'form': form
        }
    return render(request, 'accounts/user_profile.html', context)
