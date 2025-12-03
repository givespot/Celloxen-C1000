# Additional Clinic Endpoints
# To be appended to simple_auth_main.py

@app.post("/api/v1/clinic/change-password")
async def change_password(request: Request, password_data: dict):
    """Change clinic password"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization")

        token = auth_header.split(" ")[1]
        import jwt
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        clinic_email = decoded.get("email")
        
        current_password = password_data.get("current_password")
        new_password = password_data.get("new_password")
        
        if not current_password or not new_password:
            raise HTTPException(status_code=400, detail="Passwords required")
        
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be 8+ characters")
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        try:
            user = await conn.fetchrow(
                "SELECT id, password_hash FROM clinic_credentials WHERE email = $1", clinic_email
            )
            
            if not user or not bcrypt.checkpw(current_password.encode("utf-8"), user["password_hash"].encode("utf-8")):
                raise HTTPException(status_code=400, detail="Current password incorrect")
            
            new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt(rounds=12))
            
            await conn.execute(
                "UPDATE clinic_credentials SET password_hash = $1, must_change_password = false, updated_at = CURRENT_TIMESTAMP WHERE email = $2",
                new_hash.decode("utf-8"), clinic_email
            )
            
            return {"success": True, "message": "Password changed successfully"}
        finally:
            await conn.close()
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error changing password: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/clinic/invoices")
async def get_clinic_invoices(request: Request):
    """Get subscription invoices"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization")

        token = auth_header.split(" ")[1]
        import jwt
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        clinic_email = decoded.get("email")
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        try:
            clinic_cred = await conn.fetchrow(
                "SELECT clinic_id FROM clinic_credentials WHERE email = $1", clinic_email
            )
            
            if not clinic_cred:
                raise HTTPException(status_code=404, detail="Clinic not found")
            
            invoices = await conn.fetch(
                """
                SELECT id, invoice_number, amount, due_date, payment_status as status, 
                       payment_date, billing_period, description, issue_date, created_at
                FROM clinic_invoices
                WHERE clinic_id = $1
                ORDER BY due_date DESC
                """,
                clinic_cred["clinic_id"]
            )
            
            result = []
            for inv in invoices:
                result.append({
                    "id": inv["id"],
                    "invoice_number": inv["invoice_number"],
                    "amount": float(inv["amount"]),
                    "due_date": inv["due_date"].isoformat() if inv["due_date"] else None,
                    "status": inv["status"],
                    "payment_date": inv["payment_date"].isoformat() if inv["payment_date"] else None,
                    "billing_period": inv["billing_period"],
                    "description": inv["description"],
                    "issue_date": inv["issue_date"].isoformat() if inv["issue_date"] else None
                })
            
            return {"invoices": result, "total": len(result)}
        finally:
            await conn.close()
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching invoices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/clinic/patient-invoices")
async def get_patient_invoices(request: Request):
    """Get patient invoices"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authorization")

        token = auth_header.split(" ")[1]
        import jwt
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        clinic_email = decoded.get("email")
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        try:
            clinic_cred = await conn.fetchrow(
                "SELECT clinic_id FROM clinic_credentials WHERE email = $1", clinic_email
            )
            
            if not clinic_cred:
                raise HTTPException(status_code=404, detail="Clinic not found")
            
            invoices = await conn.fetch(
                """
                SELECT pi.*, p.first_name || ' ' || p.last_name as patient_name, p.email as patient_email
                FROM patient_invoices pi
                JOIN patients p ON pi.patient_id = p.id
                WHERE pi.clinic_id = $1
                ORDER BY pi.created_at DESC
                """,
                clinic_cred["clinic_id"]
            )
            
            result = []
            for inv in invoices:
                result.append({
                    "id": inv["id"],
                    "invoice_number": inv["invoice_number"],
                    "patient_name": inv["patient_name"],
                    "patient_email": inv["patient_email"],
                    "amount": float(inv["amount"]),
                    "description": inv["description"],
                    "due_date": inv["due_date"].isoformat() if inv["due_date"] else None,
                    "status": inv["status"]
                })
            
            return {"invoices": result, "total": len(result)}
        finally:
            await conn.close()
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching patient invoices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

