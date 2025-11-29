"""
Django settings for Agentic RAG project.
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-in-production-123456789')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'daphne',  # Must be first for ASGI
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',  # For PostgreSQL extensions
    
    # Third-party apps
    'channels',
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    
    # Local apps
    'apps.rag',
    'apps.chat',
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

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Channels Configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(config('REDIS_HOST', default='redis'), config('REDIS_PORT', default=6379, cast=int))],
        },
    },
}

# Database with PostgreSQL and pgvector
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='agentic_rag'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]
CORS_ALLOW_CREDENTIALS = True

# CSRF settings for WebSocket
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "ws://localhost:8000",
]

# Spectacular settings for API documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'Agentic RAG API',
    'DESCRIPTION': 'Retrieval Augmented Generation with Agents',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# LLM and Embedding settings
LLM_CONFIG = {
    'DEFAULT_PROVIDER': config('DEFAULT_LLM_PROVIDER', default='openai'),
    'OPENAI_API_KEY': config('OPENAI_API_KEY', default=''),
    'GROQ_API_KEY': config('GROQ_API_KEY', default=''),
    'AGENT_MODEL': config('AGENT_MODEL', default='gpt-4-turbo-preview'),
}

EMBEDDING_CONFIG = {
    'DEFAULT_PROVIDER': config('DEFAULT_EMBEDDING_PROVIDER', default='openai'),
    'EMBEDDING_MODEL': config('EMBEDDING_MODEL', default='text-embedding-3-small'),
    'EMBEDDING_DIMENSION': config('EMBEDDING_DIMENSION', default=1536, cast=int),
}

# Agent settings
AGENT_CONFIG = {
    'MAX_STEPS': config('MAX_AGENT_STEPS', default=5, cast=int),
}

# Qdrant settings
QDRANT_CONFIG = {
    'HOST': config('QDRANT_HOST', default='qdrant'),
    'PORT': config('QDRANT_PORT', default=6333, cast=int),
}
