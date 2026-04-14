from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-rg8&%a#48=1779rsju9mzpu(b-f8evdzgzbk%8909@h1^n6u0d'
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# =====================================================
# APLICACIONES INSTALADAS
# =====================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',    
    'django.contrib.humanize',

    'rest_framework',
    "corsheaders",

    'geografia',
    'alumnos',
    'carreras',
    'valores',
    'ctacte',

    'usuarios',
    'mensajes',
    'reportes',
]

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
ROOT_URLCONF = 'backend.urls'

# =====================================================
# TEMPLATES
# =====================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'backend.wsgi.application'

# =====================================================
# BASE DE DATOS (MySQL)
# =====================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sigecodb',
        'USER': 'backend_user',
        'PASSWORD': '34745',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

# =====================================================
# REST FRAMEWORK / JWT
# =====================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # CAMBIO: AllowAny → IsAuthenticated
    # Todas las vistas de la API requieren token JWT válido.
    # Las vistas públicas (login) usan @csrf_exempt sin pasar por DRF.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}


 
SIMPLE_JWT = {
    # El access token dura 8 horas (una jornada laboral)
    'ACCESS_TOKEN_LIFETIME':  timedelta(hours=8),
    # El refresh token dura 7 días
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    # Permite renovar el refresh token en cada uso
    'ROTATE_REFRESH_TOKENS':  True,
    # Invalida el refresh anterior al rotar
    'BLACKLIST_AFTER_ROTATION': False,
    # Campos extra que se incluyen en el payload del token
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'usuario_id',
}
 

# =====================================================
# CORS
# =====================================================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]
CORS_ALLOW_CREDENTIALS = True

# =====================================================
# INTERNACIONALIZACIÓN
# =====================================================
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# =====================================================
# ARCHIVOS ESTÁTICOS
# =====================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "frontend" / "shared",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True

# Configuración de correo real
# Configuración de correo real usando Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'           # servidor SMTP de Gmail
EMAIL_PORT = 587                        # puerto TLS
EMAIL_USE_TLS = True                     # habilitar TLS
EMAIL_HOST_USER = 'toledoagus421@gmail.com'   # tu correo de Gmail
EMAIL_HOST_PASSWORD = 'Quebrachocolorado1628'  # contraseña de Gmail o App Password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
