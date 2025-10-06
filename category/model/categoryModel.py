from mongoengine import Document, StringField ,DateTimeField ,BooleanField
from pydantic import BaseModel ,EmailStr
from datetime import datetime
from typing import Optional

# MongoDB Model
class CategoryTable(Document):
    category_name = StringField(required=True)
    url_slug = StringField(required=True, unique=True)
    # parent_cat_id = StringField(required=True)
    Status = BooleanField(required=True) # active / inactive
    created_at = DateTimeField(default=datetime.utcnow , required=False)

# Pydantic Model
class CategoryModel(BaseModel):
    category_name : str
    url_slug :str
    # parent_cat_id :str
    Status: bool
    created_at: datetime = None