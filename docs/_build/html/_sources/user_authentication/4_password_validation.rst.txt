Password Validators
===================

Overview
--------

Users often choose poor passwords. To help mitigate this problem, Django offers pluggable password validation functions, which can be configured to provide multiple password validators at the same time. A few validators are included in Django, but we can create custom validations as well. For this Staff Calibration project, we will use the default password validator and also create some custom validators for users to strengthen their choice of passwords. 

Note from Django - *Password validation can prevent the use of many types of weak passwords. However, the fact that a password passes all the validators doesn’t guarantee that it is a strong password. There are many factors that can weaken a password that are not detectable by even the most advanced password validators.*

Each password validator must provide a help text to explain the requirements to the user, validate a given password and return an error message if it does not meet the requirements. Validators can also have optional settings to fine tune their behavior.

Settings
--------

Validation is controlled by the ``AUTH_PASSWORD_VALIDATORS`` setting in the **settings.py**. The default for the setting is an empty list, which means no validators are applied. 

.. code-block:: python

	# Password validation
	AUTH_PASSWORD_VALIDATORS = [
		...
	]

As this project uses a custom model, Form, and a authentication system, no password validations will be applied by default and we have to define it. Let's add four validators that are commonly used and provided by Django in the empty list above:

	.. code-block:: python

		#filename: staff/staff/settings.py

		...

		AUTH_PASSWORD_VALIDATORS = [
		    {
		        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
		    },
		    {
		        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
		        'OPTIONS': {
		            'min_length': 8,
		        }
		    },
		    {
		        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
		    },
		    {
		        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
		    },
		]

The above validators will raise errors if:

* the password is too similar to the username or email
* the length of password word is less than 8 characters
* the password is too common 
* the password contains only numbers

Customising password validation
-------------------------------

Just to be on the safer side, we would also like users to have at least one uppercase, one lowercase letter, and one digit in their password. To enable this functionality, we will create a file called **passwordValidators.py** in the project directory (**staff/staff/**) and copy the following procedures- containing a method and a help text for each validator:

.. code-block:: python
	
	#filename: staff/staff/passwordValidators.py

	import re
	from django.core.exceptions import ValidationError
	from django.utils.translation import ugettext as _


	class NumberValidator(object):
	    def __init__(self, min_digits=0):
	        self.min_digits = min_digits

	    def validate(self, password, user=None):
	        if not len(re.findall('\d', password)) >= self.min_digits:
	            raise ValidationError(
	                _("The password must contain at least %(min_digits)d digit(s), 0-9."),
	                code='password_no_number',
	                params={'min_digits': self.min_digits},
	            )

	    def get_help_text(self):
	        return _(
	            "Your password must contain at least %(min_digits)d digit(s), 0-9." % {'min_digits': self.min_digits}
	        )


	class UppercaseValidator(object):
	    def validate(self, password, user=None):
	        if not re.findall('[A-Z]', password):
	            raise ValidationError(
	                _("The password must contain at least 1 uppercase letter, A-Z."),
	                code='password_no_upper',
	            )
	    def get_help_text(self):
	        return _(
	            "Your password must contain at least 1 uppercase letter, A-Z."
	        )


	class LowercaseValidator(object):
	    def validate(self, password, user=None):
	        if not re.findall('[a-z]', password):
	            raise ValidationError(
	                _("The password must contain at least 1 lowercase letter, a-z."),
	                code='password_no_lower',
	            )

	    def get_help_text(self):
	        return _(
	            "Your password must contain at least 1 lowercase letter, a-z."
	        )

And add them to the list of ``AUTH_PASSWORD_VALIDATORS`` in **settings.py**. The path to custom validators are given by ``staff.passwordValidators.ClassName``

.. code-block:: python

	AUTH_PASSWORD_VALIDATORS = [

		... 

		{   'NAME': 'staff.passwordValidators.NumberValidator',
	        'OPTIONS': {
	            'min_digits': 1, 
	            }
	    },
	    {'NAME': 'staff.passwordValidators.UppercaseValidator', },
	    {'NAME': 'staff.passwordValidators.LowercaseValidator', },
	]

That's it. Users will now be able to see error messages (through ``raise ValidationError``) if their passwords do not meet the above requirements. 

.. figure:: Password_validation_error.png
	:align: center

	Sign up form showing upper case requirement error