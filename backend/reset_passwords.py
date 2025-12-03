#!/usr/bin/env python3
"""Reset passwords for both users"""
import bcrypt
import psycopg2
import os

# New password for both users
NEW_PASSWORD = "password"

# Hash the password
password_hash = bcrypt.hashpw(NEW_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Update in database
conn = psycopg2.connect(
    dbname="celloxen_portal",
    user="celloxen_user",
    password=os.getenv("DB_PASSWORD"),
    host="localhost"
)

cur = conn.cursor()

# Update admin password
cur.execute(
    "UPDATE users SET password_hash = %s WHERE email = 'admin@celloxen.com'",
    (password_hash,)
)

# Update staff password
cur.execute(
    "UPDATE users SET password_hash = %s WHERE email = 'staff@aberdeenwellness.co.uk'",
    (password_hash,)
)

conn.commit()
cur.close()
conn.close()

print("✅ Passwords reset successfully for both users!")
print("\n🔐 LOGIN CREDENTIALS:")
print("\n   Admin Account:")
print("   URL: https://celloxen.com")
print("   Email: admin@celloxen.com")
print("   Password: password")
print("\n   Staff Account:")
print("   Email: staff@aberdeenwellness.co.uk")
print("   Password: password")
