import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'your-secret-key' 
DEBUG = True
ALLOWED_HOSTS = ['*'] 

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # Ensure this app is enabled
    'kube', # Your custom Django app
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

ROOT_URLCONF = 'kubeweb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Project-wide templates
        'APP_DIRS': True, # Look for templates in 'templates' subdirectories of apps
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

CSRF_TRUSTED_ORIGINS = [
    "https://my-site.darkube.app",
    "http://site.hamshad.ir",
    "https://repo-test.darkube.app",
]

WSGI_APPLICATION = 'kubeweb.wsgi.application'

DATABASES = { # local
    # 'default': { 
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2', 
    #     'NAME': os.getenv('POSTGRES_DB', 'kubeweb'),
    #     'USER': os.getenv('POSTGRES_USER', 'kubeuser'),
    #     'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'kubepass'),
    #     'HOST': os.getenv('POSTGRES_HOST', 'postgres-service.hamravesh-project.svc.cluster.local'),
    #     'PORT': os.getenv('POSTGRES_PORT', '5432'),
    # }
    # 'default': { # imagedocker test
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2', 
    #     'NAME': os.getenv('POSTGRES_DB', 'postgres'),
    #     'USER': os.getenv('POSTGRES_USER', 'postgres'),
    #     'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'D5L2mNpBW7F9fO278os2'),
    #     'HOST': os.getenv('POSTGRES_HOST', 'database-test.dehghanimehrshad82.svc'),
    #     'PORT': os.getenv('POSTGRES_PORT', '5432'),
    # } 
    # 'default': { # git repo test
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2', 
    #     'NAME': os.getenv('POSTGRES_DB', 'postgres'),
    #     'USER': os.getenv('POSTGRES_USER', 'postgres'),
    #     'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'D5L2mNpBW7F9fO278os2'),
    #     'HOST': os.getenv('POSTGRES_HOST', '81.12.30.45'),
    #     'PORT': os.getenv('POSTGRES_PORT', '31920'),
    # } 
    'default': { # manual test
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': os.getenv('POSTGRES_DB', 'postgres'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'qwedsazxc'),
        'HOST': os.getenv('POSTGRES_HOST', 'database-manual.dehghanimehrshad82-database-manual.svc'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    } 
}


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build') 

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

KUBERNETES_CONFIG_PATH = os.environ.get('KUBECONFIG', None)
