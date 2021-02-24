
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import password_validation
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import CustomUser, Authority

class NonstickyTextInput(forms.TextInput):
    '''Input widget for preserving the form errors but forgets the submitted fields'''
    def get_context(self, name, value, attrs):
        value = None  # Clear the submitted value.
        return super().get_context(name, value, attrs)

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(widget=NonstickyTextInput())
    first_name = forms.CharField(widget=NonstickyTextInput())
    last_name = forms.CharField(widget=NonstickyTextInput())
    #phone_number = forms.CharField(widget=NonstickyTextInput())
    password1 = forms.CharField(label='Password', 
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', 
                                widget=forms.PasswordInput)

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'authority', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        try:
            email_qs = CustomUser.objects.get(email=email)
            if email_qs.is_active:
                raise forms.ValidationError("User already exists. Please use a different email address to sign up.")
            elif not email_qs.is_active:
                raise forms.ValidationError("Your account is not active yet. Please log in to request a new activation code.")
        except ObjectDoesNotExist:
            pass
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        password_validation.validate_password(self.cleaned_data.get('password1'), None)
        return password2

    # def clean_phone_number(self):
    #     phone_number = self.cleaned_data.get("phone_number")
    #     if not phone_number.isdigit() or not len(phone_number)==10:
    #         raise forms.ValidationError("Please enter a valid 10 digit phone number, e.g., 0411110000")
    #     return phone_number

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name").title()
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name").title()
        return last_name

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = (
            'email', 
            'password',
            'first_name', 
            'last_name', 
            'authority',
            'is_staff',
            'is_superuser',
            'is_active',
            'date_joined')

    def clean_password(self):
        return self.initial["password"]


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=NonstickyTextInput())
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        )

    def clean(self):
        user = self.authenticate_via_email()
        if not user:
            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        else:
            self.user = user
        return self.cleaned_data

    def authenticate_via_email(self):
        """
            Authenticate user using email.
            Returns user object if authenticated else None
        """
        email = self.cleaned_data.get('email').lower()
        if email:
            try:
                user = CustomUser.objects.get(email__iexact=email)
                if user.check_password(self.cleaned_data['password']):
                    return user
                else:
                    raise forms.ValidationError('Login failed! Incorrect email and/or password given')
            except ObjectDoesNotExist:
                pass
                # return forms.ValidationError('Login failed! Enter you email and/or password correctly')
        return None

class AuthorityForm(forms.Form):
    authority_name = forms.CharField(max_length=200)
    authority_abbrev = forms.CharField(max_length=10)

    def clean_authority_abbrev(self):
        authority_abbrev = self.cleaned_data['authority_abbrev'].upper()
        return authority_abbrev

class ProfileForm(forms.ModelForm):
    authority = forms.ModelChoiceField(queryset=Authority.objects.all(), widget=forms.Select(attrs={"onChange":'admSelectCheck(this)'}))

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'authority']


        widgets = {
            'email': forms.TextInput(attrs={'placeholder':'Enter email address'}),
            'first_name': forms.TextInput(attrs={'placeholder':'Enter first name'}),
            'last_name': forms.TextInput(attrs={'placeholder':'Enter last name'}),
            
        }




