import asyncio
import asyncpg
from datetime import datetime, date
import json

async def create_sample_data():
    # Database connection
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="celloxen_user",
        password="CelloxenSecure2025",
        database="celloxen_portal"
    )
    
    try:
        # Create tables manually with proper SQL
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS clinics (
                id BIGSERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(50) NOT NULL,
                address_line1 VARCHAR(255) NOT NULL,
                city VARCHAR(100) NOT NULL,
                postcode VARCHAR(20) NOT NULL,
                country VARCHAR(100) DEFAULT 'United Kingdom',
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id BIGSERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL,
                clinic_id BIGINT REFERENCES clinics(id),
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id BIGSERIAL PRIMARY KEY,
                patient_number VARCHAR(50) UNIQUE NOT NULL,
                clinic_id BIGINT REFERENCES clinics(id) NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                mobile_phone VARCHAR(50) NOT NULL,
                date_of_birth DATE NOT NULL,
                status VARCHAR(20) DEFAULT 'active',
                portal_access BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        print("✅ Tables created successfully!")
        
        # Insert sample clinic
        clinic_id = await conn.fetchval('''
            INSERT INTO clinics (name, email, phone, address_line1, city, postcode)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        ''', 
        "Aberdeen Wellness Centre", 
        "info@aberdeenwellness.co.uk", 
        "01224 123456",
        "123 Union Street",
        "Aberdeen", 
        "AB10 1AA"
        )
        
        print(f"✅ Sample clinic created with ID: {clinic_id}")
        
        # Insert sample super admin user
        user_id = await conn.fetchval('''
            INSERT INTO users (email, password_hash, full_name, role)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        ''', 
        "admin@celloxen.com",
        "$2b$12$LQv3c1yqBwfNp1cT8MEVUOGdlEzGYKj1OZF7VJcK8GGlEkJyPtf4.", # "password123"
        "Celloxen Admin",
        "super_admin"
        )
        
        print(f"✅ Sample super admin created with ID: {user_id}")
        
        # Insert sample clinic user
        clinic_user_id = await conn.fetchval('''
            INSERT INTO users (email, password_hash, full_name, role, clinic_id)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        ''',
        "staff@aberdeenwellness.co.uk",
        "$2b$12$LQv3c1yqBwfNp1cT8MEVUOGdlEzGYKj1OZF7VJcK8GGlEkJyPtf4.", # "password123"
        "Aberdeen Clinic Staff",
        "clinic_user",
        clinic_id
        )
        
        print(f"✅ Sample clinic user created with ID: {clinic_user_id}")
        
        # Insert sample patient
        patient_id = await conn.fetchval('''
            INSERT INTO patients (patient_number, clinic_id, first_name, last_name, email, mobile_phone, date_of_birth, portal_access)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        ''',
        "CLX-ABD-00001",
        clinic_id,
        "John",
        "Smith", 
        "john.smith@email.com",
        "07700 123456",
        date(1975, 6, 15),
        True
        )
        
        print(f"✅ Sample patient created with ID: {patient_id}")
        
        # Verify data was inserted
        clinics = await conn.fetch("SELECT * FROM clinics")
        users = await conn.fetch("SELECT * FROM users") 
        patients = await conn.fetch("SELECT * FROM patients")
        
        print(f"\n📊 Database Contents:")
        print(f"Clinics: {len(clinics)}")
        print(f"Users: {len(users)}")
        print(f"Patients: {len(patients)}")
        
        print(f"\n🏥 Clinic: {clinics[0]['name']} in {clinics[0]['city']}")
        print(f"👤 Admin: {users[0]['full_name']} ({users[0]['role']})")
        print(f"👩‍⚕️ Staff: {users[1]['full_name']} ({users[1]['role']})")
        print(f"🤒 Patient: {patients[0]['first_name']} {patients[0]['last_name']} ({patients[0]['patient_number']})")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_sample_data())
