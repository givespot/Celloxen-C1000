# CELLOXEN HEALTH PORTAL - COMPREHENSIVE TECHNICAL DOCUMENTATION
## Version: Clean Restore Point - 30 November 2025

---

# TABLE OF CONTENTS

1. [System Overview](#1-system-overview)
2. [Server Infrastructure](#2-server-infrastructure)
3. [File Structure](#3-file-structure)
4. [Database Architecture](#4-database-architecture)
5. [API Endpoints Reference](#5-api-endpoints-reference)
6. [Frontend Architecture](#6-frontend-architecture)
7. [Authentication & Security](#7-authentication--security)
8. [Module Documentation](#8-module-documentation)
9. [Nginx Configuration](#9-nginx-configuration)
10. [Troubleshooting Guide](#10-troubleshooting-guide)
11. [Backup & Restore Procedures](#11-backup--restore-procedures)
12. [Development Guidelines](#12-development-guidelines)
13. [Common Issues & Solutions](#13-common-issues--solutions)

---

# 1. SYSTEM OVERVIEW

## 1.1 Purpose
Celloxen Health Portal is a comprehensive multi-tenant wellness clinic management platform providing:
- AI-powered iridology analysis
- Holistic health assessments
- Patient management
- Appointment scheduling
- Therapy session tracking
- Invoicing and billing
- Multi-portal access (Super Admin, Clinic Admin, Patient)

## 1.2 Technology Stack
| Component | Technology | Version |
|-----------|------------|---------|
| Backend | FastAPI (Python) | 3.12 |
| Frontend | React (CDN) | 18.x |
| Database | PostgreSQL | 14+ |
| Web Server | Nginx | Latest |
| Process Manager | Uvicorn | Latest |
| OS | Ubuntu | 24.04 |
| SSL | Let's Encrypt | Auto-renewed |

## 1.3 Live URLs
| Portal | URL |
|--------|-----|
| Clinic Portal | https://celloxen.com |
| Super Admin | https://celloxen.com/super-admin/ |
| Patient Portal | https://celloxen.com/patient-portal.html |
| API Health Check | https://celloxen.com/health |

## 1.4 File Sizes (Current)
| File | Size | Lines |
|------|------|-------|
| Backend (simple_auth_main.py) | 203 KB | 5,453 |
| Frontend (index.html) | 430 KB | 7,164 |
| Database Dump | 3.4 MB | - |

---

# 2. SERVER INFRASTRUCTURE

## 2.1 Server Details
```
Hostname: sharp-bouman.217-154-36-97.plesk.page
Provider: IONOS
OS: Linux 6.8.0-85-generic Ubuntu
Architecture: x86_64
```

## 2.2 Directory Structure
```
/var/www/
├── simple_auth_main.py          # MAIN BACKEND FILE (207KB)
├── Celloxen-C1000/              # MAIN PROJECT DIRECTORY
│   ├── frontend/                # All HTML/JS/CSS files
│   │   ├── index.html           # Main clinic portal (430KB)
│   │   ├── patient-portal.html  # Patient portal
│   │   ├── super_admin_portal.html
│   │   ├── iridology_report.html
│   │   ├── uploads/             # User uploads
│   │   │   └── therapy_diagrams/
│   │   └── ... other HTML files
│   ├── backend/                 # Python modules
│   │   ├── simple_auth_main.py  # Copy of main backend
│   │   ├── iridology_analyzer.py
│   │   ├── pdf_report_generator.py
│   │   ├── super_admin_endpoints.py
│   │   └── ... other modules
│   ├── docs/                    # Documentation
│   ├── nginx/                   # Nginx configs
│   ├── scripts/                 # Utility scripts
│   └── backups/                 # Internal backups
├── backups/                     # MAIN BACKUP DIRECTORY
│   └── RESTORE_POINT_20251130_063213/
└── welshdale/                   # Separate project (port 5010)
```

## 2.3 Running Processes
| Service | Port | Command |
|---------|------|---------|
| Celloxen Backend | 5001 | `python3 -m uvicorn simple_auth_main:app --host 0.0.0.0 --port 5001` |
| Welshdale Backend | 5010 | Separate virtualenv |
| Nginx | 80/443 | System service |
| PostgreSQL | 5432 | System service |

## 2.4 Service Management Commands
```bash
# Start Backend
cd /var/www && nohup python3 -m uvicorn simple_auth_main:app --host 0.0.0.0 --port 5001 > /var/log/celloxen-backend.log 2>&1 &

# Stop Backend
pkill -9 -f "uvicorn.*simple_auth_main"

# Restart Backend
pkill -9 -f "uvicorn.*simple_auth_main" && sleep 2 && cd /var/www && nohup python3 -m uvicorn simple_auth_main:app --host 0.0.0.0 --port 5001 > /var/log/celloxen-backend.log 2>&1 &

# Check Backend Status
ps aux | grep uvicorn | grep -v grep
netstat -tlnp | grep 5001

# View Backend Logs
tail -f /var/log/celloxen-backend.log

# Nginx Commands
sudo systemctl restart nginx
sudo systemctl status nginx
sudo nginx -t  # Test config

# PostgreSQL Commands
sudo systemctl status postgresql
sudo -u postgres psql -d celloxen_portal
```

---

# 3. FILE STRUCTURE

## 3.1 Critical Files
| File | Location | Purpose |
|------|----------|---------|
| simple_auth_main.py | /var/www/ | Main backend API (93 endpoints) |
| index.html | /var/www/Celloxen-C1000/frontend/ | Main clinic portal |
| .env | /var/www/Celloxen-C1000/backend/ | Environment variables |
| celloxen.com | /etc/nginx/sites-enabled/ | Nginx config |

## 3.2 Backend Modules
```
/var/www/Celloxen-C1000/backend/
├── simple_auth_main.py       # Main API (all endpoints)
├── ai_assessment_analyzer.py # AI assessment logic
├── ai_iridology_analyzer.py  # AI iridology logic
├── ai_iridology_module.py    # Iridology helpers
├── ai_response_handler.py    # AI response formatting
├── iridology_analyzer.py     # Core iridology analysis
├── iridology_pdf_generator.py # PDF report generation
├── pdf_report_generator.py   # General PDF reports
├── super_admin_endpoints.py  # Super admin routes
├── super_admin_auth.py       # Super admin authentication
├── email_config.py           # Email configuration
├── email_service.py          # Email sending
├── email_templates.py        # Email templates
└── simple_assessment_api.py  # Assessment API
```

## 3.3 Frontend Files
```
/var/www/Celloxen-C1000/frontend/
├── index.html                    # Main clinic portal
├── patient-portal.html           # Patient self-service
├── super_admin_portal.html       # Super admin dashboard
├── super_admin_clinic_details.html
├── super_admin_invoices.html
├── super_admin_invoice_view.html
├── super_admin_settings.html
├── super_admin_reports.html
├── super_admin_audit_logs.html
├── iridology_report.html         # Iridology results
├── clinic_invoice_view.html      # Invoice view
├── admin.html                    # Admin panel
└── uploads/
    └── therapy_diagrams/         # Therapy placement images
```

---

# 4. DATABASE ARCHITECTURE

## 4.1 Connection Details
```
Host: localhost
Port: 5432
Database: celloxen_portal
User: celloxen_user
Password: [stored in .env]
```

## 4.2 Database Tables (44 Total)
### Core Tables
| Table | Purpose | Key Fields |
|-------|---------|------------|
| clinics | Multi-tenant clinics | id, name, clinic_code, email |
| users | System users | id, email, role, clinic_id |
| patients | Patient records | id, clinic_id, first_name, last_name |
| appointments | Scheduling | id, clinic_id, patient_id, date_time |
| assessments | Health assessments | id, patient_id, assessment_type |

### Iridology Tables
| Table | Purpose |
|-------|---------|
| iridology_analyses | Main analysis records |
| iridology_findings | Analysis findings |
| iridology_body_systems | Body system mappings |
| iridology_capture_sessions | Image capture sessions |
| iridology_gp_referrals | GP referral data |
| iridology_therapy_recommendations | Therapy suggestions |
| iridology_wellness_recommendations | Wellness advice |
| iris_findings | Raw iris findings |

### Therapy Tables
| Table | Purpose |
|-------|---------|
| therapies | Therapy definitions (C-102 to C-108) |
| therapy_plans | Patient therapy plans |
| therapy_sessions | Individual sessions |
| therapy_plan_items | Plan line items |
| therapy_correlations | Assessment correlations |

### Billing Tables
| Table | Purpose |
|-------|---------|
| patient_invoices | Patient billing |
| clinic_invoices | Clinic billing |

### Settings Tables
| Table | Purpose |
|-------|---------|
| opening_hours | Clinic hours (by day_of_week) |
| notification_settings | Notification preferences |

### Admin Tables
| Table | Purpose |
|-------|---------|
| super_admins | Super admin users |
| super_admin_audit_log | Admin activity log |
| clinic_credentials | API credentials |
| system_configuration | System settings |

## 4.3 Key Relationships
```
clinics (1) ─────────────────────────────── (N) users
clinics (1) ─────────────────────────────── (N) patients
clinics (1) ─────────────────────────────── (N) appointments
clinics (1) ─────────────────────────────── (N) opening_hours
patients (1) ────────────────────────────── (N) assessments
patients (1) ────────────────────────────── (N) therapy_plans
patients (1) ────────────────────────────── (N) iridology_analyses
patients (1) ────────────────────────────── (N) patient_invoices
therapy_plans (1) ───────────────────────── (N) therapy_sessions
```

## 4.4 Database Commands
```bash
# Connect to database
sudo -u postgres psql -d celloxen_portal

# List all tables
\dt

# Describe table structure
\d table_name

# Export database
sudo -u postgres pg_dump celloxen_portal > backup.sql

# Import database
sudo -u postgres psql -d celloxen_portal < backup.sql

# Check table counts
SELECT 'patients' as table_name, COUNT(*) FROM patients
UNION ALL
SELECT 'appointments', COUNT(*) FROM appointments
UNION ALL
SELECT 'assessments', COUNT(*) FROM assessments;
```

## 4.5 Important Column Details

### clinics Table - Notification Columns
```sql
email_appointment_reminders BOOLEAN DEFAULT true
email_appointment_confirmations BOOLEAN DEFAULT true
email_new_patient_alerts BOOLEAN DEFAULT true
email_invoice_notifications BOOLEAN DEFAULT true
email_marketing BOOLEAN DEFAULT false
```

### opening_hours Table
```sql
id, clinic_id, day_of_week (0-6), is_open, open_time, close_time
-- 0 = Sunday, 6 = Saturday
```

### therapies Table
```sql
id, therapy_code, therapy_name, subtitle, description,
recommended_sessions, session_frequency, session_duration,
applicator_placement, target_organs, is_active, diagram_image
```

---

# 5. API ENDPOINTS REFERENCE

## 5.1 Total Endpoints: 93

## 5.2 Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/login | User login, returns JWT |
| GET | /api/v1/auth/me | Get current user |
| GET | /api/v1/me | Get current user profile |

## 5.3 Patients
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/clinic/patients | List all patients |
| GET | /api/v1/clinic/patients/{id} | Get patient details |
| POST | /api/v1/clinic/patients | Create patient |
| PUT | /api/v1/clinic/patients/{id} | Update patient |
| DELETE | /api/v1/clinic/patients/{id} | Delete patient |
| GET | /api/v1/patients/stats/overview | Patient statistics |

## 5.4 Appointments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/appointments | List appointments |
| POST | /api/v1/appointments | Create appointment |
| GET | /api/v1/appointments/{id} | Get appointment |
| PUT | /api/v1/appointments/{id} | Update appointment |
| DELETE | /api/v1/appointments/{id} | Delete appointment |
| POST | /api/v1/appointments/{id}/cancel | Cancel appointment |
| POST | /api/v1/appointments/{id}/confirm | Confirm appointment |
| POST | /api/v1/appointments/{id}/decline | Decline appointment |
| GET | /api/v1/appointments/stats | Appointment stats |
| GET | /api/v1/appointments/calendar/{year}/{month} | Calendar view |

## 5.5 Assessments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/assessments/questions | Get all questions |
| GET | /api/v1/assessments/questions/{domain} | Get domain questions |
| POST | /api/v1/assessments/comprehensive | Create assessment |
| GET | /api/v1/assessments/patient/{patient_id} | Get patient assessments |
| GET | /api/v1/assessments/{id} | Get assessment details |
| GET | /api/v1/assessments/{id}/complete | Get complete assessment |
| GET | /api/v1/assessments/{id}/report | Get assessment report |
| GET | /api/v1/patients/{patient_id}/assessment-overview | Assessment overview |
| GET | /api/v1/assessments/patient/{patient_id}/dashboard | Assessment dashboard |

## 5.6 Iridology
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/iridology/start | Start analysis |
| POST | /api/v1/iridology/{id}/upload-images | Upload iris images |
| POST | /api/v1/iridology/{id}/analyse | Run AI analysis |
| GET | /api/v1/iridology/{id}/results | Get results |
| GET | /api/v1/iridology/{id}/report | Get detailed report |
| GET | /api/v1/iridology/{id}/download-pdf | Download PDF report |
| GET | /api/v1/iridology/recent | Recent analyses |
| POST | /api/v1/assessments/{id}/iridology | Add iridology to assessment |

## 5.7 Therapies
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/therapies | List all therapies |
| GET | /api/v1/therapies/stats | Therapy statistics |
| GET | /api/v1/therapies/active-plans | Active therapy plans |
| GET | /api/v1/therapies/today-sessions | Today's sessions |
| GET | /api/v1/therapy-module/stats | Module stats |
| GET | /api/v1/therapy-plans | List therapy plans |
| GET | /api/v1/therapy-plans/{id} | Get plan details |
| POST | /api/v1/therapy-plans | Create plan |
| PUT | /api/v1/therapy-plans/{id}/status | Update status |
| GET | /api/v1/patients/{id}/therapy-assignments | Patient assignments |
| POST | /api/v1/patients/{id}/therapy-assignments | Assign therapy |
| GET | /api/v1/therapy-assignments/{id}/sessions | Get sessions |
| POST | /api/v1/therapy-sessions/{id}/complete | Complete session |
| GET | /api/v1/therapy-items/{id}/sessions | Get item sessions |
| POST | /api/v1/therapy-items/{id}/create-appointments | Create appointments |
| POST | /api/v1/therapy-sessions/{id}/reschedule | Reschedule session |
| POST | /api/v1/therapies/{code}/upload-diagram | Upload diagram |
| DELETE | /api/v1/therapies/{code}/diagram | Delete diagram |

## 5.8 Patient Invoices
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/patient-invoices | List invoices |
| GET | /api/v1/patient-invoices/{id} | Get invoice |
| POST | /api/v1/patient-invoices | Create invoice |
| PUT | /api/v1/patient-invoices/{id} | Update invoice |
| DELETE | /api/v1/patient-invoices/{id} | Delete invoice |
| PUT | /api/v1/patient-invoices/{id}/mark-paid | Mark as paid |
| GET | /api/v1/clinic/patient-invoices/v2 | List invoices (v2) |

## 5.9 Settings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/clinic/settings | Get all settings |
| PATCH | /api/v1/clinic/settings/profile | Update profile |
| PATCH | /api/v1/clinic/settings/hours | Update hours |
| PATCH | /api/v1/clinic/settings/password | Change password |
| PATCH | /api/v1/clinic/settings/notifications | Update notifications |

## 5.10 Super Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/superadmin/stats | Dashboard stats |
| GET | /api/v1/superadmin/clinics | List all clinics |
| POST | /api/v1/superadmin/clinics | Create clinic |
| POST | /api/v1/superadmin/clinics/{id}/activate | Activate clinic |
| POST | /api/v1/superadmin/clinics/{id}/deactivate | Deactivate clinic |
| DELETE | /api/v1/superadmin/clinics/{id} | Delete clinic |

## 5.11 Patient Portal
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/patient/available-slots | Get booking slots |
| POST | /api/v1/patient/book-appointment | Book appointment |
| DELETE | /api/v1/patient/appointments/{id} | Cancel booking |

## 5.12 Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/reports/overview | Overview stats |
| GET | /api/v1/reports/patient-activity | Patient activity |
| GET | /api/v1/reports/wellness-trends | Wellness trends |
| POST | /api/v1/reports/generate/{id} | Generate PDF |
| GET | /reports/{filename} | Download report |

## 5.13 Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/clinic/dashboard | Dashboard data |
| GET | /health | Health check |

---

# 6. FRONTEND ARCHITECTURE

## 6.1 Technology
- **Framework**: React 18 (loaded via CDN)
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Charts**: Recharts (for dashboard)
- **Date Handling**: Native JavaScript
- **State Management**: React useState/useEffect

## 6.2 Single-Page Application Structure
The main `index.html` contains all modules as React components:
```javascript
// Main Modules (in order of appearance)
- LoginPage           // Authentication
- Dashboard           // Overview stats
- PatientsModule      // Patient management
- AssessmentsModule   // Health assessments
- IridologyModule     // Iris analysis
- AppointmentsModule  // Scheduling
- TherapiesModule     // Therapy management
- PatientInvoicesModule // Billing
- SettingsModule      // Clinic settings
```

## 6.3 Authentication Flow
```
1. User enters credentials on LoginPage
2. POST /api/v1/auth/login
3. Receive JWT token
4. Store token in localStorage (celloxen_token)
5. All subsequent API calls include: Authorization: Bearer {token}
6. Token expires in 30 minutes (1800 seconds)
```

## 6.4 Module State Pattern
Each module follows this pattern:
```javascript
const ModuleName = () => {
    // State
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState([]);
    const [error, setError] = useState(null);
    
    // Fetch data on mount
    useEffect(() => {
        fetchData();
    }, []);
    
    // API call function
    const fetchData = async () => {
        try {
            const response = await fetch('/api/v1/endpoint', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('celloxen_token')}` }
            });
            const result = await response.json();
            setData(result.data);
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };
    
    // Render
    return (/* JSX */);
};
```

## 6.5 Key UI Components
- **Navigation**: Sidebar with icons for each module
- **Stats Cards**: Dashboard statistics display
- **Data Tables**: Patient lists, appointments, invoices
- **Modals**: Create/Edit/Delete confirmations
- **Forms**: Patient registration, appointment booking
- **Charts**: Recharts for analytics

---

# 7. AUTHENTICATION & SECURITY

## 7.1 JWT Token Structure
```json
{
  "sub": "user_id",
  "clinic_id": 4,
  "email": "user@example.com",
  "exp": 1764485926
}
```

## 7.2 Token Configuration
```python
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

## 7.3 Multi-Tenant Security
- All database queries filter by `clinic_id`
- `clinic_id` extracted from JWT token, NOT from request
- Super Admin has separate authentication system
- Patient portal has restricted access to own data only

## 7.4 Password Hashing
```python
import bcrypt
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
bcrypt.checkpw(password.encode('utf-8'), stored_hash)
```

## 7.5 CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

# 8. MODULE DOCUMENTATION

## 8.1 Dashboard Module
**Features:**
- Total patients count
- Today's appointments
- Active therapy plans
- Pending invoices
- Recent activity feed
- Quick actions

**Endpoints Used:**
- GET /api/v1/clinic/dashboard
- GET /api/v1/appointments/stats
- GET /api/v1/therapy-plans/stats

## 8.2 Patients Module
**Features:**
- Patient list with search
- Patient profile view/edit
- Medical history
- Assessment history
- Therapy history
- Invoice history

**Key Fields:**
- patient_number (auto-generated: PAT-{clinic_id}-{sequence})
- first_name, last_name
- date_of_birth
- email, phone
- address fields
- medical notes

## 8.3 Assessments Module
**Features:**
- Comprehensive health questionnaire
- AI-powered analysis
- Domain-based scoring
- PDF report generation
- Historical comparison

**Domains:**
- Energy & Vitality
- Digestive Health
- Mental Wellbeing
- Sleep Quality
- Joint & Mobility
- Cardiovascular
- Metabolic Health

## 8.4 Iridology Module
**Features:**
- Iris image capture/upload
- Left and right eye analysis
- AI-powered interpretation (Anthropic API)
- Body system correlations
- Wellness recommendations
- PDF report with images
- GP referral suggestions

**Process Flow:**
1. Start new analysis (POST /api/v1/iridology/start)
2. Upload images (POST /api/v1/iridology/{id}/upload-images)
3. Run AI analysis (POST /api/v1/iridology/{id}/analyse)
4. View results (GET /api/v1/iridology/{id}/results)
5. Download PDF (GET /api/v1/iridology/{id}/download-pdf)

## 8.5 Appointments Module
**Features:**
- Calendar view (month/week/day)
- Appointment creation
- Status management (scheduled, confirmed, completed, cancelled)
- Conflict detection
- Integration with therapy sessions

**Appointment Types:**
- Consultation
- Assessment
- Therapy Session
- Follow-up
- Iridology Analysis

## 8.6 Therapies Module
**Features:**
- 4 tabs: Active Plans, Assign New, Library, Today's Schedule
- 5 pre-configured therapies (C-102 to C-108)
- Session tracking and progress
- Diagram image upload
- Appointment creation from sessions
- Reschedule functionality

**Available Therapies:**
| Code | Name |
|------|------|
| C-102 | Vitality & Energy Support |
| C-104 | Comfort & Mobility Support |
| C-105 | Circulation & Heart Wellness |
| C-107 | Stress & Relaxation Support |
| C-108 | Metabolic Balance Support |

## 8.7 Patient Invoices Module
**Features:**
- Invoice creation
- Status tracking (pending, paid, overdue, cancelled)
- Payment recording
- PDF generation
- Patient linking

**Invoice Fields:**
- invoice_number (auto: PI-{clinic_id}-{year}-{sequence})
- patient_id
- amount
- description
- service_date, due_date
- status
- payment_method
- notes

## 8.8 Settings Module
**Tabs:**
1. **Clinic Profile**: Name, address, contact details
2. **Opening Hours**: Day-by-day schedule (uses opening_hours table)
3. **Security**: Password change
4. **Notifications**: Email preferences (uses clinic columns)

---

# 9. NGINX CONFIGURATION

## 9.1 Main Configuration Location
`/etc/nginx/sites-enabled/celloxen.com`

## 9.2 Key Locations
```nginx
# Main frontend
root /var/www/Celloxen-C1000/frontend;

# API proxy
location /api/ {
    proxy_pass http://127.0.0.1:5001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# Super Admin portal
location /super-admin/ {
    alias /var/www/Celloxen-C1000/frontend/;
    try_files /super_admin_portal.html =404;
}

# Reports
location /reports/ {
    alias /var/www/Celloxen-C1000/reports/;
}

# Uploads
location /uploads/ {
    alias /var/www/Celloxen-C1000/frontend/uploads/;
}
```

## 9.3 SSL Configuration
```nginx
ssl_certificate /etc/letsencrypt/live/celloxen.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/celloxen.com/privkey.pem;
```

## 9.4 Common Nginx Commands
```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# Restart nginx
sudo systemctl restart nginx

# View error logs
tail -f /var/log/nginx/error.log

# View access logs
tail -f /var/log/nginx/access.log
```

---

# 10. TROUBLESHOOTING GUIDE

## 10.1 Backend Not Starting

**Symptom:** Port 5001 not responding
```bash
# Check if process running
ps aux | grep uvicorn

# Check port usage
netstat -tlnp | grep 5001

# Force kill and restart
pkill -9 -f uvicorn
cd /var/www && nohup python3 -m uvicorn simple_auth_main:app --host 0.0.0.0 --port 5001 > /var/log/celloxen-backend.log 2>&1 &
```

**Symptom:** "Address already in use"
```bash
fuser -k 5001/tcp
sleep 2
# Then restart backend
```

## 10.2 Backend Crashes on Start

**Check for syntax errors:**
```bash
cd /var/www && python3 -c "import simple_auth_main"
```

**Check logs:**
```bash
tail -50 /var/log/celloxen-backend.log
```

## 10.3 Database Connection Issues

**Check PostgreSQL:**
```bash
sudo systemctl status postgresql
sudo -u postgres psql -d celloxen_portal -c "SELECT 1"
```

**Check credentials:**
```bash
cat /var/www/Celloxen-C1000/backend/.env
```

## 10.4 404 Errors on API

**Possible causes:**
1. Backend not running
2. Nginx not proxying correctly
3. Endpoint doesn't exist

**Debug steps:**
```bash
# Test API directly (bypassing nginx)
curl http://localhost:5001/health

# Test through nginx
curl https://celloxen.com/health

# Check nginx error log
tail -20 /var/log/nginx/error.log
```

## 10.5 500 Internal Server Errors

**Check backend log immediately:**
```bash
tail -100 /var/log/celloxen-backend.log | grep -A5 ERROR
```

**Common causes:**
- Database column mismatch
- Missing table/column
- JSON parsing error
- Authentication failure

## 10.6 Frontend Not Loading

**Check nginx:**
```bash
sudo nginx -t
sudo systemctl status nginx
```

**Check file permissions:**
```bash
ls -la /var/www/Celloxen-C1000/frontend/index.html
```

## 10.7 Authentication Issues

**Token expired:**
- User needs to re-login
- Token expires after 30 minutes

**Invalid token:**
```bash
# Decode JWT to check (online or python)
import jwt
jwt.decode(token, options={"verify_signature": False})
```

## 10.8 Slow Performance

**Check system resources:**
```bash
top
free -h
df -h
```

**Check database:**
```bash
sudo -u postgres psql -d celloxen_portal -c "SELECT COUNT(*) FROM patients;"
```

---

# 11. BACKUP & RESTORE PROCEDURES

## 11.1 Current Backup Location
```
/var/www/backups/RESTORE_POINT_20251130_063213/
├── simple_auth_main.py        # Backend (207KB)
├── celloxen_portal_database.sql  # Database (3.4MB)
└── Celloxen-C1000/            # Complete project
```

## 11.2 Create New Backup
```bash
# Create backup directory
BACKUP_DIR="/var/www/backups/RESTORE_POINT_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup backend
cp /var/www/simple_auth_main.py $BACKUP_DIR/

# Backup frontend
cp -r /var/www/Celloxen-C1000 $BACKUP_DIR/

# Backup database
sudo -u postgres pg_dump celloxen_portal > $BACKUP_DIR/celloxen_portal_database.sql

echo "Backup created at: $BACKUP_DIR"
```

## 11.3 Restore Backend
```bash
# Stop current backend
pkill -9 -f uvicorn

# Restore file
cp /var/www/backups/RESTORE_POINT_20251130_063213/simple_auth_main.py /var/www/

# Restart backend
cd /var/www && nohup python3 -m uvicorn simple_auth_main:app --host 0.0.0.0 --port 5001 > /var/log/celloxen-backend.log 2>&1 &
```

## 11.4 Restore Database
```bash
# WARNING: This will overwrite all data!
sudo -u postgres psql -d celloxen_portal < /var/www/backups/RESTORE_POINT_20251130_063213/celloxen_portal_database.sql
```

## 11.5 Restore Frontend
```bash
cp -r /var/www/backups/RESTORE_POINT_20251130_063213/Celloxen-C1000/frontend/* /var/www/Celloxen-C1000/frontend/
```

## 11.6 GitHub Backup
```bash
cd /var/www/Celloxen-C1000
git add -A
git commit -m "Backup: $(date +%Y-%m-%d_%H:%M)"
git push origin main
```

---

# 12. DEVELOPMENT GUIDELINES

## 12.1 Adding New API Endpoint

**Location:** `/var/www/simple_auth_main.py`

**Template:**
```python
@app.get("/api/v1/new-endpoint")
async def new_endpoint(current_user: dict = Depends(get_current_user)):
    """Description of endpoint"""
    try:
        clinic_id = current_user.get('clinic_id')  # Always use JWT clinic_id
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), 
            user=DB_USER, password=DB_PASSWORD, 
            database=DB_NAME
        )
        
        result = await conn.fetch("""
            SELECT * FROM table_name WHERE clinic_id = $1
        """, clinic_id)
        
        await conn.close()
        
        return {"success": True, "data": [dict(r) for r in result]}
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

## 12.2 Adding New Frontend Module

**Location:** `/var/www/Celloxen-C1000/frontend/index.html`

**Steps:**
1. Add navigation item in sidebar
2. Create new component function
3. Add to renderPage() switch statement
4. Implement state management and API calls

## 12.3 Database Changes

**Always:**
1. Create backup first
2. Test in development
3. Document the change

**Adding column:**
```sql
ALTER TABLE table_name ADD COLUMN column_name data_type DEFAULT default_value;
```

**Adding table:**
```sql
CREATE TABLE new_table (
    id SERIAL PRIMARY KEY,
    clinic_id INTEGER REFERENCES clinics(id),
    ...
);
```

## 12.4 Testing Changes

**Backend:**
```bash
# Syntax check
python3 -c "import simple_auth_main"

# API test
curl -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

**Frontend:**
- Hard refresh browser (Ctrl+F5)
- Check browser console for errors
- Test all affected functionality

## 12.5 Deployment Checklist

- [ ] Create backup before changes
- [ ] Test changes locally
- [ ] Update backend file
- [ ] Restart backend service
- [ ] Test API endpoints
- [ ] Update frontend if needed
- [ ] Hard refresh and test UI
- [ ] Commit to GitHub
- [ ] Document changes

---

# 13. COMMON ISSUES & SOLUTIONS

## 13.1 Issue: "relation does not exist"
**Cause:** Backend querying wrong table name
**Solution:** Check actual table name in database
```bash
sudo -u postgres psql -d celloxen_portal -c "\dt" | grep table_name
```

## 13.2 Issue: "column does not exist"
**Cause:** Backend expecting column that doesn't exist
**Solution:** Check table structure
```bash
sudo -u postgres psql -d celloxen_portal -c "\d table_name"
```

## 13.3 Issue: "KeyError in response"
**Cause:** Backend accessing dict key that doesn't exist
**Solution:** Use `.get('key', default)` instead of `['key']`

## 13.4 Issue: 405 Method Not Allowed
**Cause:** Frontend using wrong HTTP method
**Solution:** Match frontend method (GET/POST/PUT/PATCH/DELETE) with backend decorator

## 13.5 Issue: CORS Error
**Cause:** Cross-origin request blocked
**Solution:** Check CORS middleware in backend
```python
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
```

## 13.6 Issue: "hours.map is not a function"
**Cause:** Backend returning object instead of array
**Solution:** Ensure API returns `[]` not `{}`

## 13.7 Issue: Data not showing after save
**Cause:** Frontend not refreshing after API call
**Solution:** Call fetch function after successful POST/PUT

## 13.8 Issue: Multi-tenant data leaking
**Cause:** Hardcoded clinic_id or missing WHERE clause
**Solution:** Always extract clinic_id from JWT and use in queries
```python
clinic_id = current_user.get('clinic_id')  # From JWT
WHERE clinic_id = $1  # Always filter
```

---

# APPENDIX A: ENVIRONMENT VARIABLES
```bash
# /var/www/Celloxen-C1000/backend/.env
DB_HOST=localhost
DB_PORT=5432
DB_USER=celloxen_user
DB_PASSWORD=<password>
DB_NAME=celloxen_portal
JWT_SECRET_KEY=<secret>
ANTHROPIC_API_KEY=<api_key>  # For AI features
```

---

# APPENDIX B: USER ROLES

| Role | Access |
|------|--------|
| super_admin | All clinics, system configuration |
| clinic_admin | Own clinic data only |
| practitioner | Own clinic, limited settings |
| patient | Own data only via patient portal |

---

# APPENDIX C: QUICK REFERENCE COMMANDS
```bash
# Restart everything
pkill -9 -f uvicorn && sleep 2 && cd /var/www && nohup python3 -m uvicorn simple_auth_main:app --host 0.0.0.0 --port 5001 > /var/log/celloxen-backend.log 2>&1 &

# View logs
tail -f /var/log/celloxen-backend.log

# Database shell
sudo -u postgres psql -d celloxen_portal

# Check services
ps aux | grep uvicorn
netstat -tlnp | grep 5001
sudo systemctl status nginx
sudo systemctl status postgresql

# Quick backup
sudo -u postgres pg_dump celloxen_portal > /var/www/backups/quick_$(date +%Y%m%d_%H%M%S).sql
```

---

**Document Created:** 30 November 2025
**Last Updated:** 30 November 2025
**Author:** Claude AI Assistant
**Version:** 1.0

---
