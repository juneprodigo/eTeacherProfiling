# eTeacher Profiling System — Docker Deployment Guide
**CS Form No. 212 (Revised 2026) & Daily Time Record (CS Form No. 48)**  
*Cagayan East Elementary School (CES) / Department of Education (DepEd)*

---

## 🏗️ Architecture Overview

The containerized stack runs three orchestrated services managed via Docker Compose:

1. **`frontend` (Nginx Alpine + Vue 3 Single Page Application)**
   - Pre-compiles the Vue 3 + Vite frontend into optimized static bundles.
   - Serves the application with HTTP gzip compression and asset caching headers.
   - Acts as a reverse proxy routing `/api/` and `/admin/` requests to the Django backend.
   - Serves uploaded media (`/media/`) and collected static files (`/static/`) directly.

2. **`backend` (Python 3.12-slim + Django + Gunicorn WSGI)**
   - High-performance production WSGI application server with multi-worker concurrency.
   - Automated startup entrypoint:
     - Waits for database readiness.
     - Runs pending database migrations (`manage.py migrate`).
     - Auto-seeds administrative & test accounts (`admin`, `hr_officer`, `teacher1`).
     - Auto-seeds reference libraries (Trainings, Voluntary Work, Experience, Civil Service Eligibility).
     - Auto-seeds standard faculty shift settings.
     - Collects static files (`manage.py collectstatic`).
   - Equipped with native PDF generation libraries (`xhtml2pdf`, `weasyprint`, `pango`, `cairo`) and Excel exporters (`openpyxl`).

3. **`db` (PostgreSQL 16 Alpine)**
   - Production PostgreSQL database with automated health checks and persistent volume storage.

---

## 🚀 Quick Start

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) or Docker Engine & Docker Compose v2 (Linux).

### 2. Configure Environment Variables
Copy the template configuration file:
```bash
cp .env.example .env
```
*(On Windows PowerShell: `Copy-Item .env.example .env`)*

Review `.env` and adjust passwords or ports as needed:
- `PORT`: HTTP port to expose (default is `80`; change to `8080` if port 80 is occupied by IIS/Apache).
- `DB_PASSWORD`: Strong password for the database.
- `SECRET_KEY`: A secure random string for Django token signing.

### 3. Build & Launch Containers
```bash
docker compose up -d --build
```

### 4. Access the Application
Open your browser and navigate to:
- **Web Application**: [http://localhost](http://localhost) (or `http://localhost:8080` if custom port)
- **Django Admin**: [http://localhost/admin/](http://localhost/admin/)
- **API Root**: [http://localhost/api/](http://localhost/api/)

---

## 🔑 Default Initial Credentials

When launched for the first time, the entrypoint seeds the following accounts:

| Role | Username | Password | Email |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `Admin@123456` | `admin@ces.deped.gov.ph` |
| **HR Officer** | `hr_officer` | `Hr@123456` | `hr@ces.deped.gov.ph` |
| **Faculty / Teacher** | `teacher1` | `Teacher@123456` | `teacher1@ces.deped.gov.ph` |

> [!WARNING]
> Please change default passwords after first login in production environments!

---

## 🛠️ Management & Maintenance Commands

### View Service Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

### Create a New Superuser
```bash
docker compose exec backend python manage.py createsuperuser
```

### Run Migrations Manually
```bash
docker compose exec backend python manage.py migrate
```

### Re-seed Reference Libraries
```bash
docker compose exec backend python manage.py seed_libraries
```

### Open Django Shell
```bash
docker compose exec backend python manage.py shell
```

### Backup & Restore Database
**Backup**:
```bash
docker compose exec -T db pg_dump -U postgres eteacher_profiling_db > backup_$(date +%Y%m%d_%H%M%S).sql
```
*(On Windows PowerShell: `docker compose exec -T db pg_dump -U postgres eteacher_profiling_db > backup.sql`)*

**Restore**:
```bash
docker compose exec -T db psql -U postgres eteacher_profiling_db < backup.sql
```

### Stopping & Restarting Services
```bash
# Stop containers without deleting data
docker compose stop

# Restart containers
docker compose restart

# Bring down containers (data in named volumes is preserved)
docker compose down

# Bring down containers and completely wipe volumes (FRESH RESET)
docker compose down -v
```

---

## 🔒 Production Security Checklist

Before exposing to a public domain or municipal/division network:
1. Set `DEBUG=False` in `.env`.
2. Generate a fresh 50+ character random `SECRET_KEY`.
3. Set your production domain in `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS`:
   ```env
   ALLOWED_HOSTS=eteacher.cesdeped.ph,192.168.1.100,localhost,backend,frontend
   CORS_ALLOWED_ORIGINS=https://eteacher.cesdeped.ph,http://192.168.1.100
   CSRF_TRUSTED_ORIGINS=https://eteacher.cesdeped.ph,http://192.168.1.100
   ```
4. For HTTPS/SSL, either terminate SSL in front of this Docker stack using Cloudflare, Traefik, or an upstream Nginx reverse proxy with Certbot/Let's Encrypt.
