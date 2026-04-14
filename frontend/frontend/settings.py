from pathlib import Path
import sys
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR        = Path(__file__).resolve().parent.parent
SIGECO_ROOT_DIR = BASE_DIR.parent

if str(SIGECO_ROOT_DIR) not in sys.path:
    sys.path.append(str(SIGECO_ROOT_DIR))

# =====================================================
# SEGURIDAD
# =====================================================
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG       = os.environ.get('DEBUG', 'False') == 'True'

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
    'corsheaders',

    'cobros_front',
    'alumnos_front',
    'carreras_front',
    'usuarios_front',
    'mensajes_front',

    'backend.ctacte',
    'backend.alumnos',
    'backend.carreras',
    'backend.usuarios',
    'backend.reportes',
    'backend.valores',
    'backend.geografia',
]

# =====================================================
# MIDDLEWARE — incluye protección de rutas por token
# =====================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'frontend.middleware.TokenCookieMiddleware',  # protección server-side
]

ROOT_URLCONF = 'frontend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'shared' / 'templates'],
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

WSGI_APPLICATION = 'frontend.wsgi.application'

# =====================================================
# BASE DE DATOS
# =====================================================
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     os.environ.get('DB_NAME',     'SiGeCoDB'),
        'USER':     os.environ.get('DB_USER',     'backend_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST':     os.environ.get('DB_HOST',     '127.0.0.1'),
        'PORT':     os.environ.get('DB_PORT',     '3306'),
        'OPTIONS':  {'charset': 'utf8mb4'},
    }
}

# =====================================================
# ARCHIVOS ESTÁTICOS
# =====================================================
STATIC_URL  = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'shared' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# =====================================================
# CORS — solo acepta requests internos
# =====================================================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True

# =====================================================
# LOCALIZACIÓN
# =====================================================
LANGUAGE_CODE = 'es-ar'
TIME_ZONE     = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ   = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'