#!/usr/bin/env python3
"""
Utility script to set patient passwords
Usage: python3 set_patient_password.py <patient_email> <password>
"""

import sys
import bcrypt
import psycopg2
import os

def set_patient_password(email, password):
    """Set password for a patient by email"""
    
    # Hash the password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Connect to database
    conn = psycopg2.connect(
        dbname="celloxen_portal",
        user="celloxen_user",
        password=os.getenv("DB_PASSWORD"),
        host="localhost"
    )
    cur = conn.cursor()
    
    try:
        # Update patient password
        cur.execute("""
            UPDATE patients 
            SET password_hash = %s
            WHERE LOWER(email) = LOWER(%s)
            RETURNING id, first_name, last_name, email
        """, (password_hash, email))
        
        result = cur.fetchone()
        
        if result:
            conn.commit()
            patient_id, first_name, last_name, patient_email = result
            print(f"✅ Password set successfully for:")
            print(f"   Patient: {first_name} {last_name}")
            print(f"   Email: {patient_email}")
            print(f"   Patient ID: {patient_id}")
            print(f"\n🔐 Patient can now login at: https://celloxen.com/patient_portal.html")
        else:
            print(f"❌ No patient found with email: {email}")
            
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 set_patient_password.py <patient_email> <password>")
        print("Example: python3 set_patient_password.py john.smith@email.com SecurePass123")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    set_patient_password(email, password)
