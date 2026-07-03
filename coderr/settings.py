"""
Django settings for the coderr project.

This module contains all the configuration variables and settings for the 
Django application, including database connections, installed applications, 
middleware configuration, and security settings.

For more information on this file, see:
https://docs.djangoproject.com/en/6.0/topics/settings/

For the full list of settings and their values, see:
https://docs.djangoproject.com/en/6.0/ref/settings/
"""

from pathlib import Path

# ==========================================
# Core Project Paths
# ==========================================
# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR dynamically determines the absolute path to the project root directory.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================
# Security & Development Settings
# ==========================================
# Quick-start development settings - unsuitable for production.
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# This key is used for cryptographic signing. It must never be exposed publicly.
SECRET_KEY = 'django-insecure-u-br-c=j)11grmeq7onfyah#*t_u!h+qr&vjohia8*oi+$k!)4'

# SECURITY WARNING: don't run with debug turned on in production!
# Set to False in production to prevent leaking sensitive stack traces to users.
DEBUG = True

# Defines the host/domain names that this Django site can serve.
# Must be populated with domain names in production (e.g., ['example.com']).
ALLOWED_HOSTS = []


# ==========================================
# Application Definition
# ==========================================
INSTALLED_APPS = [
    # Core Django Applications
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-Party Applications
    'rest_framework',            # Django REST framework for building the API
    'rest_framework.authtoken',  # Token-based authentication for DRF
    'corsheaders',               # Handles Cross-Origin Resource Sharing (CORS)
    
    # Local Applications
    'core',                      # WICHTIG: Hier wurde 'api' zu 'core' geändert!
]

# Middleware components are hooks into Django's request/response processing.
# Note: Order is critical here. CorsMiddleware should be placed as high as possible.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Points Django to the root URL configuration module.
# WICHTIG: Hier wurde 'config.urls' zu 'coderr.urls' geändert!
ROOT_URLCONF = 'coderr.urls'

# Configuration for Django's template rendering engine.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# The Python path to the WSGI application object that Django's built-in servers will use.
# WICHTIG: Hier wurde 'config.wsgi.application' zu 'coderr.wsgi.application' geändert!
WSGI_APPLICATION = 'coderr.wsgi.application'


# ==========================================
# Database Configuration
# ==========================================
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ==========================================
# Password Validation
# ==========================================
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==========================================
# Internationalization & Localization
# ==========================================
# https://docs.djangoproject.com/en/6.0/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# ==========================================
# Static Files (CSS, JavaScript, Images)
# ==========================================
# https://docs.djangoproject.com/en/6.0/howto/static-files/
STATIC_URL = 'static/'


# ==========================================
# Custom Configuration & Third-Party Settings
# ==========================================

# CORS (Cross-Origin Resource Sharing) Settings
# SECURITY WARNING: Setting this to True allows any origin to make requests to the API.
# In a strict production environment, replace this with CORS_ALLOWED_ORIGINS and specify domains.
CORS_ALLOW_ALL_ORIGINS = True

# Django REST Framework Settings
REST_FRAMEWORK = {
    # Defines the default authentication methods used to identify users requesting API endpoints.
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',    # Used for API clients (like Angular/Postman)
        'rest_framework.authentication.SessionAuthentication',  # Used for the browsable API and Django Admin
    ],
}