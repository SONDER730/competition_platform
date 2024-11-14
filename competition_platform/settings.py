# competition_platform/settings.py
import os

from datetime import timedelta
import redis
# 安全密钥
SECRET_KEY = 'your-secret-key'  # 请替换为您的实际密钥


# 自定义用户模型
AUTH_USER_MODEL = 'oAuth.CustomUser'

INSTALLED_APPS = [
    # Django 默认应用
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 第三方应用
    'rest_framework',
    'corsheaders',
    'django_filters',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    # 自定义应用
    'apps.competitions',
    'apps.oAuth.apps.OauthConfig',  # 确保只添加一次
    'apps.student_center.apps.StudentCenterConfig',
    'apps.teacher_center.apps.TeacherCenterConfig',
    'apps.competition_application',
]

ROOT_URLCONF = 'competition_platform.urls'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_BLACKLIST_ENABLED': True,
}

DEBUG = True
# CSRF 配置
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

CORS_ALLOW_ALL_ORIGINS = True  # 仅在开发环境使用

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True  # 仅在开发环境使用

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # 模板目录
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



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'competition_db',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


CORS_ALLOW_CREDENTIALS = True

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    # ... 其他验证器
]

ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # 使用真实的域名/IP

STATIC_URL = '/static/'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

PDF_FILES_DIR = os.path.join(MEDIA_ROOT, 'pdf_files')
PDF_CACHE_DURATION = 86400

# 确保目录存在
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(PDF_FILES_DIR, exist_ok=True)

# 文件上传配置
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# 超时设置
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# 竞赛文件存储路径
COMPETITION_FILES_DIR = os.path.join(MEDIA_ROOT, 'competition_files')
os.makedirs(COMPETITION_FILES_DIR, exist_ok=True)


# 确保报销文件目录存在
REIMBURSEMENT_FILES_DIR = os.path.join(MEDIA_ROOT, 'reimbursement_files')
os.makedirs(REIMBURSEMENT_FILES_DIR, exist_ok=True)

# 国际化
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'  # 您的邮件服务器地址
EMAIL_PORT = 587  # 通常为587（TLS）或465（SSL）
EMAIL_USE_TLS = True  # 或 EMAIL_USE_SSL = True，根据您的邮件服务器要求
EMAIL_HOST_USER = 'your-email@example.com'  # 您的邮件地址
EMAIL_HOST_PASSWORD = 'your-email-password'  # 您的邮件密码
DEFAULT_FROM_EMAIL = 'Your Project <your-email@example.com>'

# # 配置 Redis 连接
# REDIS_HOST = 'localhost'
# REDIS_PORT = 6379
# REDIS_DB = 0
#
# # 创建 Redis 连接对象
# redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)