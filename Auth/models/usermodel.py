from mongoengine import Document, StringField, DateTimeField, ReferenceField
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from userRole.model.userRoleModel import UserRoleTable

# MongoDB Model
class UserTable(Document):
    name = StringField(required=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=False)
    country_code = StringField(required=False)
    role = StringField(required=True , default="user")
    phone = StringField(required=True)
    alternateMobile = StringField(required=False)
    dob= StringField(required=False)
    gender = StringField(required=False)
    address = StringField(required=False)
    status = StringField(required=False, choices=("active", "inactive", "block"))
    created_at = DateTimeField(default=datetime.utcnow)

# Pydantic Model
class UserModel(BaseModel):
    name: str
    email: str
    password: Optional[str] = None
    status: Optional[str] = None
    alternateMobile : Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    dob : Optional[str] = None
    role:  Optional[str] = None
    phone: Optional[str] = None
    country_code: Optional[str] = None
    created_at: Optional[datetime] = None
