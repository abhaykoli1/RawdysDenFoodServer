from mongoengine import Document, StringField ,DateTimeField
from pydantic import BaseModel ,EmailStr
from datetime import datetime
from typing import Optional

# MongoDB Model
class UserRoleTable(Document):
    user_role = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

# Pydantic Model
class UserRoleModel(BaseModel):
    user_role : str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None