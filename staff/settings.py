"""
Django settings for staff project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
import django_heroku
# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = '2hboyc$4ejiv&j-sugkx5w@nrs&esda@*3*wpv&uy%+jp@m(d_'
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG_VALUE') == 'True'
# DEBUG = True

# Set hosts to allow any app on Heroku and the local testing URL
ALLOWED_HOSTS = ['staffcalibration.herokuapp.com','127.0.0.1']

# Set the custom user account
AUTH_USER_MODEL = 'accounts.CustomUser'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mathfilters',
    'formtools',
    'staffs',
    'range_calibration',
    'staff_calibration',
    'accounts',
    'docs',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'csp.middleware.CSPMiddleware',
]

ROOT_URLCONF = 'staff.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'staff.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# Heroku: Update database configuration from $DATABASE_URL.
if 'DATABASE_URL' in os.environ:
    import dj_database_url
    DATABASES = {'default': dj_database_url.config()}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR , 'db.sqlite3'),
        }
    }

#DJANG MESSAGE
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/
DATE_INPUT_FORMATS = ('%d-%m-%Y','%Y-%m-%d')

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Australia/Perth'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'assets'),]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/data/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'data')

#DOCS_URL = '/docs/'
DOCS_ROOT = os.path.join(BASE_DIR, 'docs/_build/html')
DOCS_ACCESS = 'staff'

#SECURITY SETTINGS
#CSRF Protections
#CSRF_COOKIE_SECURE = True
#CSRF_USE_SESSIONS = True

# Delete Sessions
SESSION_COOKIE_SECURE=True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 5*60

# Cross Site Scripting
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Re-direct non HTTPS requests to HTTPS
#SECURE_SSL_REDIRECT = True

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Password validation
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
    
    {   'NAME': 'staff.passwordValidators.NumberValidator',
        'OPTIONS': {
            'min_digits': 1, 
            }
    },
    {'NAME': 'staff.passwordValidators.UppercaseValidator', },
    {'NAME': 'staff.passwordValidators.LowercaseValidator', },
]
# Email settings
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']
                       
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_SSL = False    # use port 465
EMAIL_USE_TLS = True    # use port 587
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")


# redirect url
LOGIN_REDIRECT_URL = '/'


# settings
django_heroku.settings(locals())
