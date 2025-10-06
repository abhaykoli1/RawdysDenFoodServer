from mongoengine import Document, StringField, ListField, FloatField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField
from pydantic import BaseModel
from datetime import datetime

from typing import List, Literal


# ------------------- ITEM MODEL -------------------
class ItemModel(Document):
    name = StringField(required=True)
    image = StringField(required=True)
    price = StringField(required=True)
    cat_id = StringField(required=True)


class ItemSchema(BaseModel):
    name: str
    image: str
    price: str
    cat_id: str


# ------------------- CATEGORY MODEL -------------------
class CatagroryItemModel(Document):
    name = StringField(required=True)


class CategoryItemSchems(BaseModel):
    name: str


# ------------------- ORDER MODEL -------------------

class OrderItem(BaseModel):
    item_id: str
    quantity: int

class OrderSchema(BaseModel):
    user_name: str
    phone: str
    payment_method: Literal["cash", "upi"]
    items: List[OrderItem]



class OrderItemModel(EmbeddedDocument):
    item_id = StringField(required=True)
    quantity = FloatField(required=True)

class OrderModel(Document):
    user_name = StringField(required=True)
    phone = StringField(required=True)
    payment_method = StringField(required=True, choices=["cash", "upi"])
    items = ListField(EmbeddedDocumentField(OrderItemModel))  # Changed from ListField(StringField)
    total_amount = FloatField(required=True)
    order_status = StringField(default="pending", choices=["pending", "inprocess", "complete"])
    created_at = DateTimeField(default=datetime.utcnow)


class OrderStatusUpdate(BaseModel):
    order_status: Literal["pending", "inprocess", "complete"]
