Customise User Forms and Admin Views
====================================

Overview
--------

The new **CustomUser** model has been set up but Django still does not know how to use it. This is because Django uses the default authentication (*auth*) form that will accept only the default Django **User** model. In order to tell Django to use the **CustomUser** model, we will have to modify the default authentication form by subclassing the ``UserCreationForm`` and ``UserChangeForm``. 

After that we will need to tell Django **admin** to use the customised form and model so that admin have the appropriate form views and user model. 

Customise the Form
------------------

Let's subclass the ``UserCreationForm`` and ``UserChangeForm`` forms so that Django can now use the new **CustomUser** model. 

Create a new file in *accounts* directory called **forms.py** and copy the following lines:
	
.. code-block:: python

	#filename: staff/accounts/forms.py

	from django import forms
	from django.core.exceptions import ObjectDoesNotExist
	from django.contrib.auth.forms import UserCreationForm, UserChangeForm
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

Note that several methods have been put in place to indicate how the input texts are interpreted and raise *Validation* errors. Custom validations include:

1. Preserving the unique email address by enquring the **CustomUser** model

2. Checking if the two passwords match

3. The **CustomUserChangeForm** uses a ``ReadOnlyPasswordHashField`` which tells Django not to store the raw passwords.

Please refer to https://docs.djangoproject.com/en/3.1/topics/auth/customizing/ for more information about customising the authentication form.

Customise the Admin
-------------------

Now, we need to tell Django to use the above forms by subclassing ``UserAdmin`` in the **admin.py** in the same directory (**staff/accounts/**). 

Let's open the **admin.py** and register the custom models and Forms like this:

.. code-block: python
	
	#filename: staff/accounts/admin.py

	from django.contrib import admin
	from django.contrib.auth.admin import UserAdmin
	from .forms import CustomUserCreationForm, CustomUserChangeForm         # import forms
	from .models import CustomUser, Authority                               # import models

	# Register the Authority model and modify the list display and ordering
	@admin.register(Authority)
	class AuthorityAdmin(admin.ModelAdmin):
	    list_display = ('authority_name', 'authority_abbrev',)

	    ordering = ('authority_abbrev',)

	# Register the CustomUser model and the associated Forms. Also customise the views 
	class CustomUserAdmin(UserAdmin):
	    add_form = CustomUserCreationForm
	    form = CustomUserChangeForm
	    model = CustomUser
	    list_display = ('email', 'first_name', 'last_name', 'authority', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
	    list_filter = ('email', 'is_staff', 'is_active',)
	    fieldsets = (
	        (None, {'fields': ('email', 'password')}),
	        #('Personal info', {'fields': ('email', 'phone_number',)}),
	        ('Permissions', {'fields': ('is_staff','groups',)}),
	    )
	    add_fieldsets = (
	        (None, {
	            'classes': ('wide',),
	            'fields': (
	                'email', 
	                'first_name',
	                'last_name',
	                'authority',
	                'password1', 
	                'password2',
	                'is_staff', 
	                'is_active')}
	        ),
	    )
	    search_fields = ('email',)
	    ordering = ('email',)


	admin.site.register(CustomUser, CustomUserAdmin)

Thats all the steps required to enable Django to use the email authentication instead of its default username. Note that are many different ways to acheive this and developers are free to adopt any one of them. 

Django admin page
-----------------

Run the sever (``python manage.py runserver``) in the command prompt and log in to the admin site (http://127.0.0.1:8000/admin) using the superuser credentials created through ``python manage.py createsuperuser``. The ``superuser`` us now able to add and change users as before. 

.. figure::  custom_admin_page.png
	   :align:   center

	   Custom admin site showing the fields required to add a new user



