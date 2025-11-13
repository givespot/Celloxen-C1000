# 🏥 Celloxen Health Portal

A comprehensive multi-tenant clinic management platform for holistic wellness therapies.

## 📋 Project Overview

**Celloxen Health Portal** manages the complete patient journey from registration through therapy completion across multiple wellness clinics specializing in four primary therapy domains:

- 🩺 **Diabetics Support** - Blood sugar management and metabolic wellness  
- 🦴 **Chronic Pain Management** - Pain relief and mobility improvement
- 🧘 **Anxiety & Stress Relief** - Mental wellness and relaxation
- ⚡ **Energy Rejuvenation** - General health and vitality improvement

## ✅ Features Implemented

### 🔐 Authentication System
- Multi-role access (Super Admin, Clinic Staff, Patient)
- JWT token authentication with secure sessions
- Role-based access control (RBAC)

### 🏥 Clinic Management
- Multi-tenant architecture with complete data isolation
- Real-time dashboard with live statistics
- Aberdeen Wellness Centre active with patient data

### 👥 Patient Management  
- Comprehensive patient registration (personal + medical + emergency)
- Advanced real-time search and filtering
- Full CRUD operations (Create, Read, Update, Delete)
- Individual patient profiles with complete medical history
- Medical conditions, medications, and allergies tracking

### 📊 Dashboard Analytics
- Live patient counts from database
- Today's appointment schedule
- Quick action buttons for common tasks
- Professional healthcare-appropriate interface

## 🛠️ Technology Stack

- **Backend**: Python FastAPI + PostgreSQL + asyncpg
- **Frontend**: React 18 + Tailwind CSS + Font Awesome
- **Infrastructure**: Ubuntu 24.04 + Nginx + systemd  
- **Security**: JWT authentication + RBAC + data encryption

## 🚀 Quick Start
```bash
# 1. Clone repository
git clone https://github.com/givespot/celloxen_portal.git
cd celloxen_portal

# 2. Run installation
chmod +x scripts/install.sh
sudo ./scripts/install.sh

# 3. Access portal
# https://celloxen.com
```

## 🎯 Current Status

- ✅ **Authentication**: Complete with JWT + RBAC
- ✅ **Clinic Dashboard**: Real-time analytics  
- ✅ **Patient Management**: Full CRUD + search + medical records
- ✅ **Patient Profiles**: Comprehensive individual views
- 🚧 **Assessment System**: Next milestone
- ⏳ **Therapy Planning**: Planned
- ⏳ **Patient Portal**: Planned

## 📊 Active Data

- **2 Patients**: John Smith, Hafsa Rguib (with full medical records)
- **1 Clinic**: Aberdeen Wellness Centre  
- **System Users**: Super admin and clinic staff accounts

## 🔒 Security & Compliance

- Data encryption at rest and in transit
- GDPR-compliant data handling
- Audit trails for all patient interactions  
- Role-based data isolation

## 📁 Project Structure
```
celloxen_portal/
├── backend/                 # FastAPI application
├── frontend/               # React application
├── database/              # Schema and seed data  
├── scripts/              # Deployment automation
└── README.md            # This file
```

## 🏥 Next Development Phase

Building comprehensive health assessment system with questionnaires for the four therapy domains and automated therapy recommendations.

---

**Built for holistic wellness and exceptional patient care** 🏥✨
