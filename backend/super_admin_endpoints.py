from email_config import send_email, create_welcome_email_html
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from super_admin_auth import (
    verify_super_admin_password, 
    create_super_admin_token,
    verify_super_admin_token
)

router = APIRouter(prefix="/api/v1/super-admin", tags=["Super Admin"])

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="celloxen_portal",
        user="celloxen_user",
        password="CelloxenSecure2025"
    )

# ============================================================================
# AUTHENTICATION
# ============================================================================

class SuperAdminLogin(BaseModel):
    email: str
    password: str

@router.post("/login")
def super_admin_login(credentials: SuperAdminLogin):
    """Super Admin login"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, email, password_hash, first_name, last_name, is_active
            FROM super_admins
            WHERE email = %s
        """, (credentials.email,))
        
        admin = cursor.fetchone()
        
        if not admin:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        admin_id, email, password_hash, first_name, last_name, is_active = admin
        
        if not is_active:
            raise HTTPException(status_code=403, detail="Account inactive")
        
        if not verify_super_admin_password(credentials.password, password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_super_admin_token(admin_id, email)
        
        cursor.execute("""
            UPDATE super_admins 
            SET last_login = CURRENT_TIMESTAMP, login_attempts = 0
            WHERE id = %s
        """, (admin_id,))
        conn.commit()
        
        cursor.execute("""
            INSERT INTO super_admin_audit_log 
            (super_admin_id, action, description)
            VALUES (%s, 'login', 'Super admin logged in')
        """, (admin_id,))
        conn.commit()
        
        return {
            "success": True,
            "token": token,
            "super_admin": {
                "id": admin_id,
                "email": email,
                "first_name": first_name,
                "last_name": last_name
            }
        }
        
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# CLINIC MANAGEMENT (GDPR-COMPLIANT)
# ============================================================================

@router.get("/clinics")
def list_clinics(token_data = Depends(verify_super_admin_token)):
    """List all clinics with GDPR-safe information only"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                c.id,
                COALESCE(c.clinic_name, c.name) as clinic_name,
                c.clinic_code,
                c.city,
                c.postcode,
                c.subscription_tier,
                c.subscription_status,
                c.subscription_end_date,
                c.status,
                c.created_at,
                
                (SELECT COUNT(*) FROM patients WHERE clinic_id = c.id) as total_patients,
                (SELECT COUNT(*) FROM users WHERE clinic_id = c.id) as total_staff,
                (SELECT COUNT(*) FROM appointments WHERE clinic_id = c.id) as total_appointments
                
            FROM clinics c
            ORDER BY c.created_at DESC
        """)
        
        clinics = []
        for row in cursor.fetchall():
            clinics.append({
                "id": row[0],
                "clinic_name": row[1],
                "clinic_code": row[2],
                "city": row[3],
                "postcode": row[4],
                "subscription_tier": row[5],
                "subscription_status": row[6],
                "subscription_end_date": row[7].isoformat() if row[7] else None,
                "status": row[8],
                "created_at": row[9].isoformat() if row[9] else None,
                "statistics": {
                    "total_patients": row[10],
                    "total_staff": row[11],
                    "total_appointments": row[12]
                }
            })
        
        cursor.execute("""
            INSERT INTO super_admin_audit_log 
            (super_admin_id, action, description)
            VALUES (%s, 'viewed_clinics_list', 'Viewed list of all clinics')
        """, (token_data['super_admin_id'],))
        conn.commit()
        
        return {
            "success": True,
            "clinics": clinics,
            "count": len(clinics)
        }
        
    finally:
        cursor.close()
        conn.close()

@router.get("/clinics/{clinic_id}")
def get_clinic_details(clinic_id: int, token_data = Depends(verify_super_admin_token)):
    """Get GDPR-safe clinic details"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                id, COALESCE(clinic_name, name) as clinic_name, clinic_code,
                address_line1, address_line2, city, county, postcode,
                phone, email, website,
                subscription_tier, subscription_status,
                subscription_start_date, subscription_end_date,
                max_patients, max_staff, max_storage_gb,
                status, is_trial, created_at
            FROM clinics
            WHERE id = %s
        """, (clinic_id,))
        
        clinic = cursor.fetchone()
        
        if not clinic:
            raise HTTPException(status_code=404, detail="Clinic not found")
        
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM patients WHERE clinic_id = %s) as total_patients,
                (SELECT COUNT(*) FROM patients WHERE clinic_id = %s AND created_at >= CURRENT_DATE - INTERVAL '30 days') as new_patients_30d,
                (SELECT COUNT(*) FROM users WHERE clinic_id = %s) as total_staff,
                (SELECT COUNT(*) FROM appointments WHERE clinic_id = %s) as total_appointments,
                (SELECT COUNT(*) FROM appointments WHERE clinic_id = %s AND appointment_date >= CURRENT_DATE) as upcoming_appointments,
                (SELECT COUNT(*) FROM iridology_analyses WHERE clinic_id = %s) as total_analyses
        """, (clinic_id, clinic_id, clinic_id, clinic_id, clinic_id, clinic_id))
        
        stats = cursor.fetchone()
        
        cursor.execute("""
            INSERT INTO super_admin_audit_log 
            (super_admin_id, action, resource_type, resource_id, description)
            VALUES (%s, 'viewed_clinic_details', 'clinic', %s, %s)
        """, (token_data['super_admin_id'], clinic_id, f"Viewed details for clinic: {clinic[1]}"))
        conn.commit()
        
        return {
            "success": True,
            "clinic": {
                "id": clinic[0],
                "clinic_name": clinic[1],
                "clinic_code": clinic[2],
                "address": {
                    "line1": clinic[3],
                    "line2": clinic[4],
                    "city": clinic[5],
                    "county": clinic[6],
                    "postcode": clinic[7]
                },
                "contact": {
                    "phone": clinic[8],
                    "email": clinic[9],
                    "website": clinic[10]
                },
                "subscription": {
                    "tier": clinic[11],
                    "status": clinic[12],
                    "start_date": clinic[13].isoformat() if clinic[13] else None,
                    "end_date": clinic[14].isoformat() if clinic[14] else None
                },
                "limits": {
                    "max_patients": clinic[15],
                    "max_staff": clinic[16],
                    "max_storage_gb": clinic[17]
                },
                "status": clinic[18],
                "is_trial": clinic[19],
                "created_at": clinic[20].isoformat() if clinic[20] else None,
                "statistics": {
                    "total_patients": stats[0],
                    "new_patients_30d": stats[1],
                    "total_staff": stats[2],
                    "total_appointments": stats[3],
                    "upcoming_appointments": stats[4],
                    "total_analyses": stats[5]
                }
            }
        }
        
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# SYSTEM STATISTICS
# ============================================================================

@router.get("/dashboard/stats")
def get_system_stats(token_data = Depends(verify_super_admin_token)):
    """Get system-wide statistics (highly aggregated)"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT c.id) as total_clinics,
                COUNT(DISTINCT CASE WHEN c.status = 'active' THEN c.id END) as active_clinics,
                COUNT(DISTINCT CASE WHEN c.subscription_status = 'active' THEN c.id END) as paying_clinics,
                SUM((SELECT COUNT(*) FROM patients WHERE clinic_id = c.id)) as total_patients,
                SUM((SELECT COUNT(*) FROM appointments WHERE clinic_id = c.id)) as total_appointments,
                SUM((SELECT COUNT(*) FROM iridology_analyses WHERE clinic_id = c.id)) as total_analyses
            FROM clinics c
        """)
        
        stats = cursor.fetchone()
        
        return {
            "success": True,
            "system_statistics": {
                "clinics": {
                    "total": stats[0] or 0,
                    "active": stats[1] or 0,
                    "paying": stats[2] or 0
                },
                "patients": {
                    "total_across_all_clinics": stats[3] or 0
                },
                "appointments": {
                    "total_across_all_clinics": stats[4] or 0
                },
                "analyses": {
                    "total_across_all_clinics": stats[5] or 0
                }
            }
        }
        
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# CLINIC MANAGEMENT - CREATE NEW CLINIC
# ============================================================================

class CreateClinicRequest(BaseModel):
    clinic_name: str
    clinic_code: str
    email: str
    phone: str
    address_line1: str
    city: str
    postcode: str
    subscription_tier: str = "professional"
    max_patients: int = 500
    max_staff: int = 10

@router.post("/clinics/create")
def create_clinic(clinic: CreateClinicRequest, token_data = Depends(verify_super_admin_token)):
    """Create a new clinic"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if clinic code already exists
        cursor.execute("SELECT id FROM clinics WHERE clinic_code = %s", (clinic.clinic_code,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Clinic code already exists")
        
        # Insert new clinic
        cursor.execute("""
            INSERT INTO clinics (
                name, clinic_name, clinic_code, email, phone,
                address_line1, city, postcode,
                subscription_tier, subscription_status,
                max_patients, max_staff, max_storage_gb,
                status, created_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, 'active',
                %s, %s, 50,
                'active', CURRENT_TIMESTAMP
            ) RETURNING id
        """, (
            clinic.clinic_name, clinic.clinic_name, clinic.clinic_code,
            clinic.email, clinic.phone,
            clinic.address_line1, clinic.city, clinic.postcode,
            clinic.subscription_tier,
            clinic.max_patients, clinic.max_staff
        ))
        
        clinic_id = cursor.fetchone()[0]
        conn.commit()
        
        # Log the action
        cursor.execute("""
            INSERT INTO super_admin_audit_log 
            (super_admin_id, action, resource_type, resource_id, description, new_values)
            VALUES (%s, 'created_clinic', 'clinic', %s, %s, %s)
        """, (
            token_data['super_admin_id'], 
            clinic_id,
            f"Created new clinic: {clinic.clinic_name}",
            f'{{"clinic_code": "{clinic.clinic_code}", "subscription_tier": "{clinic.subscription_tier}"}}'
        ))
        conn.commit()
        
        return {
            "success": True,
            "message": "Clinic created successfully",
            "clinic_id": clinic_id,
            "clinic_code": clinic.clinic_code
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        import traceback
        error_msg = f"Error creating user: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # This will show in logs
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# AUDIT LOGS - VIEW ALL SUPER ADMIN ACTIONS
# ============================================================================

@router.get("/audit-logs")
def get_audit_logs(
    limit: int = 100,
    token_data = Depends(verify_super_admin_token)
):
    """Get audit logs of all Super Admin actions"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT 
                al.id,
                al.super_admin_id,
                sa.email as admin_email,
                CONCAT(sa.first_name, ' ', sa.last_name) as admin_name,
                al.action,
                al.resource_type,
                al.resource_id,
                al.description,
                al.old_values,
                al.new_values,
                al.ip_address,
                al.created_at
            FROM super_admin_audit_log al
            LEFT JOIN super_admins sa ON al.super_admin_id = sa.id
            ORDER BY al.created_at DESC 
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        
        logs = []
        for row in rows:
            logs.append({
                "id": row[0],
                "super_admin_id": row[1],
                "admin_email": row[2],
                "admin_name": row[3],
                "action": row[4],
                "resource_type": row[5],
                "resource_id": row[6],
                "description": row[7],
                "old_values": row[8],
                "new_values": row[9],
                "ip_address": row[10],
                "created_at": row[11].isoformat() if row[11] else None
            })
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM super_admin_audit_log")
        total = cursor.fetchone()[0]
        
        return {
            "success": True,
            "logs": logs,
            "total": total
        }
        
    finally:
        cursor.close()
        conn.close()

@router.get("/audit-logs/summary")
def get_audit_summary(token_data = Depends(verify_super_admin_token)):
    """Get summary of audit log actions"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                action,
                COUNT(*) as count,
                MAX(created_at) as last_occurrence
            FROM super_admin_audit_log
            GROUP BY action
            ORDER BY count DESC
        """)
        
        summary = []
        for row in cursor.fetchall():
            summary.append({
                "action": row[0],
                "count": row[1],
                "last_occurrence": row[2].isoformat() if row[2] else None
            })
        
        return {
            "success": True,
            "summary": summary
        }
        
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# CLINIC MANAGEMENT - UPDATE CLINIC
# ============================================================================

class UpdateClinicRequest(BaseModel):
    clinic_name: str
    email: str
    phone: str
    address_line1: str
    city: str
    postcode: str
    subscription_tier: str
    max_patients: int
    max_staff: int

@router.put("/clinics/{clinic_id}/update")
def update_clinic(clinic_id: int, clinic: UpdateClinicRequest, token_data = Depends(verify_super_admin_token)):
    """Update clinic details"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get old values for audit log
        cursor.execute("SELECT name, email, subscription_tier FROM clinics WHERE id = %s", (clinic_id,))
        old_data = cursor.fetchone()
        
        if not old_data:
            raise HTTPException(status_code=404, detail="Clinic not found")
        
        # Update clinic
        cursor.execute("""
            UPDATE clinics SET
                name = %s,
                clinic_name = %s,
                email = %s,
                phone = %s,
                address_line1 = %s,
                city = %s,
                postcode = %s,
                subscription_tier = %s,
                max_patients = %s,
                max_staff = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (
            clinic.clinic_name, clinic.clinic_name,
            clinic.email, clinic.phone,
            clinic.address_line1, clinic.city, clinic.postcode,
            clinic.subscription_tier,
            clinic.max_patients, clinic.max_staff,
            clinic_id
        ))
        
        conn.commit()
        
        # Log the action
        cursor.execute("""
            INSERT INTO super_admin_audit_log 
            (super_admin_id, action, resource_type, resource_id, description, old_values, new_values)
            VALUES (%s, 'updated_clinic', 'clinic', %s, %s, %s, %s)
        """, (
            token_data['super_admin_id'], 
            clinic_id,
            f"Updated clinic: {clinic.clinic_name}",
            f'{{"name": "{old_data[0]}", "email": "{old_data[1]}", "tier": "{old_data[2]}"}}',
            f'{{"name": "{clinic.clinic_name}", "email": "{clinic.email}", "tier": "{clinic.subscription_tier}"}}'
        ))
        conn.commit()
        
        return {
            "success": True,
            "message": "Clinic updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        import traceback
        error_msg = f"Error creating user: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # This will show in logs
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# CLINIC MANAGEMENT - CHANGE STATUS (SUSPEND/ACTIVATE)
# ============================================================================

class ClinicStatusRequest(BaseModel):
    status: str

@router.put("/clinics/{clinic_id}/status")
def update_clinic_status(clinic_id: int, request: ClinicStatusRequest, token_data = Depends(verify_super_admin_token)):
    """Suspend or activate a clinic"""
    
    if request.status not in ['active', 'suspended']:
        raise HTTPException(status_code=400, detail="Status must be 'active' or 'suspended'")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get clinic name
        cursor.execute("SELECT name, status FROM clinics WHERE id = %s", (clinic_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Clinic not found")
        
        clinic_name, old_status = result
        
        # Update status
        cursor.execute("""
            UPDATE clinics SET
                status = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (request.status, clinic_id))
        
        conn.commit()
        
        # Log the action
        cursor.execute("""
            INSERT INTO super_admin_audit_log 
            (super_admin_id, action, resource_type, resource_id, description, old_values, new_values)
            VALUES (%s, %s, 'clinic', %s, %s, %s, %s)
        """, (
            token_data['super_admin_id'], 
            'suspended_clinic' if request.status == 'suspended' else 'activated_clinic',
            clinic_id,
            f"Changed status of {clinic_name} to {request.status}",
            f'{{"status": "{old_status}"}}',
            f'{{"status": "{request.status}"}}'
        ))
        conn.commit()
        
        return {
            "success": True,
            "message": f"Clinic {request.status} successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        import traceback
        error_msg = f"Error creating user: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # This will show in logs
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# CLINIC MANAGEMENT - DELETE CLINIC
# ============================================================================

@router.delete("/clinics/{clinic_id}/delete")
def delete_clinic(clinic_id: int, token_data = Depends(verify_super_admin_token)):
    """Delete a clinic and all related records"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get clinic name for audit log
        cursor.execute("SELECT name, clinic_code FROM clinics WHERE id = %s", (clinic_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Clinic not found")
        
        clinic_name, clinic_code = result
        
        # Delete clinic (this will cascade to related tables)
        cursor.execute("DELETE FROM clinics WHERE id = %s", (clinic_id,))
        
        conn.commit()
        
        # Log the action
        cursor.execute("""
            INSERT INTO super_admin_audit_log 
            (super_admin_id, action, resource_type, resource_id, description, old_values)
            VALUES (%s, 'deleted_clinic', 'clinic', %s, %s, %s)
        """, (
            token_data['super_admin_id'], 
            clinic_id,
            f"Deleted clinic: {clinic_name}",
            f'{{"name": "{clinic_name}", "code": "{clinic_code}"}}'
        ))
        conn.commit()
        
        return {
            "success": True,
            "message": "Clinic deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        import traceback
        error_msg = f"Error creating user: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # This will show in logs
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# INVOICE MANAGEMENT - CREATE INVOICE
# ============================================================================

class CreateInvoiceRequest(BaseModel):
    clinic_id: int
    amount: float
    due_date: str
    billing_period: str = None
    description: str = None

@router.post("/invoices/create")
def create_invoice(invoice: CreateInvoiceRequest, token_data = Depends(verify_super_admin_token)):
    """Create a new invoice for a clinic"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Generate invoice number
        cursor.execute("SELECT COUNT(*) FROM clinic_invoices")
        invoice_count = cursor.fetchone()[0]
        invoice_number = f"INV-{(invoice_count + 1):05d}"
        
        # Get clinic name
        cursor.execute("SELECT name FROM clinics WHERE id = %s", (invoice.clinic_id,))
        clinic_result = cursor.fetchone()
        if not clinic_result:
            raise HTTPException(status_code=404, detail="Clinic not found")
        
        # Insert invoice
        cursor.execute("""
            INSERT INTO clinic_invoices (
                clinic_id, invoice_number, amount, due_date,
                billing_period, description, payment_status,
                issue_date, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, 'pending', CURRENT_DATE, CURRENT_TIMESTAMP
            ) RETURNING id
        """, (
            invoice.clinic_id, invoice_number, invoice.amount, invoice.due_date,
            invoice.billing_period, invoice.description
        ))
        
        invoice_id = cursor.fetchone()[0]
        conn.commit()
        
        # Log the action
        cursor.execute("""
            INSERT INTO super_admin_audit_log 
            (super_admin_id, action, resource_type, resource_id, description, new_values)
            VALUES (%s, 'created_invoice', 'invoice', %s, %s, %s)
        """, (
            token_data['super_admin_id'], 
            invoice_id,
            f"Created invoice {invoice_number} for {clinic_result[0]}",
            f'{{"amount": {invoice.amount}, "due_date": "{invoice.due_date}"}}'
        ))
        conn.commit()
        
        return {
            "success": True,
            "message": "Invoice created successfully",
            "invoice_id": invoice_id,
            "invoice_number": invoice_number
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        import traceback
        error_msg = f"Error creating user: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # This will show in logs
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# INVOICE MANAGEMENT - GET ALL INVOICES
# ============================================================================

@router.get("/invoices")
def get_invoices(
    status: str = None,
    clinic_id: int = None,
    period: str = None,
    token_data = Depends(verify_super_admin_token)
):
    """Get all invoices with optional filters"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT 
                i.id,
                i.invoice_number,
                i.clinic_id,
                c.name as clinic_name,
                i.amount,
                i.due_date,
                i.payment_status,
                i.payment_date,
                i.billing_period,
                i.description,
                i.issue_date
            FROM clinic_invoices i
            LEFT JOIN clinics c ON i.clinic_id = c.id
            WHERE 1=1
        """
        
        params = []
        
        if status:
            query += " AND i.payment_status = %s"
            params.append(status)
        
        if clinic_id:
            query += " AND i.clinic_id = %s"
            params.append(clinic_id)
        
        if period:
            if period == 'this_month':
                query += " AND EXTRACT(MONTH FROM i.issue_date) = EXTRACT(MONTH FROM CURRENT_DATE)"
                query += " AND EXTRACT(YEAR FROM i.issue_date) = EXTRACT(YEAR FROM CURRENT_DATE)"
            elif period == 'last_month':
                query += " AND EXTRACT(MONTH FROM i.issue_date) = EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')"
                query += " AND EXTRACT(YEAR FROM i.issue_date) = EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 month')"
            elif period == 'this_quarter':
                query += " AND EXTRACT(QUARTER FROM i.issue_date) = EXTRACT(QUARTER FROM CURRENT_DATE)"
                query += " AND EXTRACT(YEAR FROM i.issue_date) = EXTRACT(YEAR FROM CURRENT_DATE)"
            elif period == 'this_year':
                query += " AND EXTRACT(YEAR FROM i.issue_date) = EXTRACT(YEAR FROM CURRENT_DATE)"
        
        query += " ORDER BY i.issue_date DESC, i.id DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        invoices = []
        for row in rows:
            invoices.append({
                "id": row[0],
                "invoice_number": row[1],
                "clinic_id": row[2],
                "clinic_name": row[3],
                "amount": float(row[4]),
                "due_date": row[5].isoformat() if row[5] else None,
                "payment_status": row[6],
                "payment_date": row[7].isoformat() if row[7] else None,
                "billing_period": row[8],
                "description": row[9],
                "issue_date": row[10].isoformat() if row[10] else None
            })
        
        return {
            "success": True,
            "invoices": invoices,
            "total": len(invoices)
        }
        
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# INVOICE MANAGEMENT - GET INVOICE STATISTICS
# ============================================================================

@router.get("/invoices/stats")
def get_invoice_stats(token_data = Depends(verify_super_admin_token)):
    """Get invoice statistics"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Total revenue (all paid invoices)
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) 
            FROM clinic_invoices 
            WHERE payment_status = 'paid'
        """)
        total_revenue = float(cursor.fetchone()[0])
        
        # Paid this month
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) 
            FROM clinic_invoices 
            WHERE payment_status = 'paid'
            AND EXTRACT(MONTH FROM payment_date) = EXTRACT(MONTH FROM CURRENT_DATE)
            AND EXTRACT(YEAR FROM payment_date) = EXTRACT(YEAR FROM CURRENT_DATE)
        """)
        paid_this_month = float(cursor.fetchone()[0])
        
        # Pending amount
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) 
            FROM clinic_invoices 
            WHERE payment_status = 'pending'
        """)
        pending_amount = float(cursor.fetchone()[0])
        
        # Overdue amount
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) 
            FROM clinic_invoices 
            WHERE payment_status = 'overdue'
        """)
        overdue_amount = float(cursor.fetchone()[0])
        
        return {
            "success": True,
            "stats": {
                "total_revenue": total_revenue,
                "paid_this_month": paid_this_month,
                "pending_amount": pending_amount,
                "overdue_amount": overdue_amount
            }
        }
        
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# INVOICE MANAGEMENT - MARK INVOICE AS PAID
# ============================================================================

@router.put("/invoices/{invoice_id}/mark-paid")
def mark_invoice_paid(invoice_id: int, token_data = Depends(verify_super_admin_token)):
    """Mark an invoice as paid"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get invoice details
        cursor.execute("""
            SELECT i.invoice_number, c.name 
            FROM clinic_invoices i
            LEFT JOIN clinics c ON i.clinic_id = c.id
            WHERE i.id = %s
        """, (invoice_id,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice_number, clinic_name = result
        
        # Update invoice
        cursor.execute("""
            UPDATE clinic_invoices SET
                payment_status = 'paid',
                payment_date = CURRENT_DATE,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (invoice_id,))
        
        conn.commit()
        
        # Log the action
        cursor.execute("""
            INSERT INTO super_admin_audit_log 
            (super_admin_id, action, resource_type, resource_id, description)
            VALUES (%s, 'marked_invoice_paid', 'invoice', %s, %s)
        """, (
            token_data['super_admin_id'], 
            invoice_id,
            f"Marked invoice {invoice_number} as paid for {clinic_name}"
        ))
        conn.commit()
        
        return {
            "success": True,
            "message": "Invoice marked as paid"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        import traceback
        error_msg = f"Error creating user: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # This will show in logs
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# INVOICE MANAGEMENT - GET SINGLE INVOICE
# ============================================================================

@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int, token_data = Depends(verify_super_admin_token)):
    """Get detailed invoice information"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                i.id,
                i.invoice_number,
                i.clinic_id,
                c.name as clinic_name,
                c.email as clinic_email,
                c.phone as clinic_phone,
                c.address_line1,
                c.city,
                c.postcode,
                i.amount,
                i.due_date,
                i.payment_status,
                i.payment_date,
                i.billing_period,
                i.description,
                i.issue_date,
                i.created_at
            FROM clinic_invoices i
            LEFT JOIN clinics c ON i.clinic_id = c.id
            WHERE i.id = %s
        """, (invoice_id,))
        
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        invoice = {
            "id": row[0],
            "invoice_number": row[1],
            "clinic": {
                "id": row[2],
                "name": row[3],
                "email": row[4],
                "phone": row[5],
                "address_line1": row[6],
                "city": row[7],
                "postcode": row[8]
            },
            "amount": float(row[9]),
            "due_date": row[10].isoformat() if row[10] else None,
            "payment_status": row[11],
            "payment_date": row[12].isoformat() if row[12] else None,
            "billing_period": row[13],
            "description": row[14],
            "issue_date": row[15].isoformat() if row[15] else None,
            "created_at": row[16].isoformat() if row[16] else None
        }
        
        return {
            "success": True,
            "invoice": invoice
        }
        
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# REPORTS - SUMMARY STATISTICS
# ============================================================================

@router.get("/reports/summary")
def get_reports_summary(token_data = Depends(verify_super_admin_token)):
    """Get summary statistics for reports"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Total clinics
        cursor.execute("SELECT COUNT(*) FROM clinics")
        total_clinics = cursor.fetchone()[0]
        
        # New clinics this month
        cursor.execute("""
            SELECT COUNT(*) FROM clinics 
            WHERE EXTRACT(MONTH FROM created_at) = EXTRACT(MONTH FROM CURRENT_DATE)
            AND EXTRACT(YEAR FROM created_at) = EXTRACT(YEAR FROM CURRENT_DATE)
        """)
        new_clinics_this_month = cursor.fetchone()[0]
        
        # Total patients across all clinics
        cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = cursor.fetchone()[0]
        
        # Patient growth last 30 days
        cursor.execute("""
            SELECT COUNT(*) FROM patients 
            WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
        """)
        patients_growth_30d = cursor.fetchone()[0]
        
        # Revenue this month
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM clinic_invoices 
            WHERE payment_status = 'paid'
            AND EXTRACT(MONTH FROM payment_date) = EXTRACT(MONTH FROM CURRENT_DATE)
            AND EXTRACT(YEAR FROM payment_date) = EXTRACT(YEAR FROM CURRENT_DATE)
        """)
        revenue_this_month = float(cursor.fetchone()[0])
        
        # Revenue last month
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) FROM clinic_invoices 
            WHERE payment_status = 'paid'
            AND EXTRACT(MONTH FROM payment_date) = EXTRACT(MONTH FROM CURRENT_DATE - INTERVAL '1 month')
            AND EXTRACT(YEAR FROM payment_date) = EXTRACT(YEAR FROM CURRENT_DATE - INTERVAL '1 month')
        """)
        revenue_last_month = float(cursor.fetchone()[0])
        
        # Calculate revenue growth
        if revenue_last_month > 0:
            revenue_growth = ((revenue_this_month - revenue_last_month) / revenue_last_month) * 100
        else:
            revenue_growth = 100.0 if revenue_this_month > 0 else 0.0
        
        # Active subscriptions
        cursor.execute("""
            SELECT COUNT(*) FROM clinics 
            WHERE status = 'active' AND subscription_status = 'active'
        """)
        active_subscriptions = cursor.fetchone()[0]
        
        subscription_rate = (active_subscriptions / total_clinics * 100) if total_clinics > 0 else 0
        
        return {
            "success": True,
            "stats": {
                "total_clinics": total_clinics,
                "new_clinics_this_month": new_clinics_this_month,
                "total_patients": total_patients,
                "patients_growth_30d": patients_growth_30d,
                "revenue_this_month": revenue_this_month,
                "revenue_growth": revenue_growth,
                "active_subscriptions": active_subscriptions,
                "subscription_rate": subscription_rate
            }
        }
        
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# REPORTS - CHART DATA
# ============================================================================

@router.get("/reports/charts")
def get_charts_data(token_data = Depends(verify_super_admin_token)):
    """Get data for charts"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Revenue trend - last 6 months
        cursor.execute("""
            SELECT 
                TO_CHAR(payment_date, 'Mon YYYY') as month,
                SUM(amount) as revenue
            FROM clinic_invoices
            WHERE payment_status = 'paid'
            AND payment_date >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY TO_CHAR(payment_date, 'Mon YYYY'), EXTRACT(YEAR FROM payment_date), EXTRACT(MONTH FROM payment_date)
            ORDER BY EXTRACT(YEAR FROM payment_date), EXTRACT(MONTH FROM payment_date)
        """)
        revenue_data = cursor.fetchall()
        revenue_trend = {
            "labels": [row[0] for row in revenue_data],
            "values": [float(row[1]) for row in revenue_data]
        }
        
        # Patient growth - last 6 months
        cursor.execute("""
            SELECT 
                TO_CHAR(created_at, 'Mon YYYY') as month,
                COUNT(*) as patients
            FROM patients
            WHERE created_at >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY TO_CHAR(created_at, 'Mon YYYY'), EXTRACT(YEAR FROM created_at), EXTRACT(MONTH FROM created_at)
            ORDER BY EXTRACT(YEAR FROM created_at), EXTRACT(MONTH FROM created_at)
        """)
        patient_data = cursor.fetchall()
        patient_growth = {
            "labels": [row[0] for row in patient_data],
            "values": [row[1] for row in patient_data]
        }
        
        # Clinic status
        cursor.execute("SELECT COUNT(*) FROM clinics WHERE status = 'active'")
        active_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM clinics WHERE status = 'suspended'")
        suspended_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM clinics WHERE is_trial = true")
        trial_count = cursor.fetchone()[0]
        
        clinic_status = {
            "active": active_count,
            "suspended": suspended_count,
            "trial": trial_count
        }
        
        # Subscription tiers
        cursor.execute("SELECT COUNT(*) FROM clinics WHERE subscription_tier = 'free'")
        free_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM clinics WHERE subscription_tier = 'basic'")
        basic_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM clinics WHERE subscription_tier = 'professional'")
        professional_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM clinics WHERE subscription_tier = 'enterprise'")
        enterprise_count = cursor.fetchone()[0]
        
        subscription_tiers = {
            "free": free_count,
            "basic": basic_count,
            "professional": professional_count,
            "enterprise": enterprise_count
        }
        
        return {
            "success": True,
            "revenue_trend": revenue_trend,
            "patient_growth": patient_growth,
            "clinic_status": clinic_status,
            "subscription_tiers": subscription_tiers
        }
        
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# REPORTS - TOP CLINICS
# ============================================================================

@router.get("/reports/top-clinics")
def get_top_clinics(token_data = Depends(verify_super_admin_token)):
    """Get top performing clinics"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                c.id,
                c.name,
                COUNT(DISTINCT p.id) as patient_count,
                COUNT(DISTINCT a.id) as appointment_count,
                COUNT(DISTINCT an.id) as analysis_count,
                (COUNT(DISTINCT p.id) + COUNT(DISTINCT a.id) + COUNT(DISTINCT an.id)) as total_score
            FROM clinics c
            LEFT JOIN patients p ON c.id = p.clinic_id
            LEFT JOIN appointments a ON c.id = a.clinic_id
            LEFT JOIN analyses an ON c.id = an.clinic_id
            GROUP BY c.id, c.name
            ORDER BY total_score DESC
            LIMIT 10
        """)
        
        clinics = []
        for row in cursor.fetchall():
            clinics.append({
                "id": row[0],
                "name": row[1],
                "patients": row[2],
                "appointments": row[3],
                "analyses": row[4],
                "score": row[5]
            })
        
        return {
            "success": True,
            "clinics": clinics
        }
        
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# EMAIL NOTIFICATIONS - SEND WELCOME EMAIL
# ============================================================================

import secrets
import string
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_temp_password(length=10):
    """Generate a secure temporary password (max 10 chars for bcrypt)"""
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

def send_email_notification(recipient_email, recipient_name, subject, body, email_type, clinic_id=None):
    """Log email notification (to be sent by email service)"""
    # For now, we just log it. Later, integrate with SMTP/SendGrid/etc.
    return {
        "recipient_email": recipient_email,
        "recipient_name": recipient_name,
        "subject": subject,
        "body": body,
        "email_type": email_type,
        "clinic_id": clinic_id
    }

@router.post("/clinics/{clinic_id}/send-welcome-email")
def send_clinic_welcome_email(clinic_id: int, token_data = Depends(verify_super_admin_token)):
    """Send welcome email to new clinic with credentials"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get clinic details
        cursor.execute("""
            SELECT name, email FROM clinics WHERE id = %s
        """, (clinic_id,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Clinic not found")
        
        clinic_name, clinic_email = result
        
        # Generate temporary password
        temp_password = generate_temp_password()
        password_hash = pwd_context.hash(temp_password)
        
        # Store credentials
        cursor.execute("""
            INSERT INTO users 
            (clinic_id, email, password_hash, full_name, role, status)
            VALUES (%s, %s, %s, %s, 'clinic_admin', 'active')
            ON CONFLICT (email) 
            DO UPDATE SET 
                password_hash = EXCLUDED.password_hash
            RETURNING id
        """, (clinic_id, clinic_email, password_hash, clinic_name))
        
        credential_id = cursor.fetchone()[0]
        
        # Create email content
        email_subject = "Welcome to Celloxen Health Portal!"
        email_body = f"""
Hello {clinic_name},

Welcome to Celloxen Health Portal! We're excited to have you on board.

Your clinic portal is now ready to use. Here are your login credentials:

Portal URL: https://celloxen.com/
Email: {clinic_email}
Temporary Password: {temp_password}

IMPORTANT SECURITY NOTICE:
⚠️ This is a temporary password. You will be required to change it upon your first login.
⚠️ Please keep your credentials secure and do not share them.

Getting Started:
1. Visit https://celloxen.com/
2. Log in with the credentials above
3. You'll be prompted to create a new password
4. Complete your clinic profile
5. Start adding patients and managing appointments

Features Available to You:
✅ Patient Management
✅ Appointment Scheduling
✅ Iridology Analysis (AI-powered)
✅ Digital Health Records
✅ Staff Management
✅ Secure Data Storage

Need Help?
If you have any questions or need assistance, please don't hesitate to contact us.

Best regards,
The Celloxen Team

---
This is an automated message. Please do not reply to this email.
        """.strip()
        
        # Log email notification
        cursor.execute("""
            INSERT INTO email_notifications 
            (recipient_email, recipient_name, subject, email_type, status, related_clinic_id)
            VALUES (%s, %s, %s, 'welcome', 'pending', %s)
            RETURNING id
        """, (clinic_email, clinic_name, email_subject, clinic_id))
        
        email_log_id = cursor.fetchone()[0]
        
        conn.commit()
        
        # In production, send actual email here via SMTP/SendGrid
        # Send the actual email
        html_body = create_welcome_email_html(
            clinic_name, 
            "https://celloxen.com/", 
            clinic_email, 
            temp_password
        )
        
        email_result = send_email(
            to_email=clinic_email,
            subject=email_subject,
            html_body=html_body
        )
        
        if email_result["success"]:
            cursor.execute(
                "UPDATE email_notifications SET status = 'sent', sent_at = CURRENT_TIMESTAMP WHERE id = %s",
                (email_log_id,)
            )
            conn.commit()
        
        return {
            "success": True,
            "message": "Welcome email prepared",
            "email_details": {
                "to": clinic_email,
                "subject": email_subject,
                "body": email_body
            },
            "credentials": {
                "email": clinic_email,
                "temporary_password": temp_password
            },
            "note": "Email logged in database. In production, this would be sent automatically."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        import traceback
        error_msg = f"Error creating user: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # This will show in logs
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# EMAIL NOTIFICATIONS - GET EMAIL LOG
# ============================================================================

@router.get("/emails/log")
def get_email_log(
    limit: int = 50,
    email_type: str = None,
    token_data = Depends(verify_super_admin_token)
):
    """Get email notification log"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT 
                e.id,
                e.recipient_email,
                e.recipient_name,
                e.subject,
                e.email_type,
                e.status,
                e.sent_at,
                e.error_message,
                c.name as clinic_name,
                e.created_at
            FROM email_notifications e
            LEFT JOIN clinics c ON e.related_clinic_id = c.id
            WHERE 1=1
        """
        
        params = []
        
        if email_type:
            query += " AND e.email_type = %s"
            params.append(email_type)
        
        query += " ORDER BY e.created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        emails = []
        for row in rows:
            emails.append({
                "id": row[0],
                "recipient_email": row[1],
                "recipient_name": row[2],
                "subject": row[3],
                "email_type": row[4],
                "status": row[5],
                "sent_at": row[6].isoformat() if row[6] else None,
                "error_message": row[7],
                "clinic_name": row[8],
                "created_at": row[9].isoformat() if row[9] else None
            })
        
        return {
            "success": True,
            "emails": emails,
            "total": len(emails)
        }
        
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# USER MANAGEMENT - GET SUPER ADMINS
# ============================================================================

@router.get("/users/super-admins")
def get_super_admins(token_data = Depends(verify_super_admin_token)):
    """Get list of all super admin users"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, email, name, created_at, last_login
            FROM super_admins
            ORDER BY created_at DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row[0],
                "email": row[1],
                "name": row[2],
                "created_at": row[3].isoformat() if row[3] else None,
                "status": row[4]
            })
        
        return {
            "success": True,
            "users": users
        }
        
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# USER MANAGEMENT - GET CLINIC ADMINS
# ============================================================================

@router.get("/users/clinic-admins")
def get_clinic_admins(token_data = Depends(verify_super_admin_token)):
    """Get list of all clinic admin users"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                u.id,
                u.email,
                c.name as clinic_name,
                u.created_at,
                u.status
            FROM users u
            JOIN clinics c ON u.clinic_id = c.id
            WHERE u.role = 'clinic_admin' ORDER BY u.created_at DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row[0],
                "email": row[1],
                "name": row[1].split('@')[0],  # Extract name from email
                "clinic_name": row[2],
                "created_at": row[3].isoformat() if row[3] else None,
                "status": row[4]
            })
        
        return {
            "success": True,
            "users": users
        }
        
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# USER MANAGEMENT - CREATE USER
# ============================================================================

class CreateUserRequest(BaseModel):
    user_type: str  # 'super_admin' or 'clinic_admin'
    email: str
    name: str
    clinic_id: int = None

@router.post("/users/create")
def create_user(request: CreateUserRequest, token_data = Depends(verify_super_admin_token)):
    """Create a new super admin or clinic admin user"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Generate temporary password
        temp_password = generate_temp_password()
        password_hash = pwd_context.hash(temp_password)
        
        if request.user_type == 'super_admin':
            # Check if email already exists
            cursor.execute("SELECT id FROM super_admins WHERE email = %s", (request.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email already exists")
            
            # Create super admin
            cursor.execute("""
                INSERT INTO super_admins (email, password_hash, name, created_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING id
            """, (request.email, password_hash, request.name))
            
            user_id = cursor.fetchone()[0]
            
            # Log action
            cursor.execute("""
                INSERT INTO super_admin_audit_log (super_admin_id, action, description, ip_address)
                VALUES (%s, 'create_user', %s, '0.0.0.0')
            """, (token_data.get("super_admin_id", 1), f"Created super admin user: {request.email}"))
            
            # Send welcome email to Super Admin
            email_subject = "Celloxen Super Admin - Your Account Created"
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; }}
        .header {{ background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; }}
        .credentials {{ background: #fef3c7; border: 2px solid #f59e0b; border-radius: 8px; padding: 20px; margin: 20px 0; }}
        .credential-item {{ margin: 10px 0; padding: 10px; background: white; border-radius: 6px; }}
        .footer {{ background: #1e293b; color: white; text-align: center; padding: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Celloxen Super Admin</h1>
        </div>
        <div class="content">
            <h2>Hello {request.name},</h2>
            <p>Your Super Admin account has been created for the Celloxen Health Portal platform.</p>
            
            <div class="credentials">
                <h3 style="color: #92400e; margin-top: 0;">🔐 Your Login Credentials</h3>
                <div class="credential-item">
                    <strong>Portal URL:</strong><br>
                    <a href="https://celloxen.com/super_admin_portal.html">https://celloxen.com/super_admin_portal.html</a>
                </div>
                <div class="credential-item">
                    <strong>Email:</strong><br>
                    {request.email}
                </div>
                <div class="credential-item">
                    <strong>Temporary Password:</strong><br>
                    <code style="font-size: 18px; font-weight: bold; color: #1e3a8a;">{temp_password}</code>
                </div>
            </div>
            
            <p><strong>⚠️ IMPORTANT:</strong></p>
            <ul>
                <li>This is a temporary password</li>
                <li>You should change it immediately after your first login</li>
                <li>Never share your password with anyone</li>
                <li>Keep these credentials secure</li>
            </ul>
            
            <p><strong>As a Super Admin, you have access to:</strong></p>
            <ul>
                <li>✅ Manage all clinics</li>
                <li>✅ Create invoices and track payments</li>
                <li>✅ View system analytics and reports</li>
                <li>✅ Manage user accounts</li>
                <li>✅ View audit logs</li>
            </ul>
            
            <p>Best regards,<br><strong>Celloxen Team</strong></p>
        </div>
        <div class="footer">
            <p><strong>CELLOXEN HEALTH PORTAL</strong></p>
            <p>&copy; 2025 Celloxen. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
            """
            
            # Send the email
            email_result = send_email(
                to_email=request.email,
                subject=email_subject,
                html_body=html_body
            )
            
            # Log the email
            cursor.execute("""
                INSERT INTO email_notifications 
                (recipient_email, recipient_name, subject, email_type, status)
                VALUES (%s, %s, %s, 'super_admin_welcome', %s)
            """, (request.email, request.name, email_subject, 'sent' if email_result['success'] else 'failed'))
            
        elif request.user_type == 'clinic_admin':
            if not request.clinic_id:
                raise HTTPException(status_code=400, detail="Clinic ID required for clinic admin")
            
            # Check if email already exists
            cursor.execute("SELECT id FROM clinic_credentials WHERE email = %s", (request.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email already exists")
            
            # Create clinic admin
            cursor.execute("""
                INSERT INTO users 
                (clinic_id, email, password_hash, full_name, role, status, created_at)
                VALUES (%s, %s, %s, %s, 'clinic_admin', 'active', CURRENT_TIMESTAMP)
                RETURNING id
            """, (request.clinic_id, request.email, password_hash, request.name))
            
            user_id = cursor.fetchone()[0]
            
            # Log action
            cursor.execute("""
                INSERT INTO super_admin_audit_log (super_admin_id, action, description, ip_address)
                VALUES (%s, 'create_user', %s, '0.0.0.0')
            """, (token_data.get("super_admin_id", 1), f"Created clinic admin user: {request.email} for clinic ID {request.clinic_id}"))
            
        else:
            raise HTTPException(status_code=400, detail="Invalid user type")
        
        conn.commit()
        
        # Send welcome email with credentials
        if request.user_type == 'super_admin':
            email_subject = "Celloxen Super Admin - Your Account"
            email_body = f"""
Hello {request.name},

Your Super Admin account has been created for Celloxen Health Portal.

Login URL: https://celloxen.com/super_admin_portal.html
Email: {request.email}
Temporary Password: {temp_password}

⚠️ IMPORTANT: You must change this password on your first login.

Best regards,
Celloxen Team
            """
        else:
            # Get clinic name
            cursor.execute("SELECT name FROM clinics WHERE id = %s", (request.clinic_id,))
            clinic_name = cursor.fetchone()[0]
            
            email_subject = "Welcome to Celloxen Health Portal"
            html_body = create_welcome_email_html(
                clinic_name,
                "https://celloxen.com/",
                request.email,
                temp_password
            )
            
            # Send email
            email_result = send_email(
                to_email=request.email,
                subject=email_subject,
                html_body=html_body
            )
            
            # Log email
            cursor.execute("""
                INSERT INTO email_notifications 
                (recipient_email, recipient_name, subject, email_type, status, related_clinic_id)
                VALUES (%s, %s, %s, 'welcome', %s, %s)
            """, (request.email, request.name, email_subject, 
                  'sent' if email_result['success'] else 'failed', request.clinic_id))
            conn.commit()
        
        return {
            "success": True,
            "message": "User created successfully. Welcome email sent." if request.user_type == 'clinic_admin' else "User created successfully.",
            "user_id": user_id,
            "temporary_password": temp_password
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        import traceback
        error_msg = f"Error creating user: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # This will show in logs
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# USER MANAGEMENT - RESET PASSWORD
# ============================================================================

@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    user_type: str,
    token_data = Depends(verify_super_admin_token)
):
    """Reset a user's password"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Generate new temporary password
        new_password = generate_temp_password()
        password_hash = pwd_context.hash(new_password)
        
        if user_type == 'super_admin':
            cursor.execute("""
                UPDATE super_admins
                SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING email
            """, (password_hash, user_id))
            
        elif user_type == 'clinic_admin':
            cursor.execute("""
                UPDATE clinic_credentials
                SET password_hash = %s, 
                    temporary_password = true, 
                    must_change_password = true,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING email
            """, (password_hash, user_id))
            
        else:
            raise HTTPException(status_code=400, detail="Invalid user type")
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_email = result[0]
        
        # Log action
        cursor.execute("""
            INSERT INTO super_admin_audit_log (super_admin_id, action, description, ip_address)
            VALUES (%s, 'reset_password', %s, '0.0.0.0')
        """, (token_data.get("super_admin_id", 1), f"Reset password for {user_type}: {user_email}"))
        
        conn.commit()
        
        return {
            "success": True,
            "message": "Password reset successfully",
            "new_password": new_password
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        import traceback
        error_msg = f"Error creating user: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # This will show in logs
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# USER MANAGEMENT - DELETE USER
# ============================================================================

@router.delete("/users/{user_id}/delete")
def delete_user(
    user_id: int,
    user_type: str,
    token_data = Depends(verify_super_admin_token)
):
    """Delete a user account"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if user_type == 'super_admin':
            # Get user email first
            cursor.execute("SELECT email FROM super_admins WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_email = result[0]
            
            # Prevent deletion of primary admin
            if user_email == 'admin@celloxen.com':
                raise HTTPException(status_code=400, detail="Cannot delete primary admin account")
            
            cursor.execute("DELETE FROM super_admins WHERE id = %s", (user_id,))
            
        elif user_type == 'clinic_admin':
            # Get user email first
            cursor.execute("SELECT email FROM clinic_credentials WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_email = result[0]
            cursor.execute("DELETE FROM clinic_credentials WHERE id = %s", (user_id,))
            
        else:
            raise HTTPException(status_code=400, detail="Invalid user type")
        
        # Log action
        cursor.execute("""
            INSERT INTO super_admin_audit_log (super_admin_id, action, description, ip_address)
            VALUES (%s, 'delete_user', %s, '0.0.0.0')
        """, (token_data.get("super_admin_id", 1), f"Deleted {user_type}: {user_email}"))
        
        conn.commit()
        
        return {
            "success": True,
            "message": "User deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        import traceback
        error_msg = f"Error creating user: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # This will show in logs
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
