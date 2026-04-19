import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-su@07qmxsci6$bdyl5g+8i_=yc*(8ofo6!-qty%7ruf5y^@iby'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'laundry_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
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

WSGI_APPLICATION = 'laundry_project.wsgi.application'

# Database (SQL Server)
DATABASES = {
    'default': {
        'ENGINE': 'mssql', 
        'NAME': 'LaundryDB', 
        'USER': 'sa', 
        'PASSWORD': '123456789', 
        'HOST': 'DESKTOP-6445F79\\SQLEXPRESS2019', 
        'PORT': '', 
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server', 
            'extra_params': 'TrustServerCertificate=yes;',
        },
    }
}

# 🔐 ระบบ Password (ปิด Validator เพื่อให้ตั้งรหัส 1234 ได้)
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = 'th-th' # 🚨 ปรับเป็นภาษาไทยหน่อยเพื่อความเท่
TIME_ZONE = 'Asia/Bangkok'
USE_I18N = True
USE_TZ = False

# 📁 Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "core" / "static",]  

# 🔐 ระบบ Login / Logout
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
