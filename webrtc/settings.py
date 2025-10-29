import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

IS_RENDER = os.environ.get('RENDER', 'False') == 'True'

if IS_RENDER:
    # === PRODUCTION (RENDER) ===
    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    
    # Khởi tạo với domain cứng trước
    ALLOWED_HOSTS = [
        '127.0.0.1', 
        'localhost',
        'streemly.onrender.com',
        '.onrender.com',
    ]
    
    CSRF_TRUSTED_ORIGINS = [
        'https://streemly.onrender.com',  # ← Thêm cứng
    ]

    # Vẫn đọc từ biến môi trường nếu có
    trusted_origins_env = os.environ.get('CSRF_TRUSTED_ORIGINS')
    if trusted_origins_env:
        origins = trusted_origins_env.split(',')
        CSRF_TRUSTED_ORIGINS.extend(origins)
        
        for origin in origins:
            hostname = origin.replace('https://', '').replace('http://', '').split('/')[0]
            if hostname not in ALLOWED_HOSTS:
                ALLOWED_HOSTS.append(hostname)

    # Đọc RENDER_EXTERNAL_URL
    RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')
    if RENDER_EXTERNAL_URL:
        hostname = RENDER_EXTERNAL_URL.replace('https://', '').replace('http://', '').split('/')[0]
        if hostname not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(hostname)
        if RENDER_EXTERNAL_URL not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(RENDER_EXTERNAL_URL)

    # Database
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }

    # Channel Layers
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
            },
        },
    }
    
    # Static files
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

else:
    # === DEVELOPMENT (LOCAL) ===
    SECRET_KEY = 'django-insecure-local-key-cho-development'
    DEBUG = True
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
    CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }
    
    STATIC_ROOT = BASE_DIR / 'staticfiles'

# === COMMON SETTINGS ===

INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'streaming',
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
]

ROOT_URLCONF = 'webrtc.urls'

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

ASGI_APPLICATION = 'webrtc.asgi.application'

AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_DIRS = [
    BASE_DIR / "streaming/static",
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'login_redirect' 
LOGOUT_REDIRECT_URL = 'welcome'