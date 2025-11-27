from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
SIGECO_ROOT_DIR = BASE_DIR.parent

# Asegura que el backend sea importable desde el frontend
if str(SIGECO_ROOT_DIR) not in sys.path:
    sys.path.append(str(SIGECO_ROOT_DIR))

SECRET_KEY = 'django-insecure-(#iu=-*y4nendy35hp(36@4f_%cjtxq7w!bn4%oaomsbnx)zn&'
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# =====================================================
# APLICACIONES INSTALADAS
# =====================================================
INSTALLED_APPS = [
    # Django apps básicas
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceros
    'corsheaders',

    # Apps del frontend (HTML, vistas, templates)
    'cobros_front',
    'alumnos_front',
    'carreras_front',
    'usuarios_front',
    'mensajes_front',
    # Apps del backend (lógica, modelos, API)
    'backend.ctacte',
    'backend.alumnos',
    'backend.carreras',
    'backend.usuarios',
    'backend.reportes',
    'backend.valores',
]


# =====================================================
# MIDDLEWARE
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
]

ROOT_URLCONF = 'frontend.urls'

# =====================================================
# TEMPLATES
# =====================================================
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
# BASE DE DATOS LOCAL (solo para desarrollo)
# =====================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'SiGeCoDB',
        'USER': 'backend_user',
        'PASSWORD': '34745',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

# =====================================================
# ARCHIVOS ESTÁTICOS
# =====================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'shared' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# =====================================================
# CORS
# =====================================================
CORS_ALLOW_ALL_ORIGINS = True  # Solo desarrollo
CORS_ALLOW_CREDENTIALS = True

# =====================================================
# LOCALIZACIÓN
# =====================================================
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
