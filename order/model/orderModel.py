
from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    ListField,
    ReferenceField,
    StringField,
    FloatField,
    IntField,
    DateTimeField,
    BooleanField
)


from datetime import datetime
from product.model.productModel import Product
from Auth.models.usermodel import UserTable
from pydantic import BaseModel
from typing import List, Optional
from address.model.addressModel import Address, AddressSchema




class Payment(EmbeddedDocument):
    payment_method = StringField(required=True)
    transaction_id = StringField()
    paid = BooleanField(default=False)
    payment_date = DateTimeField()


class OrderItem(EmbeddedDocument):
    product_id = ReferenceField(Product, required=True)
    quantity = IntField(required=True, min_value=1)
    price = FloatField(required=True, min_value=0)
    sku = StringField()
    name = StringField(required=True)


class Order(Document):
    user_id = ReferenceField(UserTable, required=True)
    items = ListField(EmbeddedDocumentField(OrderItem), required=True)
    
    shipping_address = EmbeddedDocumentField(Address, required=True)
    billing_address = EmbeddedDocumentField(Address, required=True)
    
    payment = EmbeddedDocumentField(Payment, required=True)
    
    total_price = FloatField(required=True, min_value=0)
    discount = FloatField(default=0)       # optional
    tax = FloatField(default=0)            # optional
    shipping_fee = FloatField(default=0)   # optional
    notes = StringField()                  # optional
    
    status = StringField(
        choices=["pending", "processing", "shipped", "delivered", "canceled"],
        default="pending"
    )
    
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {"collection": "orders"}



class PaymentSchema(BaseModel):
    payment_method: str
    transaction_id: Optional[str] = None
    paid: bool = False
    payment_date: Optional[datetime] = None


class OrderItemSchema(BaseModel):
    product_id: str
    quantity: int
    price: float
    sku: Optional[str] = None
    name: str


class OrderCreateSchema(BaseModel):
    user_id: str
    items: List[OrderItemSchema]
    shipping_address: AddressSchema
    billing_address: AddressSchema
    payment: PaymentSchema
    discount: Optional[float] = 0
    tax: Optional[float] = 0
    shipping_fee: Optional[float] = 0
    notes: Optional[str] = None