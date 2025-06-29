import os
import stripe # type: ignore
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-hky+k)%#3j+9in+@)k#a&lyn56z$p0zf+j3zj+6e$5pcjasasu'

DEBUG = True

ALLOWED_HOSTS = ["*"]

SITE_URL = os.getenv("SITE_URL")
FORNTEND_SITE_URL = os.getenv("FORNTEND_SITE_URL")

STRIPE_SUCCESS_URL = f"https://finch-development.vercel.app/success"
STRIPE_CANCEL_URL = f"https://finch-development.vercel.app/cancel"

GEOIP_PATH = os.path.join(BASE_DIR, 'geoip')

# Application definition

INSTALLED_APPS = [
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    "unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history",
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',

    'django_extensions',

    'corsheaders',

    'core',
    'product_management',
    'api',
    'pos',
    'setting',

    'django_select2'
]

DATA_UPLOAD_MAX_NUMBER_FIELDS = 80240

AUTH_USER_MODEL = 'core.User'  

LOGIN_URL = 'core:login'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),  # Access token valid for 30 days
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30), # Refresh token valid for 30 days
}

CORS_ALLOW_ALL_ORIGINS = True


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.GeoIPMiddleware',
    
]

ROOT_URLCONF = 'fleet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'setting.context_preprocessor.currency_context',
            ],
            'libraries': {
                'custom_filters': 'core.templatetags.custom_filters',
            },
        },
    },
]

WSGI_APPLICATION = 'fleet.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'fleetdb'),
        'USER': os.getenv('POSTGRES_USER', 'roy77'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'asdf1234@77'),
        'HOST': os.getenv('POSTGRES_HOST', 'db'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SITE_TITLE": "Finch Adminstration",
    "SITE_HEADER": "Finch Adminstration",
    "SITE_URL": "/",
    # "SITE_ICON": lambda request: static("icon.svg"),  # both modes, optimise for 32px height
    # "SITE_ICON": {
    #     "light": lambda request: static("icon-light.svg"),  # light mode
    #     "dark": lambda request: static("icon-dark.svg"),  # dark mode
    # },
    # # "SITE_LOGO": lambda request: static("logo.svg"),  # both modes, optimise for 32px height
    # "SITE_LOGO": {
    #     "light": lambda request: static("logo-light.svg"),  # light mode
    #     "dark": lambda request: static("logo-dark.svg"),  # dark mode
    # },
    "SITE_SYMBOL": "speed",  # symbol from icon set
    # "SITE_FAVICONS": [
    #     {
    #         "rel": "icon",
    #         "sizes": "32x32",
    #         "type": "image/svg+xml",
    #         "href": lambda request: static("favicon.svg"),
    #     },
    # ],
    "SHOW_HISTORY": True, # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": True, # show/hide "View on site" button, default: True
    "SHOW_BACK_BUTTON": False,

    "SITE_DROPDOWN": [
        {
            "icon": "store",
            "title": _("Ecommerce Site"),
            "link": "https://example.com",
        },
        {
            "icon": "point_of_sale",
            "title": _("POS Site"),
            "link": "https://example.com",
        },
    ],

    "SIDEBAR": {
    "show_search": True,  # Search in applications and models names
    "show_all_applications": False,  # Dropdown with all applications and models
    "DASHBOARD_CALLBACK": "core.admin.dashboard_callback",
    "navigation": [
        {
            "title": _("Authentication & Authorization"),
            "separator": True, 
            "collapsible": True, 
            "items": [
                {
                    "title": _("Groups"),
                    "icon": "people", 
                    "link": "/admin/auth/group/",
                },
                {
                    "title": _("Users"),
                    "icon": "person",
                    "link": "/admin/core/user/",
                },
            ],
        },
        {
            "title": _("General Management"),
            "separator": True,  
            "collapsible": True,  
            "items": [
                {
                    "title": _("Dashboard"),
                    "icon": "dashboard", 
                    "link": reverse_lazy("admin:index"),
                    "permission": lambda request: request.user.is_superuser,
                },
                {
                    "title": _("Coupons"),
                    "icon": "tag",
                    "link": "/admin/core/cupon/",
                },
                {
                    "title": _("Menu Item"),
                    "icon": "menu",
                    "link": "/admin/core/menuitem/",
                },
                {
                    "title": _("Orders"),
                    "icon": "shopping_cart",
                    "badge": "core.admin.order_badge_callback",
                    "link": "/admin/core/order/",
                },
                {
                    "title": _("Visitor Sessions"),
                    "icon": "access_time",
                    "link": "/admin/core/visitorsession/",
                },
            ],
        },
        {
            "title": _("Product Management"),
            "separator": True,  
            "collapsible": True,  
            "items": [
                {
                    "title": _("Categories"),
                    "icon": "category",
                    "link": "/admin/core/category",
                },
                {
                    "title": _("Tags"),
                    "icon": "label",
                    "link": "/admin/core/tag",
                },
                {
                    "title": _("Colors"),
                    "icon": "palette",
                    "link": "/admin/core/color",
                },
                {
                    "title": _("Sizes"),
                    "icon": "resize",
                    "link": "/admin/core/size",
                },
                {
                    "title": _("Products"),
                    "icon": "store",
                    "link": "/admin/core/product",
                },
                {
                    "title": _("Product Reviews"),
                    "icon": "rate_review",
                    "link": "/admin/core/productreview",
                },
            ],
        },
        {
            "title": _("Point Of Sale"),
            "separator": True,  
            "collapsible": True,  
            "items": [
                {
                    "title": _("POS Sales"),
                    "icon": "point_of_sale",
                    "link": "/admin/pos/pos/",
                },
                # {
                #     "title": _("POS Items"),
                #     "icon": "inventory_2",
                #     "link": "/admin/pos_items",
                # },
            ],
        },
        {
            "title": _("Setting Management"),
            "separator": True,  
            "collapsible": True,  
            "items": [
                {
                    "title": _("Company Settings"),
                    "icon": "business",
                    "link": "/admin/setting/companysetting/",
                },
            ],
        },
    ],
}


}

def badge_callback(request):
    return 3
