from Auth.models.usermodel import UserTable

from product.model.productModel import Product
from mongoengine import Document, ReferenceField, IntField, DateTimeField
from datetime import datetime
from pydantic import BaseModel


class CartTable(Document):
    user_id = ReferenceField(UserTable, required=True)
    product_id = ReferenceField(Product, required=True)
    quantity = IntField(required=True, default=1)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    meta = {"collection": "carts"}


class CartModel(BaseModel):
    user_id: str
    product_id: str
    quantity: int = 1
