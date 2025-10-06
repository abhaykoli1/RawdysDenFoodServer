from mongoengine import Document, StringField, ListField, ReferenceField, DateTimeField, BooleanField
from datetime import datetime
from product.model.productModel import Product  # import your Product model
from pydantic import BaseModel
from typing import List, Optional



class Wishlist(Document):
    user_id = StringField(required=True)  # assuming user ID is a string (from auth)
    products = ListField(ReferenceField(Product))  # store references to Product documents
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'wishlists',
        'indexes': [
            'user_id',  
        ]
    }


class WishlistItemSchema(BaseModel):
    product_id: str

class WishlistCreateSchema(BaseModel):
    user_id: str
    product_id: str

class WishlistResponseSchema(BaseModel):
    user_id: str
    products: List[str]  # list of product IDs
    created_at: datetime
    updated_at: datetime