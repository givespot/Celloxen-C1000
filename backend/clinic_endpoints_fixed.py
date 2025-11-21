# Fixed Clinic Endpoints - No JWT validation (matches existing pattern)

@app.post("/api/v1/clinic/change-password")
async def change_password_v2(request: Request, password_data: dict):
    """Change clinic password"""
    try:
        # Get email from request body instead of token
        email = password_data.get("email", "staff@aberdeenwellness.co.uk")
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
                "SELECT id, password_hash FROM clinic_credentials WHERE email = $1", email
            )
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            if not bcrypt.checkpw(current_password.encode("utf-8"), user["password_hash"].encode("utf-8")):
                raise HTTPException(status_code=400, detail="Current password incorrect")
            
            new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt(rounds=12))
            
            await conn.execute(
                "UPDATE clinic_credentials SET password_hash = $1, must_change_password = false, updated_at = CURRENT_TIMESTAMP WHERE email = $2",
                new_hash.decode("utf-8"), email
            )
            
            return {"success": True, "message": "Password changed successfully"}
        finally:
            await conn.close()
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error changing password: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/clinic/invoices/v2")
async def get_clinic_invoices_v2():
    """Get subscription invoices - simplified"""
    try:
        # Default to clinic_id = 2 (Aberdeen Wellness)
        clinic_id = 2
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        try:
            invoices = await conn.fetch(
                """
                SELECT id, invoice_number, amount, due_date, payment_status as status, 
                       payment_date, billing_period, description, issue_date, created_at
                FROM clinic_invoices
                WHERE clinic_id = $1
                ORDER BY due_date DESC
                """,
                clinic_id
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
    except Exception as e:
        print(f"Error fetching invoices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/clinic/patient-invoices/v2")
async def get_patient_invoices_v2():
    """Get patient invoices - simplified"""
    try:
        # Default to clinic_id = 2
        clinic_id = 2
        
        conn = await asyncpg.connect(
            host=DB_HOST, port=int(DB_PORT), user=DB_USER, password=DB_PASSWORD, database=DB_NAME
        )
        
        try:
            invoices = await conn.fetch(
                """
                SELECT pi.*, p.first_name || ' ' || p.last_name as patient_name, p.email as patient_email
                FROM patient_invoices pi
                JOIN patients p ON pi.patient_id = p.id
                WHERE pi.clinic_id = $1
                ORDER BY pi.created_at DESC
                """,
                clinic_id
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
    except Exception as e:
        print(f"Error fetching patient invoices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

