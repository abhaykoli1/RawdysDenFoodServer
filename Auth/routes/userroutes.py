import json
import os
import traceback
import uuid
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from mongoengine import Document, StringField, DateTimeField, ReferenceField
from passlib.context import CryptContext
from pydantic import BaseModel
from dotenv import load_dotenv
from bson import ObjectId  # Import this if needed

from Auth.models.usermodel import UserModel, UserTable
from userRole.model.userRoleModel import UserRoleTable

load_dotenv()

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Environment Variables
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
APP_URL = os.getenv("APP_URL")

# Pending User Document
class PendingUserTable(Document):
    name = StringField(required=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    phone = StringField()
    country_code = StringField()
    role = StringField(default = "user")
    status = StringField(required=True, choices=("active", "inactive", "block"))
    verification_token = StringField(required=True, unique=True)
    created_at = DateTimeField(default=datetime.utcnow)

# Login Pydantic Schema

class LoginRequest(BaseModel):
    email: str
    password: str

# Utilities
def send_verification_email(email: str, token: str):
    subject = "Verify Your Email"
    verification_link = f"{APP_URL}/verify?token={token}"
    body = f"""
    Hello,

    Thank you for registering. Please verify your email by clicking on the link below:

    {verification_link}

    Best regards,
    Your App Team
    """

    msg = MIMEMultipart()
    msg["From"] = SMTP_EMAIL
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")

# Register
@router.post("/api/v1/register", status_code=201)
def register_user(user: UserModel):

    print(user)
    if UserTable.objects(email=user.email).first() or PendingUserTable.objects(email=user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists or pending verification")
    
    token = str(uuid.uuid4())
    hashed_password = pwd_context.hash(user.password)

    pending = PendingUserTable(
        name=user.name,
        email=user.email,
        password=hashed_password,
        phone=user.phone,
        country_code=user.country_code,
        role = "user" ,
        status=user.status,
        verification_token=token
    )
    pending.save()

    send_verification_email(user.email, token)
    return {"message": "Verification email sent. Please check your inbox."}

#veirfy
@router.get("/api/v1/verify", status_code=200)
def verify_user(token: str):
    try:

        pending = PendingUserTable.objects(verification_token=token).first()
        if not pending:
            raise HTTPException(status_code=400, detail="Invalid or expired verification token")

        user = UserTable(
            name=pending.name,
            email=pending.email,
            password=pending.password,
            phone=pending.phone,
            role = pending.role,
            country_code=pending.country_code,
            status=pending.status or "inactive",
            
        )
        user.save()
        pending.delete()

        return {
            "id": str(user.id),
            "name" : user.name,
            "email": user.email,
            "message": "Email verified successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Login
@router.post("/api/v1/login")
def login_user(req: LoginRequest):
    user = UserTable.objects(email=req.email).first()
    if not user or not pwd_context.verify(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "id": str(user.id),
        "email": user.email,
        "name" : user.name,
        "message": "Login successful"
    }

# Get User by ID
@router.get("/api/v1/user/{userId}")
def get_user(userId: str):
    try:
        user = UserTable.objects(id=ObjectId(userId)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "alternateMobile" : user.alternateMobile,
            "gender" : user.gender,
             "dob" : user.dob,
            "phone": user.phone,
            "country_code": user.country_code,
            "status": user.status,
            "created_at": user.created_at,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user ID format: {str(e)}")


# Update User by ID
@router.put("/api/v1/update_user/{userId}")
async def update_user(userId: str, data: UserModel):
    print("ID ==========", userId)
    print("Data ========>", data)

    try:
        user = UserTable.objects(id=ObjectId(userId)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # Update only the provided fields
        update_data = data.dict(exclude_unset=True)
        user.update(**update_data)

        updated = UserTable.objects.get(id=userId)

        return {
            "message": "User updated successfully",
            "data": json.loads(updated.to_json())
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Delete user by userId
@router.delete("/api/v1/delete-user/{userId}")
async def delete_user(userId: str):
    
    try:
        user = UserTable.objects(id=ObjectId(userId)).first()
        if not user:
            raise HTTPException(status_code=404, detail="user not found")
        user.delete()
        return {
            "message": "user deleted successfully",
            "status": 200
        }
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Get All Users
@router.get("/api/v1/users")
def all_users():
    users = UserTable.objects.all()
    return {
        "count": len(users),
        "data": [
            {
                "user_id": str(u.id),
                "name": u.name,
                "email": u.email,
                "phone": u.phone,
                "country_code": u.country_code,
                "address": u.address,
                "role" : u.role,
                "alternateMobile" : u.alternateMobile,
                "gender" : u.gender,
                "dob" : u.dob,
                "status": u.status,
                "created_at": u.created_at,
            }
            for u in users
        ]
    }

