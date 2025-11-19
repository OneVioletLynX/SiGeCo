from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-(#iu=-*y4nendy35hp(36@4f_%cjtxq7w!bn4%oaomsbnx)zn&'

DEBUG = True

ALLOWED_HOSTS = []

# ==========================
# APLICACIONES INSTALADAS
# ==========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'alumnos',
    'usuarios',
    'carreras',
    'shared'
]

# ==========================
# MIDDLEWARE
# ==========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # debe ir arriba del common
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'frontend.urls'

# ==========================
# TEMPLATES
# ==========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'shared' / 'templates',  # base.html
        ],
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

# ==========================
# BASE DE DATOS (solo si lo necesitás aquí)
# ==========================
# Si el frontend no maneja datos, no es necesario tener DB.
# Si querés mantener una (por ejemplo para sesiones o usuarios):
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ==========================
# ARCHIVOS ESTÁTICOS
# ==========================
WSGI_APPLICATION = 'frontend.wsgi.application'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'shared' / 'static',  
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ==========================
# CORS
# ==========================
CORS_ALLOW_ALL_ORIGINS = True  # solo para desarrollo

# ==========================
# LOCALIZACIÓN
# ==========================
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
