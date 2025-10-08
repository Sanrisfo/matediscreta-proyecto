# matediscreta-proyecto
Proyecto de final del curso de Matemáticas discretas de Jeremy y Santiago
py


# ============================================
# GUÍA TURÍSTICA INTELIGENTE - RUBER
# Estructura completa del proyecto Django
# ============================================

# ============================================
# 1. ESTRUCTURA DE CARPETAS
# ============================================
"""
ruber_project/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── ruber_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   ├── templates/
│   │   └── core/
│   │       ├── base.html
│   │       └── home.html
│   └── static/
│       └── core/
│           ├── css/
│           │   └── styles.css
│           └── js/
│               └── main.js
├── usuarios/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── tests.py
│   └── templates/
│       └── usuarios/
│           ├── login.html
│           ├── registro.html
│           └── perfil.html
├── lugares/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   └── templates/
│       └── lugares/
│           ├── lista_destinos.html
│           └── detalle_destino.html
├── rutas/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── algorithms.py
│   ├── tests.py
│   └── templates/
│       └── rutas/
│           └── mapa_rutas.html
├── itinerarios/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── generators.py
│   ├── tests.py
│   └── templates/
│       └── itinerarios/
│           ├── generar.html
│           └── detalle_itinerario.html
└── tickets/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── qr_generator.py
    ├── tests.py
    └── templates/
        └── tickets/
            └── ticket_detail.html
"""

# ============================================
# 2. requirements.txt
# ============================================
"""
Django>=4.2,<5.0
Pillow>=10.0.0
qrcode>=7.4.2
django-crispy-forms>=2.0
crispy-bootstrap5>=0.7
python-decouple>=3.8
"""

# ============================================
# 3. README.md
# ============================================
"""
# 🌍 Ruber - Guía Turística Inteligente

## Descripción
Sistema web para turistas que permite descubrir destinos, calcular rutas óptimas, 
generar itinerarios personalizados y obtener tickets electrónicos con QR.

## Características
- 🔐 Sistema de login con preferencias de usuario
- 📍 Catálogo de destinos con categorías y actividades
- 🗺️ Cálculo de rutas óptimas usando grafos (Dijkstra)
- 🎯 Generación automática de itinerarios según presupuesto y tiempo
- 🎫 Tickets electrónicos con código QR
- 🔍 Búsqueda en lenguaje natural (próximamente)

## Tecnologías
- Django 4.2+
- SQLite (desarrollo) / PostgreSQL (producción)
- HTML5, CSS3, JavaScript
- Algoritmos: Grafos, Dijkstra, Combinatoria

## Instalación

### 1. Clonar repositorio
```bash
git clone <tu-repo>
cd ruber_project
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear superusuario
```bash
python manage.py createsuperuser
```

### 6. Ejecutar servidor
```bash
python manage.py runserver
```

Visita: http://127.0.0.1:8000

## Estructura del proyecto
- **core/**: App principal con homepage
- **usuarios/**: Gestión de turistas y preferencias
- **lugares/**: Destinos, actividades y categorías
- **rutas/**: Algoritmos de grafos para rutas óptimas
- **itinerarios/**: Generación automática de planes turísticos
- **tickets/**: Emisión de tickets con QR

## Próximos pasos
- [ ] Implementar algoritmo Dijkstra completo
- [ ] Sistema de búsqueda en lenguaje natural
- [ ] Integración con mapas interactivos (Leaflet)
- [ ] Sistema de pagos
- [ ] App móvil
"""

# ============================================
# 4. .gitignore
# ============================================
"""
# Python
*.pyc
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Django
*.log
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
"""

# ============================================
# 5. ruber_project/settings.py (CONFIGURACIÓN CLAVE)
# ============================================
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-CHANGE-THIS-IN-PRODUCTION'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Apps del proyecto
    'core',
    'usuarios',
    'lugares',
    'rutas',
    'itinerarios',
    'tickets',
    
    # Terceros
    'crispy_forms',
    'crispy_bootstrap5',
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

ROOT_URLCONF = 'ruber_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'ruber_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'usuarios.Turista'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = 'core:home'
LOGOUT_REDIRECT_URL = 'core:home'
"""

# ============================================
# 6. ruber_project/urls.py
# ============================================
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('lugares/', include('lugares.urls')),
    path('rutas/', include('rutas.urls')),
    path('itinerarios/', include('itinerarios.urls')),
    path('tickets/', include('tickets.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
"""

print("✅ Estructura base del proyecto Ruber creada")
print("\n📝 SIGUIENTE PASO: Te enviaré los modelos de cada app en el próximo artefacto")
