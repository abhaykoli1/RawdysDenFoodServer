from mongoengine import (
    Document, StringField, ListField, FloatField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField, IntField
)
from datetime import datetime
from pydantic import BaseModel
from typing import Literal, List

# ------------------- ITEM MODEL -------------------
class ItemModel(Document):
    name = StringField(required=True)
    image = StringField(required=True)
    price = FloatField(required=True)  # price as float
    cat_id = StringField(required=True)  # ideally ReferenceField for relational integrity

class ItemSchema(BaseModel):
    name: str
    image: str
    price: float
    cat_id: str


# ------------------- CATEGORY MODEL -------------------
class CategoryItemModel(Document):
    name = StringField(required=True)

class CategoryItemSchema(BaseModel):
    name: str


# ------------------- CART MODEL -------------------
class CartItem(EmbeddedDocument):
    item_id = StringField(required=True)
    quantity = FloatField(required=True)  # Use IntField if fractional quantities are not needed

class CartModel(Document):
    user_identifier = StringField(required=True, unique=True)  # user_id or session_id
    items = ListField(EmbeddedDocumentField(CartItem))
    updated_at = DateTimeField(default=datetime.utcnow)

# Pydantic Schemas
class CartItemSchema(BaseModel):
    item_id: str
    quantity: float  # matches MongoEngine FloatField

class CartSchema(BaseModel):
    user_identifier: str
    items: List[CartItemSchema]

# ------------------- ORDER MODEL -------------------
class OrderItemModel(EmbeddedDocument):
    item_id = StringField(required=True)
    quantity = FloatField(required=True)

class OrderModel(Document):
    user_name = StringField(required=True)
    phone = StringField(required=True)
    payment_method = StringField(required=True, choices=["cash", "upi"])
    items = ListField(EmbeddedDocumentField(OrderItemModel))
    total_amount = FloatField(required=True)
    order_status = StringField(default="pending", choices=["pending", "confirmed", "preparing", "delivered", "cancelled"])
    created_at = DateTimeField(default=datetime.utcnow)


# Pydantic Schemas for Orders
class OrderItem(BaseModel):
    item_id: str
    quantity: float  # matches MongoEngine

class OrderSchema(BaseModel):
    user_name: str
    phone: str
    payment_method: Literal["cash", "upi"]
    items: List[OrderItem]

class OrderStatusUpdate(BaseModel):
    order_status: Literal["pending", "confirmed", "preparing", "delivered", "cancelled"]


