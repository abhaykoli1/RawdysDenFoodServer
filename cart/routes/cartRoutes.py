# cart/routes/cartRoutes.py
from product.model.productModel import Product
from cart.model.cartmodel import CartModel,CartTable
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from Auth.models.usermodel import UserTable
from bson import ObjectId
from mongoengine.errors import DoesNotExist
from pydantic import BaseModel
from typing import List, Optional


class ProductInCartSchema(BaseModel):
    id: str
    title: str
    description: Optional[str]
    base_price: float
    sale_price: Optional[float]
    images: List[str]
    category: Optional[str]
    brand: Optional[str]
    total_stock: Optional[int]
    # average_review: Optional[float]
    Status: bool

class CartWithProductSchema(BaseModel):
    cart_id: str 
    user_id: str
    product: ProductInCartSchema
    quantity: int
router = APIRouter()

# ---------------- Add to Cart ---------------- #
@router.post("/api/v1/cart", response_model=CartModel)
async def add_to_cart(cart_item: CartModel):
    try:
        user = UserTable.objects.get(id=cart_item.user_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Convert string ID to ObjectId
        product = Product.objects.get(id=ObjectId(cart_item.product_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if already in cart
    existing_item = CartTable.objects(user_id=user, product_id=product).first()
    if existing_item:
        existing_item.quantity += cart_item.quantity
        existing_item.updated_at = datetime.utcnow()
        existing_item.save()
        return CartModel(
            user_id=str(existing_item.user_id.id),
            product_id=str(existing_item.product_id.id),
            quantity=existing_item.quantity
        )
    
    # Create new cart item
    new_cart = CartTable(
        user_id=user,
        product_id=product,
        quantity=cart_item.quantity
    )
    new_cart.save()
    
    return CartModel(
        user_id=str(new_cart.user_id.id),
        product_id=str(new_cart.product_id.id),
        quantity=new_cart.quantity
    )


# ---------------- Get User Cart ---------------- #
@router.get("/api/v1/cart/{user_id}", response_model=List[CartWithProductSchema])
async def get_user_cart(user_id: str):
    try:
        user = UserTable.objects.get(id=user_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    cart_items = CartTable.objects(user_id=user)
    result = []

    for item in cart_items:
        try:
            product = Product.objects.get(id=item.product_id.id)
        except DoesNotExist:
            continue  # skip if product deleted

        product_data = ProductInCartSchema(
            id=str(product.id),
            title=product.title,
            description=product.description,
            base_price=product.base_price,
            sale_price=product.sale_price,
            images=product.images,
            category=str(product.category.id) if product.category else None,
            brand=product.brand,
            total_stock=product.total_stock,
            # average_review=product.average_review,
            Status=product.Status
        )

        result.append(
            CartWithProductSchema(
                cart_id=str(item.id),
                user_id=str(item.user_id.id),
                product=product_data,
                quantity=item.quantity
            )
        )

    return result


# ---------------- Update Cart Item ---------------- #
@router.put("/api/v1/cart/{cart_id}", response_model=CartModel)
async def update_cart_item(cart_id: str, cart_item: CartModel):
    try:
        cart = CartTable.objects.get(id=cart_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if cart_item.quantity <= 0:
        cart.delete()
        raise HTTPException(status_code=200, detail="Cart item deleted because quantity <= 0")

    cart.quantity = cart_item.quantity
    cart.updated_at = datetime.utcnow()
    cart.save()
    return CartModel(
        user_id=str(cart.user_id.id),
        product_id=str(cart.product_id.id),
        quantity=cart.quantity
    )


# ---------------- Delete Cart Item ---------------- #
@router.delete("/api/v1/cart/{cart_id}")
async def delete_cart_item(cart_id: str):
    try:
        cart = CartTable.objects.get(id=cart_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Cart item not found")

    cart.delete()
    return {"detail": "Cart item deleted successfully"}


# ---------------- Clear User Cart ---------------- #
@router.delete("/api/v1/cart/clear/{user_id}")
async def clear_user_cart(user_id: str):
    try:
        user = UserTable.objects.get(id=user_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    CartTable.objects(user_id=user).delete()
    return {"detail": "All cart items cleared for this user"}
