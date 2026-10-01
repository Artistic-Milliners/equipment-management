# EMS Application Production Readiness Guide

**Last Updated:** January 27, 2025
**Status:** Documentation for Future Implementation
**Priority:** CRITICAL security issues must be addressed before production deployment

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Security Audit Findings](#security-audit-findings)
3. [Phase 1: CRITICAL Security Fixes](#phase-1-critical-security-fixes)
4. [Phase 2: HIGH Priority Fixes](#phase-2-high-priority-fixes)
5. [Phase 3: MEDIUM Priority Improvements](#phase-3-medium-priority-improvements)
6. [Phase 4: LOW Priority Enhancements](#phase-4-low-priority-enhancements)
7. [Implementation Timeline](#implementation-timeline)
8. [Verification & Testing](#verification--testing)
9. [Production Deployment Checklist](#production-deployment-checklist)
10. [Maintenance & Support](#maintenance--support)

---

## Executive Summary

This document outlines a comprehensive security and operational audit of the EMS (Equipment Management System) application. The audit identified **critical security vulnerabilities** and operational gaps that must be addressed before production deployment.

### Severity Breakdown

- 🔴 **CRITICAL**: 8 issues (immediate security risks - data breaches, unauthorized access)
- 🟠 **HIGH**: 12 issues (significant security/operational concerns)
- 🟡 **MEDIUM**: 15 issues (performance and reliability improvements)
- 🟢 **LOW**: 8 issues (nice-to-have enhancements)

### Minimum Viable Production

To deploy safely to production, **Phase 1 (CRITICAL)** and **Phase 2 (HIGH)** must be completed. This represents approximately **2 weeks of focused development work**.

### Current State

The application currently has:
- ✅ Docker setup complete
- ✅ Database models well-structured
- ✅ Core functionality working
- ❌ Multiple critical security vulnerabilities
- ❌ No production-grade logging or monitoring
- ❌ No automated backups
- ❌ No file upload validation

---

## Security Audit Findings

### Critical Vulnerabilities (Immediate Attention Required)

1. **Hardcoded Secrets** - SECRET_KEY, JWT tokens, and database passwords exposed in source code
2. **Debug Mode Enabled** - Full stack traces and system information exposed to users
3. **Wildcard ALLOWED_HOSTS** - Vulnerable to host header injection attacks
4. **No Session Security** - Cookies vulnerable to hijacking and CSRF attacks
5. **Unvalidated File Uploads** - Allows malicious file uploads (malware, scripts)
6. **Unauthenticated API Endpoints** - Critical endpoints accessible without authentication
7. **XSS Vulnerability** - `|safe` filter in templates allows script injection
8. **No Content Security Policy** - No protection against XSS and data injection

### High Priority Issues

1. **No Log Rotation** - Log files grow indefinitely, will fill disk space
2. **Print Statements Instead of Logging** - No audit trail or monitoring capability
3. **No Database Connection Pooling** - Creates new connection for each request (performance)
4. **No Health Check Endpoints** - Cannot monitor application health
5. **No Automated Backups** - Manual backups only, risk of data loss
6. **No Error Monitoring** - No alerting when errors occur in production

### Medium Priority Improvements

1. **No Query Performance Monitoring** - Cannot detect N+1 queries or slow operations
2. **No Rate Limiting** - Vulnerable to abuse and DoS attacks
3. **No Input Sanitization** - User input not properly cleaned
4. **No Automated Tests** - Risk of regressions when making changes

### Low Priority Enhancements

1. **No Caching** - Every request hits database, slower response times
2. **No API Documentation** - Difficult for developers to understand API endpoints

---

## Phase 1: CRITICAL Security Fixes

### 🔴 CRITICAL-1: Remove Hardcoded Secrets

**Current State:**
```python
# ems/settings.py
SECRET_KEY = 'django-insecure-!+@l^5&)5mr#o0+-l6uxb&o9wkb!j-)+h3k1%s8)1=f%_$u8_^'
JWT_SECRET_KEY = 'django-insecure-!+@l^5&)5mr#o0+-l6uxb&o9wkb!j-)+h3k1%s8)1=f%_$u8_^'
DATABASES = {
    'default': {
        'PASSWORD': 'abcd@1234',  # Exposed in source control
    }
}
```

**Risk:** Anyone with source code access can:
- Forge session cookies and impersonate any user
- Generate valid JWT tokens
- Access the database directly

**Solution:**

1. **Update settings.py** (lines 28, 35, 100-101):
```python
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'ems'),
        'USER': os.getenv('DB_USER', 'zohaib'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

2. **Generate new secrets:**
```bash
# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

3. **Update .env file:**
```bash
SECRET_KEY=<generated-key-here>
JWT_SECRET_KEY=<another-generated-key>
DB_PASSWORD=<strong-password>
```

**Files to Modify:**
- `ems/settings.py` (lines 28, 35, 100-101)
- `.env` (add new secrets)

---

### 🔴 CRITICAL-2: Disable DEBUG Mode

**Current State:**
```python
# ems/settings.py line 31
DEBUG = True
```

**Risk:** Exposes:
- Full stack traces with file paths and code structure
- SQL queries with sensitive data
- All settings variables
- System information

**Solution:**

1. **Update settings.py** (line 31):
```python
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Add error handlers (at end of settings.py)
HANDLER_404 = 'ems.views.handler404'
HANDLER_500 = 'ems.views.handler500'
```

2. **Create error handlers** (`ems/views.py` - new file):
```python
from django.shortcuts import render

def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)
```

3. **Create error templates:**
   - `templates/errors/404.html`
   - `templates/errors/500.html`

4. **Update .env:**
```bash
DEBUG=False
```

**Files to Create:**
- `ems/views.py`
- `templates/errors/404.html`
- `templates/errors/500.html`

**Files to Modify:**
- `ems/settings.py` (line 31)
- `.env`

---

### 🔴 CRITICAL-3: Restrict ALLOWED_HOSTS

**Current State:**
```python
# ems/settings.py line 33
ALLOWED_HOSTS = ['*']
```

**Risk:** Vulnerable to:
- Host header injection attacks
- Cache poisoning
- Password reset poisoning

**Solution:**

1. **Update settings.py** (line 33):
```python
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

2. **Update .env:**
```bash
# Development
ALLOWED_HOSTS=localhost,127.0.0.1

# Production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost
```

**Files to Modify:**
- `ems/settings.py` (line 33)
- `.env`

---

### 🔴 CRITICAL-4: Secure Session Configuration

**Current State:** No session security configured

**Risk:**
- Session cookies vulnerable to hijacking
- CSRF attacks possible
- Sessions don't expire properly

**Solution:**

Add after line 144 in `ems/settings.py`:

```python
# Session Security
SESSION_COOKIE_SECURE = not DEBUG  # HTTPS only in production
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF Security
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_USE_SESSIONS = True

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS Settings (enable when SSL configured)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

**Files to Modify:**
- `ems/settings.py` (add after line 144)

---

### 🔴 CRITICAL-5: Fix Unvalidated File Uploads

**Current State:** No validation on uploaded files in:
- `User/views.py:304-310` - ComplainClosingView
- `maintenance/views.py:322-328` - ComplainReviewView
- `maintenance/views.py:440-444` - TemporaryIssueReviewView

**Risk:**
- Malicious file uploads (malware, web shells)
- Path traversal attacks
- Resource exhaustion (large files)
- XSS via SVG files

**Solution:**

1. **Create validation utility** (`core/validators.py` - new file):

```python
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image
import os

ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_image_file(file):
    """Validate uploaded image files"""
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(
            _(f'File size must be under {MAX_FILE_SIZE / (1024*1024)}MB')
        )

    # Check extension
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            _(f'File type {ext} not allowed. Allowed: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}')
        )

    # Validate it's actually an image
    try:
        img = Image.open(file)
        img.verify()
    except Exception:
        raise ValidationError(_('Invalid image file'))

    return file

def validate_files_list(files_list):
    """Validate multiple uploaded files"""
    if len(files_list) > 10:
        raise ValidationError(_('Maximum 10 files allowed'))

    for file in files_list:
        validate_image_file(file)

    return files_list
```

2. **Update ComplainClosingView** (`User/views.py` around line 297):

```python
from core.validators import validate_files_list
from django.core.exceptions import ValidationError
from django.contrib import messages

class ComplainClosingView(View):
    def post(self, request, issue_id):
        # ... existing code ...

        # Validate uploaded files BEFORE processing
        files = request.FILES.getlist("stateFile")
        if files:
            try:
                validate_files_list(files)
            except ValidationError as e:
                messages.error(request, f"File upload error: {str(e)}")
                return redirect('user:closingForm', issue_id=issue_id)

        # ... rest of existing code ...
```

3. **Apply same pattern to:**
   - `maintenance/views.py:322` - ComplainReviewView
   - `maintenance/views.py:440` - TemporaryIssueReviewView

**Files to Create:**
- `core/validators.py`

**Files to Modify:**
- `User/views.py` (lines 297-310)
- `maintenance/views.py` (lines 322-328, 440-444)

---

### 🔴 CRITICAL-6: Secure API Endpoints

**Current State:**
```python
# api/views.py
class MachineIssueCreateAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]  # Line 10-11

class IssueListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]  # Line 33-34
```

**Risk:**
- Unauthenticated users can create complaints
- Master issue list exposed without authentication
- No rate limiting on API endpoints

**Solution:**

1. **Update API views** (`api/views.py`):

```python
from rest_framework.permissions import IsAuthenticated

class MachineIssueCreateAPIView(generics.CreateAPIView):
    queryset = MachineIssue.objects.all()
    serializer_class = MachineIssueSerializer
    permission_classes = [IsAuthenticated]  # Changed

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class IssueListAPIView(generics.ListAPIView):
    serializer_class = IssueListSerializer
    permission_classes = [IsAuthenticated]  # Changed

    def get_queryset(self):
        equipment_id = self.kwargs.get('equipment_id')
        if not equipment_id:
            return IssueList.objects.none()
        return IssueList.objects.filter(
            equipment_id=equipment_id
        ).values('id', 'c_desc', 'error_code', 'machine_status')
```

2. **Add REST framework throttling** (`ems/settings.py`):

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

**Files to Modify:**
- `api/views.py` (lines 10-11, 33-34)
- `ems/settings.py` (add REST_FRAMEWORK config)

---

### 🔴 CRITICAL-7: Fix XSS Vulnerability

**Current State:**
```html
<!-- templates/index.html line 466 -->
{{ equipment.name|safe }}
```

**Risk:**
- Cross-site scripting (XSS) attacks
- Attackers can inject JavaScript code
- Session hijacking, data theft

**Solution:**

**Simple fix** (if no HTML needed):
```html
<!-- templates/index.html line 466 -->
{{ equipment.name }}  <!-- Remove |safe filter -->
```

**Advanced fix** (if HTML formatting needed):

1. **Create sanitization filter** (`core/templatetags/safe_html.py` - new file):

```python
from django import template
from django.utils.safestring import mark_safe
import bleach

register = template.Library()

ALLOWED_TAGS = ['b', 'i', 'u', 'strong', 'em', 'br']
ALLOWED_ATTRIBUTES = {}

@register.filter
def sanitize_html(value):
    """Sanitize HTML while allowing safe tags"""
    if not value:
        return ''
    return mark_safe(
        bleach.clean(
            value,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True
        )
    )
```

2. **Use in template:**
```html
{% load safe_html %}
{{ equipment.name|sanitize_html }}
```

3. **Add dependency** (`requirements.txt`):
```
bleach==6.1.0
```

**Files to Modify:**
- `templates/index.html` (line 466)

**Files to Create (optional):**
- `core/templatetags/safe_html.py`
- `core/templatetags/__init__.py`

**Dependencies to Add:**
- `bleach==6.1.0` (only if using sanitization filter)

---

### 🔴 CRITICAL-8: Add Content Security Policy

**Current State:** No CSP headers

**Risk:**
- XSS attacks not blocked
- Data injection attacks possible
- External scripts can be loaded

**Solution:**

1. **Add CSP middleware** (`ems/settings.py`):

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',  # Add this
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... rest of middleware
]

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",  # Needed for inline scripts
    "https://cdn.jsdelivr.net",
    "https://code.jquery.com"
)
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",  # Needed for inline styles
    "https://fonts.googleapis.com",
    "https://cdn.jsdelivr.net"
)
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = (
    "'self'",
    "https://fonts.gstatic.com",
    "https://cdn.jsdelivr.net"
)
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)
```

2. **Add dependency** (`requirements.txt`):
```
django-csp==3.8
```

**Files to Modify:**
- `ems/settings.py` (MIDDLEWARE and CSP config)
- `requirements.txt`

---

## Phase 2: HIGH Priority Fixes

### 🟠 HIGH-1: Implement Proper Logging System

**Current State:**
- `ems/settings.py` lines 171-188: Basic logging, no rotation
- Print statements throughout code (User/views.py, maintenance/views.py, etc.)
- Single log file grows indefinitely

**Problems:**
- Logs will eventually fill disk space
- No separation by severity level
- No audit trail
- Can't diagnose production issues

**Solution:**

1. **Replace LOGGING config** (`ems/settings.py` lines 171-188):

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {module} {funcName} {lineno} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {asctime} - {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'ems.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB per file
            'backupCount': 10,  # Keep 10 old files
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'ems_errors.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'ems': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'User': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'maintenance': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'file', 'error_file'],
        'level': 'INFO',
    },
}

# Email configuration for admin notifications
ADMINS = [
    ('Admin', os.getenv('ADMIN_EMAIL', 'admin@example.com')),
]
MANAGERS = ADMINS
```

2. **Replace print statements with logging:**

Find all print statements:
```bash
grep -rn "print(" User/ maintenance/ api/ core/ ems/ --include="*.py"
```

Example replacement in `User/views.py`:
```python
# Add at top of file
import logging
logger = logging.getLogger(__name__)

# Replace print statements
# OLD:
print(f"Added spare: {spare.name} (ID: {spare_id})")
print(f"Warning: Spare with ID {spare_id} not found")

# NEW:
logger.info(f"Added spare to complaint closing: {spare.name} (ID: {spare_id})")
logger.warning(f"Spare with ID {spare_id} not found during complaint closing")
```

3. **Update .env:**
```bash
ADMIN_EMAIL=your-email@example.com
```

**Files to Modify:**
- `ems/settings.py` (lines 171-188)
- `User/views.py` (replace all print statements)
- `maintenance/views.py` (replace all print statements)
- `api/views.py` (replace all print statements)
- `.env` (add ADMIN_EMAIL)

---

### 🟠 HIGH-2: Database Connection Pooling

**Current State:** New database connection created for every request

**Problem:**
- Poor performance under load
- Connection overhead on every request
- Connection pool exhaustion possible

**Solution:**

Update `ems/settings.py` DATABASES config (lines 100-107):

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'ems'),
        'USER': os.getenv('DB_USER', 'zohaib'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,  # Reuse connections for 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',  # 30s timeout
        },
    }
}

# Database backup configuration
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': BASE_DIR / 'backups'}
```

Add to INSTALLED_APPS:
```python
INSTALLED_APPS = [
    # ... existing apps ...
    'dbbackup',
]
```

Add dependency (`requirements.txt`):
```
django-dbbackup==4.0.2
```

**Files to Modify:**
- `ems/settings.py` (lines 100-107, INSTALLED_APPS)
- `requirements.txt`

---

### 🟠 HIGH-3: Health Check Endpoints

**Current State:** No health check endpoints

**Problem:**
- Cannot monitor if application is healthy
- Load balancers can't detect failures
- No automated health checks possible

**Solution:**

1. **Create health check module** (`ems/health.py` - new file):

```python
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Health check endpoint for monitoring
    Returns 200 if healthy, 503 if unhealthy
    """
    health_status = {
        'status': 'healthy',
        'checks': {}
    }
    status_code = 200

    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status['checks']['database'] = 'ok'
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status['checks']['database'] = 'error'
        health_status['status'] = 'unhealthy'
        status_code = 503

    # Cache check (if using cache)
    try:
        cache.set('health_check', 'ok', 30)
        if cache.get('health_check') == 'ok':
            health_status['checks']['cache'] = 'ok'
        else:
            health_status['checks']['cache'] = 'error'
    except Exception as e:
        logger.error(f"Cache health check failed: {str(e)}")
        health_status['checks']['cache'] = 'error'

    return JsonResponse(health_status, status=status_code)

def ready_check(request):
    """
    Readiness check for load balancers
    Returns 200 when app is ready to serve traffic
    """
    return JsonResponse({'status': 'ready'}, status=200)
```

2. **Add to URLs** (`ems/urls.py`):

```python
from django.urls import path, include
from .health import health_check, ready_check

urlpatterns = [
    # Health checks (at the top, before authentication)
    path('health/', health_check, name='health_check'),
    path('ready/', ready_check, name='ready_check'),

    # ... existing URLs ...
]
```

**Usage:**
```bash
# Check health
curl http://localhost:8000/health/

# Check readiness
curl http://localhost:8000/ready/
```

**Files to Create:**
- `ems/health.py`

**Files to Modify:**
- `ems/urls.py`

---

### 🟠 HIGH-4: Automated Database Backups

**Current State:** No automated backup system

**Problem:**
- Manual backups only
- Risk of data loss
- No backup rotation

**Solution:**

1. **Create backup command** (`core/management/commands/backup_database.py` - new file):

```python
from django.core.management.base import BaseCommand
from django.core.management import call_command
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Backup database and clean old backups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep',
            type=int,
            default=30,
            help='Number of backups to keep (default: 30)',
        )

    def handle(self, *args, **options):
        try:
            # Create backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'ems_backup_{timestamp}.dump'

            self.stdout.write(f'Creating backup: {backup_name}')
            call_command('dbbackup', output_filename=backup_name)

            self.stdout.write(
                self.style.SUCCESS('✓ Backup created successfully')
            )
            logger.info(f'Database backup created: {backup_name}')

            # Clean old backups
            from django.conf import settings
            backup_dir = settings.DBBACKUP_STORAGE_OPTIONS['location']

            backups = sorted(
                [f for f in os.listdir(backup_dir) if f.startswith('ems_backup_')],
                reverse=True
            )

            if len(backups) > options['keep']:
                for old_backup in backups[options['keep']:]:
                    os.remove(os.path.join(backup_dir, old_backup))
                    self.stdout.write(f'Removed old backup: {old_backup}')
                    logger.info(f'Removed old backup: {old_backup}')

            self.stdout.write(
                self.style.SUCCESS('✓ Backup rotation completed')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Backup failed: {str(e)}')
            )
            logger.error(f'Database backup failed: {str(e)}')
            raise
```

2. **Manual usage:**
```bash
python manage.py backup_database
python manage.py backup_database --keep=30
```

3. **Automated scheduling:**

**Windows (Task Scheduler):**
- Program: `python`
- Arguments: `manage.py backup_database --keep=30`
- Start in: `d:\Zohaib\webapps\ems\ems`
- Trigger: Daily at 2:00 AM

**Linux (crontab):**
```bash
0 2 * * * cd /path/to/ems && python manage.py backup_database --keep=30
```

4. **Restore from backup:**
```bash
python manage.py dbrestore --input-filename=ems_backup_20250127_020000.dump
```

**Files to Create:**
- `core/management/commands/backup_database.py`
- `core/management/commands/__init__.py` (if doesn't exist)
- `core/management/__init__.py` (if doesn't exist)

**Dependencies:**
- `django-dbbackup==4.0.2` (from HIGH-2)

---

### 🟠 HIGH-5: Monitoring and Alerting

**Current State:** No error monitoring or alerting

**Problem:**
- Errors in production go unnoticed
- No proactive alerting
- Difficult to diagnose issues

**Solution:**

1. **Add Sentry for error tracking** (`ems/settings.py` - add at end):

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,  # 10% of transactions
        send_default_pii=False,  # Don't send personal data
        environment=os.getenv('ENVIRONMENT', 'production'),
    )
```

2. **Update .env:**
```bash
SENTRY_DSN=https://your-dsn@sentry.io/project-id
ENVIRONMENT=production
```

3. **Add dependencies** (`requirements.txt`):
```
sentry-sdk==1.40.0
django-prometheus==2.3.1
```

**Setup:**
1. Sign up for Sentry: https://sentry.io
2. Create new project
3. Copy DSN to .env
4. Errors will automatically be reported

**Files to Modify:**
- `ems/settings.py` (add Sentry config)
- `requirements.txt`
- `.env`

---

## Phase 3: MEDIUM Priority Improvements

### 🟡 MEDIUM-1: Query Performance Monitoring

**Solution:**

Create `core/middleware/query_monitor.py`:

```python
import logging
from django.db import connection

logger = logging.getLogger('django.db.backends')

class QueryCountMiddleware:
    """Log slow queries and query counts"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        queries_before = len(connection.queries)

        response = self.get_response(request)

        queries_after = len(connection.queries)
        query_count = queries_after - queries_before

        # Log if excessive queries (N+1 indicator)
        if query_count > 20:
            logger.warning(
                f'High query count on {request.path}: {query_count} queries'
            )

        # Log slow queries
        for query in connection.queries[queries_before:]:
            time = float(query['time'])
            if time > 0.5:  # Slower than 500ms
                logger.warning(
                    f'Slow query ({time}s): {query["sql"][:200]}'
                )

        return response
```

Add to `ems/settings.py`:
```python
if DEBUG:
    MIDDLEWARE += ['core.middleware.query_monitor.QueryCountMiddleware']
```

**Files to Create:**
- `core/middleware/query_monitor.py`
- `core/middleware/__init__.py`

**Files to Modify:**
- `ems/settings.py`

---

### 🟡 MEDIUM-2: Request Rate Limiting

**Solution:**

1. **Create decorator** (`core/decorators.py`):

```python
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.decorators import login_required
from functools import wraps

def ratelimit_view(rate='100/h', method='POST', key='user'):
    """
    Combined rate limit and authentication decorator
    Usage: @ratelimit_view(rate='10/m')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        @ratelimit(key=key, rate=rate, method=method, block=True)
        def wrapped_view(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator
```

2. **Apply to views:**

```python
# User/views.py
from core.decorators import ratelimit_view

class ComplainClosingView(View):
    @ratelimit_view(rate='10/h', method='POST')
    def post(self, request, issue_id):
        # ... existing code ...
```

3. **Add dependency:**
```
django-ratelimit==4.1.0
```

**Files to Create:**
- `core/decorators.py`

**Files to Modify:**
- `User/views.py`
- `maintenance/views.py`
- `requirements.txt`

---

### 🟡 MEDIUM-3: Input Sanitization

**Solution:**

Create `core/utils/sanitize.py`:

```python
import bleach
from django.utils.html import escape

def sanitize_text_input(text, max_length=None):
    """Sanitize user text input"""
    if not text:
        return ''

    # Remove HTML tags
    cleaned = bleach.clean(text, tags=[], strip=True)

    # Trim whitespace
    cleaned = cleaned.strip()

    # Enforce max length
    if max_length:
        cleaned = cleaned[:max_length]

    return cleaned

def sanitize_html_input(html, allowed_tags=None):
    """Sanitize HTML input (for rich text)"""
    if not html:
        return ''

    if allowed_tags is None:
        allowed_tags = ['b', 'i', 'u', 'strong', 'em', 'br', 'p']

    return bleach.clean(
        html,
        tags=allowed_tags,
        attributes={},
        strip=True
    )
```

Use in views:
```python
from core.utils.sanitize import sanitize_text_input

solution_desc = sanitize_text_input(
    request.POST.get("solutionDescription"),
    max_length=5000
)
```

**Files to Create:**
- `core/utils/sanitize.py`
- `core/utils/__init__.py`

**Files to Modify:**
- `User/views.py`
- `maintenance/views.py`

**Dependencies:**
- `bleach==6.1.0` (from CRITICAL-7)

---

### 🟡 MEDIUM-4: Automated Tests

**Solution:**

Create `tests/test_complaint_workflow.py`:

```python
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from core.models import MachineIssue, Equipment
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class ComplaintWorkflowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.equipment = Equipment.objects.create(
            name='Test Equipment',
            machine_id='TEST-001'
        )

    def test_complaint_creation_requires_auth(self):
        """Test that complaint creation requires authentication"""
        response = self.client.post('/api/machine-issue/', {
            'equipment': self.equipment.id,
            'description': 'Test issue'
        })
        self.assertEqual(response.status_code, 401)

    def test_file_upload_validation(self):
        """Test that file upload validation works"""
        self.client.login(username='testuser', password='testpass123')

        # File too large
        large_file = SimpleUploadedFile(
            "test.jpg",
            b"x" * (11 * 1024 * 1024),  # 11MB
            content_type="image/jpeg"
        )

        response = self.client.post('/complaint/closing/1/', {
            'stateFile': large_file
        })

        self.assertContains(response, 'File size must be under')
```

Run tests:
```bash
python manage.py test
```

**Files to Create:**
- `tests/test_complaint_workflow.py`
- `tests/__init__.py`

**Dependencies:**
```
coverage==7.4.0
```

---

## Phase 4: LOW Priority Enhancements

### 🟢 LOW-1: Redis Caching

**Solution:**

1. **Configure caching** (`ems/settings.py`):

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True
            }
        },
        'KEY_PREFIX': 'ems',
        'TIMEOUT': 300,  # 5 minutes
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

2. **Update docker-compose.yml:**

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

volumes:
  redis_data:
```

3. **Add dependencies:**
```
redis==5.0.1
django-redis==5.4.0
```

4. **Use caching in views:**

```python
from django.core.cache import cache

def get_equipment_list():
    """Get equipment list with caching"""
    cache_key = 'equipment_list'
    equipment = cache.get(cache_key)

    if equipment is None:
        equipment = list(Equipment.objects.all().values('id', 'name'))
        cache.set(cache_key, equipment, 600)  # 10 minutes

    return equipment
```

**Files to Modify:**
- `ems/settings.py`
- `docker-compose.yml`
- `requirements.txt`
- `User/views.py` (add caching)

---

### 🟢 LOW-2: API Documentation

**Solution:**

1. **Configure** (`ems/settings.py`):

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'EMS API',
    'DESCRIPTION': 'Equipment Management System API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

2. **Add URLs** (`ems/urls.py`):

```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # ... existing URLs ...
]
```

3. **Add dependency:**
```
drf-spectacular==0.27.1
```

Access at: http://localhost:8000/api/docs/

**Files to Modify:**
- `ems/settings.py`
- `ems/urls.py`
- `requirements.txt`

---

## Implementation Timeline

### Week 1: CRITICAL Security Fixes
**Must complete before any production deployment**

- **Day 1-2:**
  - ✓ Remove hardcoded secrets
  - ✓ Disable DEBUG mode
  - ✓ Restrict ALLOWED_HOSTS
  - ✓ Secure session configuration

- **Day 3-4:**
  - ✓ Fix file upload validation
  - ✓ Secure API endpoints

- **Day 5:**
  - ✓ Fix XSS vulnerability
  - ✓ Add CSP headers
  - ✓ Deploy to staging for testing

### Week 2: HIGH Priority Operations
**Required for production monitoring and reliability**

- **Day 1-2:**
  - ✓ Implement logging system
  - ✓ Database optimization

- **Day 3:**
  - ✓ Health check endpoints
  - ✓ Automated backups

- **Day 4-5:**
  - ✓ Monitoring setup
  - ✓ Test all Phase 2 changes

### Week 3: MEDIUM Priority (Optional but Recommended)

- **Day 1:** Query performance monitoring
- **Day 2:** Rate limiting
- **Day 3:** Input sanitization
- **Day 4-5:** Automated tests

### Week 4: LOW Priority (Nice to Have)

- **Day 1-2:** Redis caching
- **Day 3:** API documentation
- **Day 4-5:** Final testing

---

## Verification & Testing

### After Phase 1 (CRITICAL)

**1. Test environment variables:**
```bash
python manage.py shell
>>> from django.conf import settings
>>> assert settings.DEBUG == False
>>> assert settings.SECRET_KEY != 'django-insecure-...'
>>> assert '*' not in settings.ALLOWED_HOSTS
>>> print("✓ All security checks passed")
```

**2. Test API authentication:**
```bash
# Should return 401
curl http://localhost:8000/api/machine-issue/

# Should work with auth
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/machine-issue/
```

**3. Test file upload validation:**
- Navigate to complaint closing form
- Try 15MB file → Should reject
- Try .exe file → Should reject
- Try valid 2MB .jpg → Should succeed

**4. Test CSP headers:**
```bash
curl -I http://localhost:8000/
# Look for: Content-Security-Policy header
```

### After Phase 2 (HIGH)

**1. Test logging:**
```bash
ls -lh logs/
# Should see: ems.log, ems_errors.log, security.log

tail -f logs/ems.log
```

**2. Test health endpoints:**
```bash
curl http://localhost:8000/health/
# Expected: {"status": "healthy", "checks": {"database": "ok"}}

curl http://localhost:8000/ready/
# Expected: {"status": "ready"}
```

**3. Test database backup:**
```bash
python manage.py backup_database
ls -lh backups/
# Should see new backup file
```

### After Phase 3 (MEDIUM)

**1. Test rate limiting:**
```bash
# Make 11 rapid requests
for i in {1..11}; do curl -X POST http://localhost:8000/some/endpoint; done
# 11th should fail with rate limit error
```

**2. Run automated tests:**
```bash
python manage.py test
coverage run --source='.' manage.py test
coverage report
```

### After Phase 4 (LOW)

**1. Test Redis caching:**
```bash
redis-cli
> KEYS ems:*
> GET ems:equipment_list
```

**2. Test API docs:**
Visit: http://localhost:8000/api/docs/

---

## Production Deployment Checklist

### Pre-Deployment

- [ ] All Phase 1 (CRITICAL) completed
- [ ] All Phase 2 (HIGH) completed
- [ ] `.env` configured for production
- [ ] New SECRET_KEY generated
- [ ] DEBUG=False verified
- [ ] ALLOWED_HOSTS set to domain
- [ ] Strong database password set
- [ ] SSL certificates installed
- [ ] Static files collected
- [ ] Migrations applied
- [ ] Superuser created

### Deployment

- [ ] Health checks responding
- [ ] Logging configured and working
- [ ] Log rotation verified
- [ ] Automated backups scheduled
- [ ] Sentry/monitoring active
- [ ] Error pages (404/500) tested
- [ ] HTTPS working
- [ ] All APIs require auth
- [ ] File uploads validated

### Post-Deployment

- [ ] Load testing performed
- [ ] Backup restoration tested
- [ ] Security scan run (OWASP ZAP)
- [ ] Monitoring alerts working
- [ ] Admin password changed
- [ ] Firewall rules configured
- [ ] Disk space monitored
- [ ] Database performance checked

---

## Maintenance & Support

### Daily Tasks

- Monitor error logs: `tail -f logs/ems_errors.log`
- Check Sentry for new errors
- Verify backups completed
- Review security logs for suspicious activity

### Weekly Tasks

- Review slow query logs
- Check disk space usage
- Review security logs
- Test backup restoration
- Update dependencies if needed

### Monthly Tasks

- Review and archive old logs
- Update dependencies: `pip list --outdated`
- Performance testing
- Security audit
- Review and update documentation

---

## Dependencies Summary

All new dependencies to add to `requirements.txt`:

```txt
# Current dependencies (keep these)
asgiref==3.7.2
Django==5.0.1
djangorestframework==3.14.0
pillow==10.2.0
pytz==2023.4
setuptools==68.2.2
sqlparse==0.4.4
tzdata==2023.4
wheel==0.41.2
psycopg2-binary==2.9.9
gunicorn==21.2.0
python-dotenv==1.0.0

# Phase 1 - CRITICAL (Security)
bleach==6.1.0
django-csp==3.8

# Phase 2 - HIGH (Operations)
sentry-sdk==1.40.0
django-prometheus==2.3.1
django-dbbackup==4.0.2

# Phase 3 - MEDIUM (Performance)
django-ratelimit==4.1.0
coverage==7.4.0

# Phase 4 - LOW (Enhancements)
redis==5.0.1
django-redis==5.4.0
drf-spectacular==0.27.1
```

---

## Environment Variables

Complete `.env` file template:

```bash
# Django Core
DEBUG=False
SECRET_KEY=<generate-with-command-below>
JWT_SECRET_KEY=<generate-another-key>
JWT_ALGORITHM=HS256
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost

# Database
DB_NAME=ems
DB_USER=zohaib
DB_PASSWORD=<strong-password>
DB_HOST=db
DB_PORT=5432

# Email (for error notifications)
ADMIN_EMAIL=admin@yourdomain.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Monitoring
SENTRY_DSN=https://your-dsn@sentry.io/project
ENVIRONMENT=production

# Caching (Phase 4 - optional)
REDIS_URL=redis://redis:6379/1
```

**Generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Files to Create

### Phase 1 - CRITICAL
1. `ems/views.py` - Error handlers
2. `templates/errors/404.html` - 404 page
3. `templates/errors/500.html` - 500 page
4. `core/validators.py` - File validation
5. `core/templatetags/safe_html.py` - HTML sanitization (optional)
6. `core/templatetags/__init__.py`

### Phase 2 - HIGH
7. `ems/health.py` - Health checks
8. `core/management/commands/backup_database.py` - Backups
9. `core/management/commands/__init__.py`
10. `core/management/__init__.py`

### Phase 3 - MEDIUM
11. `core/middleware/query_monitor.py` - Query monitoring
12. `core/middleware/__init__.py`
13. `core/decorators.py` - Rate limiting
14. `core/utils/sanitize.py` - Input sanitization
15. `core/utils/__init__.py`
16. `tests/test_complaint_workflow.py` - Tests
17. `tests/__init__.py`

---

## Files to Modify

### Phase 1 - CRITICAL
1. `ems/settings.py` - Multiple security configs
2. `templates/index.html` - Remove `|safe` filter (line 466)
3. `.env` - Add all secrets
4. `requirements.txt` - Add dependencies
5. `User/views.py` - File validation
6. `maintenance/views.py` - File validation
7. `api/views.py` - Authentication

### Phase 2 - HIGH
8. `ems/urls.py` - Health endpoints
9. `User/views.py` - Replace print statements
10. `maintenance/views.py` - Replace print statements

### Phase 3 - MEDIUM
11. `User/views.py` - Rate limiting, sanitization
12. `maintenance/views.py` - Rate limiting, sanitization

### Phase 4 - LOW
13. `docker-compose.yml` - Redis service
14. `User/views.py` - Caching

---

## Resources

- **Django Security:** https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **Sentry Django:** https://docs.sentry.io/platforms/python/guides/django/
- **Docker Security:** https://docs.docker.com/engine/security/
- **Django Production:** https://docs.djangoproject.com/en/5.0/howto/deployment/

---

## Quick Start Commands

### Generate Secrets
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Create Directories
```bash
mkdir -p logs backups templates/errors core/templatetags core/management/commands core/middleware core/utils tests
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Migrations
```bash
python manage.py migrate
```

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Test Setup
```bash
python manage.py check --deploy
python manage.py test
```

---

**Document Version:** 1.0
**Created:** January 27, 2025
**Next Review:** Before production deployment
