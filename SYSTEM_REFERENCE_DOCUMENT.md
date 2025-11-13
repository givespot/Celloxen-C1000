# CELLOXEN HEALTH PORTAL - SYSTEM REFERENCE DOCUMENT
**Date:** 13 November 2025  
**Server:** 217.154.36.97 (Ubuntu 24)  
**Status:** ✅ PRODUCTION - FULLY OPERATIONAL

---

## 🌐 DOMAIN & SSL

**Primary Domain:** https://celloxen.com  
**Alternative Domain:** https://health.celloxen.com (redirects to celloxen.com)

**SSL Certificates:**
- Location: `/etc/letsencrypt/live/celloxen.com/`
- Certificate: `fullchain.pem`
- Private Key: `privkey.pem`
- Provider: Let's Encrypt
- Auto-renewal: Enabled via certbot

---

## 📁 DIRECTORY STRUCTURE

### Production Directories
```
/var/www/celloxen/          → Symbolic link to frontend
/var/www/celloxen-portal/   → Main working directory
├── backend/                → FastAPI backend application
├── frontend/               → React/HTML frontend (served by Nginx)
├── database/               → SQL schemas and migrations
├── email-system/           → Email service configuration
└── scripts/                → Deployment and maintenance scripts
```

### Backup Directories
```
/var/www/celloxen-portal-new/     → Previous version (NOT ACTIVE)
/var/www/backups/                 → System backups
```

### Important Files
```
Backend Entry:     /var/www/celloxen-portal/backend/simple_auth_main.py
Frontend Entry:    /var/www/celloxen-portal/frontend/index.html
Patient Portal:    /var/www/celloxen-portal/frontend/patient_portal.html
```

---

## ⚙️ NGINX CONFIGURATION

**Config File:** `/etc/nginx/sites-available/celloxen.com`  
**Symlink:** `/etc/nginx/sites-enabled/celloxen.com`

### Current Configuration
```nginx
server {
    listen 80;
    server_name celloxen.com www.celloxen.com;
    return 301 https://celloxen.com$request_uri;
}

server {
    listen 443 ssl http2;
    server_name celloxen.com;
    client_max_body_size 50M;
    
    ssl_certificate /etc/letsencrypt/live/celloxen.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/celloxen.com/privkey.pem;
    
    # Frontend
    location / {
        root /var/www/celloxen;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API Proxy
    location /api {
        proxy_pass http://localhost:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Nginx Commands
```bash
# Test configuration
nginx -t

# Reload without downtime
systemctl reload nginx

# Restart (with brief downtime)
systemctl restart nginx

# View full config
nginx -T

# Check status
systemctl status nginx
```

---

## 🐍 BACKEND SERVICE

**Technology:** FastAPI (Python 3)  
**Port:** 5001  
**Entry Point:** `simple_auth_main.py`

### Current Running Process
```bash
Command: python3 -m uvicorn simple_auth_main:app --host 0.0.0.0 --port 5001 --reload
Process ID: Check with: ps aux | grep uvicorn
Log File: /var/log/celloxen-backend.log
```

### Backend Management Commands
```bash
# Check if backend is running
ps aux | grep uvicorn
netstat -tlnp | grep 5001

# Stop backend
pkill -f "uvicorn.*simple_auth_main"

# Start backend
cd /var/www/celloxen-portal/backend
nohup python3 -m uvicorn simple_auth_main:app --host 0.0.0.0 --port 5001 --reload > /var/log/celloxen-backend.log 2>&1 &

# View backend logs (live)
tail -f /var/log/celloxen-backend.log

# View last 50 lines
tail -50 /var/log/celloxen-backend.log
```

### API Endpoints (Key Routes)
```
Authentication:
POST   /api/v1/auth/login
GET    /api/v1/auth/me

Patients:
GET    /api/v1/clinic/patients
POST   /api/v1/clinic/patients
GET    /api/v1/clinic/patients/{patient_id}
GET    /api/v1/patients/stats/overview

Assessments:
GET    /api/v1/assessments/questions
POST   /api/v1/assessments/comprehensive
GET    /api/v1/assessments/patient/{patient_id}
GET    /api/v1/assessments/{assessment_id}

Appointments:
GET    /api/v1/appointments
POST   /api/v1/appointments
GET    /api/v1/appointments/{appointment_id}

Therapy Plans:
GET    /api/v1/therapy-plans
POST   /api/v1/therapy-plans
GET    /api/v1/therapy-plans/{plan_id}

Reports:
GET    /api/v1/reports/overview
GET    /api/v1/reports/patient-activity
GET    /api/v1/reports/wellness-trends

Health Check:
GET    /health
```

### API Documentation
```
Swagger UI: https://celloxen.com/docs (when logged in via localhost:5001/docs)
OpenAPI JSON: http://localhost:5001/openapi.json
```

---

## 🗄️ DATABASE CONFIGURATION

**Database Type:** PostgreSQL  
**Database Name:** `celloxen_db`  
**Host:** localhost  
**Port:** 5432 (default PostgreSQL port)

### Database Credentials
```
Username: celloxen_user
Password: CelloxenSecure2025
Connection String: postgresql://celloxen_user:CelloxenSecure2025@localhost/celloxen_db
```

**⚠️ SECURITY NOTE:** Credentials are stored in:
- `/var/www/celloxen-portal/DATABASE_CREDENTIALS.txt`
- Backend code uses environment variables or direct connection

### Database Connection from Backend
```python
DATABASE_URL = "postgresql://celloxen_user:CelloxenSecure2025@localhost/celloxen_db"
```

### PostgreSQL Management Commands
```bash
# Connect to database as celloxen_user
psql -U celloxen_user -d celloxen_db -h localhost

# Connect as postgres superuser
sudo -u postgres psql

# List all databases
sudo -u postgres psql -c "\l"

# Backup database
sudo -u postgres pg_dump celloxen_db > /var/www/backups/celloxen_db_backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
sudo -u postgres psql celloxen_db < backup_file.sql

# Check database size
sudo -u postgres psql -c "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) FROM pg_database;"
```

---

## 📊 DATABASE SCHEMA

### Core Tables

**1. Clinics Table**
```sql
Table: clinics
- clinic_id (SERIAL PRIMARY KEY)
- clinic_name (VARCHAR)
- address (TEXT)
- phone (VARCHAR)
- email (VARCHAR)
- status (VARCHAR) - 'active'/'inactive'
- created_at (TIMESTAMP)
```

**2. Users Table (Clinic Staff)**
```sql
Table: users
- user_id (SERIAL PRIMARY KEY)
- clinic_id (INTEGER FK → clinics)
- username (VARCHAR UNIQUE)
- password_hash (VARCHAR)
- email (VARCHAR)
- role (VARCHAR) - 'super_admin'/'clinic_admin'/'practitioner'/'receptionist'
- status (VARCHAR) - 'active'/'inactive'
- created_at (TIMESTAMP)
```

**3. Patients Table**
```sql
Table: patients
- id (SERIAL PRIMARY KEY)
- patient_number (VARCHAR UNIQUE) - Format: CLX-ABD-00001
- clinic_id (INTEGER FK → clinics)
- first_name (VARCHAR)
- last_name (VARCHAR)
- email (VARCHAR)
- mobile_phone (VARCHAR)
- date_of_birth (DATE)
- address (TEXT)
- emergency_contact (VARCHAR)
- emergency_phone (VARCHAR)
- medical_conditions (TEXT)
- medications (TEXT)
- allergies (TEXT)
- insurance_details (TEXT)
- notes (TEXT)
- status (VARCHAR) - 'active'/'invited'/'inactive'
- portal_access (BOOLEAN)
- password_hash (VARCHAR) - For patient portal login
- registration_token (VARCHAR)
- token_expires_at (TIMESTAMP)
- pre_assessment_completed (BOOLEAN)
- created_at (TIMESTAMP)
```

**4. Assessments Table**
```sql
Table: assessments
- assessment_id (SERIAL PRIMARY KEY)
- patient_id (INTEGER FK → patients)
- clinic_id (INTEGER FK → clinics)
- practitioner_id (INTEGER FK → users)
- assessment_type (VARCHAR) - 'comprehensive'/'iridology'/'wellness'
- assessment_date (TIMESTAMP)
- status (VARCHAR) - 'pending'/'in_progress'/'completed'
- wellness_scores (JSONB) - Stores 5 domain scores
- iridology_analysis (JSONB) - AI analysis results
- recommendations (TEXT)
- notes (TEXT)
- created_at (TIMESTAMP)
```

**5. Assessment Responses Table**
```sql
Table: assessment_responses
- response_id (SERIAL PRIMARY KEY)
- assessment_id (INTEGER FK → assessments)
- question_id (INTEGER)
- question_text (TEXT)
- answer_text (TEXT)
- score (INTEGER)
- domain (VARCHAR) - 'diabetic'/'chronic_pain'/'anxiety'/'energy'/'cardiovascular'
```

**6. Appointments Table**
```sql
Table: appointments
- appointment_id (SERIAL PRIMARY KEY)
- patient_id (INTEGER FK → patients)
- clinic_id (INTEGER FK → clinics)
- practitioner_id (INTEGER FK → users)
- appointment_date (DATE)
- appointment_time (TIME)
- duration_minutes (INTEGER)
- appointment_type (VARCHAR)
- status (VARCHAR) - 'scheduled'/'completed'/'cancelled'/'no_show'
- notes (TEXT)
- created_at (TIMESTAMP)
```

**7. Therapy Plans Table**
```sql
Table: therapy_plans
- plan_id (SERIAL PRIMARY KEY)
- patient_id (INTEGER FK → patients)
- assessment_id (INTEGER FK → assessments)
- clinic_id (INTEGER FK → clinics)
- practitioner_id (INTEGER FK → users)
- therapy_type (VARCHAR) - 'C-102 Metabolic Balance'/'C-103 Pain Relief'/etc
- sessions_total (INTEGER)
- sessions_completed (INTEGER)
- status (VARCHAR) - 'active'/'completed'/'paused'/'cancelled'
- priority (VARCHAR) - 'urgent'/'high'/'normal'/'low'
- start_date (DATE)
- end_date (DATE)
- notes (TEXT)
- created_at (TIMESTAMP)
```

**8. Chatbot Sessions Table**
```sql
Table: chatbot_sessions
- session_id (SERIAL PRIMARY KEY)
- patient_id (INTEGER FK → patients)
- practitioner_id (INTEGER FK → users)
- assessment_id (INTEGER FK → assessments)
- conversation_stage (VARCHAR) - 'greeting'/'contraindications'/'followup'/'iridology'
- session_status (VARCHAR) - 'active'/'completed'
- questions_total (INTEGER)
- questions_asked (INTEGER)
- created_at (TIMESTAMP)
```

**9. Chatbot Messages Table**
```sql
Table: chatbot_messages
- message_id (SERIAL PRIMARY KEY)
- session_id (INTEGER FK → chatbot_sessions)
- role (VARCHAR) - 'user'/'assistant'
- content (TEXT)
- message_type (VARCHAR) - 'question'/'answer'/'instruction'
- metadata (JSONB)
- created_at (TIMESTAMP)
```

### Database Statistics (Current)
```
Total Patients: 11
Active Patients: 11
Total Assessments: 18
Total Appointments: 1
Total Therapy Plans: 6
Total Clinics: 1 (Aberdeen Wellness Centre)
Total Users: ~5 clinic staff members
```

---

## 📧 EMAIL CONFIGURATION

**Email Provider:** IONOS Mail (UK)  
**SMTP Server:** smtp.ionos.co.uk  
**Port:** 587 (STARTTLS)

### Email Credentials
```
Sender Email: health@celloxen.com
SMTP Username: health@celloxen.com
SMTP Password: Welshdalehealth2024
```

### Email Service Files
```
Config: /var/www/celloxen-portal/email-system/config.py
Templates: /var/www/celloxen-portal/email-system/email_templates.py
Sender: /var/www/celloxen-portal/email-system/email_sender.py
```

### Email Templates Available
1. Patient Registration Invitation
2. Health Assessment Report
3. Appointment Confirmation
4. Appointment Reminder
5. Therapy Plan Summary

### Test Email Command
```bash
cd /var/www/celloxen-portal/email-system
python3 test_health_email.py
```

---

## 🔐 SECURITY & AUTHENTICATION

### Password Hashing
- **Algorithm:** bcrypt
- **Library:** `bcrypt` Python package
- **Rounds:** 12 (default)

### JWT Tokens (Patient Portal)
- **Secret Key:** Stored in backend environment
- **Token Expiry:** 7 days
- **Algorithm:** HS256

### User Roles
```
1. super_admin    - Full system access across all clinics
2. clinic_admin   - Full access within assigned clinic
3. practitioner   - Assessment, therapy plans, appointments
4. receptionist   - Patient registration, appointments only
```

### Login Credentials (Clinic Portal)
```
Default Admin:
Username: admin
Password: [Set during installation]
Clinic: Aberdeen Wellness Centre
```

---

## 🔄 BACKUP PROCEDURES

### Automatic Backups
- **Location:** `/var/www/backups/`
- **Frequency:** Manual (recommended: daily)

### Manual Backup Commands

**Full System Backup:**
```bash
# Create backup directory
mkdir -p /var/www/backups/backup_$(date +%Y%m%d_%H%M%S)

# Backup application files
cd /var/www
tar -czf backups/celloxen_portal_$(date +%Y%m%d_%H%M%S).tar.gz celloxen-portal/

# Backup database
sudo -u postgres pg_dump celloxen_db > /var/www/backups/celloxen_db_$(date +%Y%m%d_%H%M%S).sql

# Backup Nginx config
cp /etc/nginx/sites-available/celloxen.com /var/www/backups/nginx_celloxen_$(date +%Y%m%d_%H%M%S).conf
```

**Restore from Backup:**
```bash
# Restore application files
cd /var/www
tar -xzf backups/celloxen_portal_YYYYMMDD_HHMMSS.tar.gz

# Restore database
sudo -u postgres psql celloxen_db < /var/www/backups/celloxen_db_YYYYMMDD_HHMMSS.sql

# Restore Nginx config
cp /var/www/backups/nginx_celloxen_YYYYMMDD_HHMMSS.conf /etc/nginx/sites-available/celloxen.com
nginx -t && systemctl reload nginx
```

---

## 🔍 TROUBLESHOOTING COMMANDS

### Check All Services Status
```bash
# Backend running?
ps aux | grep uvicorn
netstat -tlnp | grep 5001

# Nginx running?
systemctl status nginx

# PostgreSQL running?
systemctl status postgresql

# Check logs
tail -f /var/log/celloxen-backend.log
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### Common Issues & Solutions

**Issue: 502 Bad Gateway**
```bash
# Check if backend is running
ps aux | grep uvicorn

# Check Nginx is proxying to correct port
grep "proxy_pass" /etc/nginx/sites-available/celloxen.com

# Should show: proxy_pass http://localhost:5001;
```

**Issue: Database Connection Failed**
```bash
# Test database connection
psql -U celloxen_user -d celloxen_db -h localhost

# Check PostgreSQL is running
systemctl status postgresql

# Restart PostgreSQL if needed
sudo systemctl restart postgresql
```

**Issue: Frontend Not Loading**
```bash
# Check symbolic link
ls -la /var/www/celloxen

# Should show: /var/www/celloxen -> /var/www/celloxen-portal/frontend

# Check Nginx config
nginx -t
```

### Emergency Restart Procedure
```bash
# 1. Stop backend
pkill -f "uvicorn.*simple_auth_main"

# 2. Restart PostgreSQL
sudo systemctl restart postgresql

# 3. Start backend
cd /var/www/celloxen-portal/backend
nohup python3 -m uvicorn simple_auth_main:app --host 0.0.0.0 --port 5001 --reload > /var/log/celloxen-backend.log 2>&1 &

# 4. Restart Nginx
systemctl restart nginx

# 5. Verify all services
ps aux | grep uvicorn
systemctl status nginx
systemctl status postgresql
```

---

## 📦 DEPENDENCIES

### Python Packages (Backend)
```
fastapi==0.104.1
uvicorn==0.24.0
psycopg2-binary==2.9.9
bcrypt==4.1.1
python-jose==3.3.0
python-multipart==0.0.6
asyncpg==0.29.0
aiosmtplib==3.0.1
anthropic==0.7.8 (for AI features)
```

### Frontend Libraries
```
React 18 (via Babel standalone)
Lucide Icons
Recharts (for analytics charts)
```

### System Requirements
```
OS: Ubuntu 24.04 LTS
Python: 3.10+
PostgreSQL: 14+
Nginx: 1.24+
Node.js: Not required (using Babel in browser)
```

---

## 🌍 GITHUB REPOSITORY

**Repository:** https://github.com/givespot/cell_portal_fnal  
**Branch:** main  
**Status:** Private

### Git Commands for Updates
```bash
cd /var/www/celloxen-portal

# Check status
git status

# Add all changes
git add .

# Commit with message
git commit -m "Description of changes"

# Push to GitHub
git push origin main

# Pull latest changes
git pull origin main
```

---

## 📞 SUPPORT CONTACTS

**Server Provider:** [Your hosting provider]  
**Domain Registrar:** [Your domain registrar]  
**SSL Certificate:** Let's Encrypt (auto-renews)  
**Email Provider:** IONOS Mail

---

## 📝 QUICK REFERENCE CHECKLIST

### Daily Health Check
- [ ] Backend running on port 5001
- [ ] Nginx responding to requests
- [ ] PostgreSQL accepting connections
- [ ] No errors in `/var/log/celloxen-backend.log`
- [ ] SSL certificate valid (check https://celloxen.com)

### Weekly Maintenance
- [ ] Review backend logs for errors
- [ ] Check database size
- [ ] Create backup of database
- [ ] Check disk space: `df -h`
- [ ] Review Nginx access logs for unusual activity

### Monthly Tasks
- [ ] Full system backup (files + database)
- [ ] Update Python dependencies if needed
- [ ] Review user accounts and remove inactive
- [ ] Check SSL certificate expiry date

---

## 🚀 DEPLOYMENT WORKFLOW

### For Code Changes
```bash
# 1. Make changes locally or via SSH
cd /var/www/celloxen-portal

# 2. Test changes (if backend)
cd backend
python3 -m pytest  # if you have tests

# 3. Restart backend to apply changes
pkill -f "uvicorn.*simple_auth_main"
nohup python3 -m uvicorn simple_auth_main:app --host 0.0.0.0 --port 5001 --reload > /var/log/celloxen-backend.log 2>&1 &

# 4. For frontend changes, just refresh browser (Nginx serves static files)

# 5. Commit and push to GitHub
git add .
git commit -m "Description"
git push origin main
```

### For Database Schema Changes
```bash
# 1. Create SQL migration file
nano /var/www/celloxen-portal/database/migrations/migration_$(date +%Y%m%d_%H%M%S).sql

# 2. Apply migration
psql -U celloxen_user -d celloxen_db -h localhost -f migration_file.sql

# 3. Backup database after migration
sudo -u postgres pg_dump celloxen_db > /var/www/backups/post_migration_backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## ⚠️ IMPORTANT NOTES

1. **Never edit files directly in `/var/www/celloxen/`** - This is a symbolic link. Always work in `/var/www/celloxen-portal/`

2. **Backend auto-reloads** - When running with `--reload` flag, code changes are detected automatically

3. **Database credentials** - Stored in plain text. Consider using environment variables for production

4. **Port 5001** - Ensure this port is not blocked by firewall and only accessible via Nginx proxy

5. **Other applications on server:**
   - TweedPet: Port 5002
   - Immigration Portal: Port 5003
   - These must not be disrupted

6. **GitHub token** - Personal access token stored locally for pushes (expires periodically)

---

**Document Created:** 13 November 2025  
**Last Updated:** 13 November 2025  
**Document Version:** 1.0  
**System Status:** ✅ OPERATIONAL

---

*Keep this document updated when making configuration changes*
