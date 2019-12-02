import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_KEY = 'tsmrtg7p81iz@j*$5quy4ek*ap*l*4^kxjingc)up2gu2e0zy1'

DEBUG = True

ALLOWED_HOSTS = ["*", ]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',


    'crispy_forms',
    'widget_tweaks',

    'cms_admin',
    'portal',
    'accounts',
    'parties',
    'materials',
    'challans',
    'payments',
    'rates',
    'bank_accounts',
    'payment_parties',

    'loadings',
    'stocks',
    'dealers',

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

ROOT_URLCONF = 'u_scale.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'u_scale.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = False

USE_TZ = True

DATE_INPUT_FORMATS = [
    "%d/%m/%Y"
]

STATIC_URL = '/static/'


#   CUSTOM SETTINGS
from django.urls import reverse_lazy

CRISPY_TEMPLATE_PACK = "bootstrap4"

SITE_DOMAIN = "127.0.0.1:8000"

BRANCH_ID = "DP"
BRANCH_NAME = "Dapodi"
ACTR_NO_PREFIX = BRANCH_ID + "P"
PARTY_CODE_PREFIX = BRANCH_ID + "PR"
CHALLAN_NO_PREFIX = BRANCH_ID + "CH"

LOGIN_URL = reverse_lazy("accounts:login")
LOGIN_REDIRECT_URL = reverse_lazy("portal:home")

SITE_ID = 1