from http.client import InvalidURL
import json
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from mongoengine.errors import DoesNotExist, ValidationError
from pydantic import BaseModel
from typing import Literal, List
from bson import ObjectId

from items.models.itemsModel import (
    CartItem, CartModel, CartSchema, CategoryItemModel, CategoryItemSchema, ItemModel, ItemSchema,
    OrderModel, OrderStatusUpdate, OrderSchema, OrderItem, OrderItemModel
)

class CartOrderSchema(BaseModel):
    user_name: str
    phone: str
    payment_method: Literal["cash", "upi"]

class OrderStatusUpdateSchema(BaseModel):
    # order_status: Literal["pending", "inprocess", "complete"]
    order_status: Literal["pending", "confirmed", "preparing", "delivered", "cancelled"]

# ------------------- Router -------------------
router = APIRouter(prefix="/api/v1")

# ------------------- CATEGORY CRUD -------------------
@router.post("/category", response_model=dict)
async def create_category(category: CategoryItemSchema):
    try:
        cat = CategoryItemModel(name=category.name)
        cat.save()
        return {"message": "Category created successfully", "id": str(cat.id)}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/category", response_model=List[dict])
async def get_all_categories():
    categories = CategoryItemModel.objects()
    return [{"id": str(cat.id), "name": cat.name} for cat in categories]


@router.get("/category/{cat_id}", response_model=dict)
async def get_category_by_id(cat_id: str):
    try:
        cat = CategoryItemModel.objects.get(id=cat_id)
        return {"id": str(cat.id), "name": cat.name}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Category not found")


@router.put("/category/{cat_id}", response_model=dict)
async def update_category(cat_id: str, category: CategoryItemSchema):
    try:
        cat = CategoryItemModel.objects.get(id=cat_id)
        cat.name = category.name
        cat.save()
        return {"message": "Category updated successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Category not found")


@router.delete("/category/{cat_id}", response_model=dict)
async def delete_category(cat_id: str):
    try:
        cat = CategoryItemModel.objects.get(id=cat_id)
        cat.delete()
        return {"message": "Category deleted successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Category not found")


# ------------------- ITEM CRUD -------------------
@router.post("/items", response_model=dict)
async def create_item(item: ItemSchema):
    if not CategoryItemModel.objects(id=item.cat_id).first():
        raise HTTPException(status_code=404, detail="Category not found")

    new_item = ItemModel(
        name=item.name,
        image=item.image,
        price=item.price,
        cat_id=item.cat_id
    )
    new_item.save()
    return {"message": "Item created successfully", "id": str(new_item.id)}


@router.get("/items", response_model=List[dict])
async def get_all_items():
    items = ItemModel.objects()
    return [
        {
            "id": str(i.id),
            "name": i.name,
            "image": i.image,
            "price": i.price,
            "cat_id": i.cat_id
        }
        for i in items
    ]



@router.get("/items/{item_id}", response_model=dict)
async def get_item_by_id(item_id: str):
    print("Received item_id:", item_id)
    try:
        # Try to fetch the item by ID
        item = ItemModel.objects.get(id=item_id)
        return {
            "id": str(item.id),
            "name": item.name,
            "image": item.image,
            "price": item.price,
            "cat_id": str(item.cat_id.id) if item.cat_id else None
        }
    
    # Handle case when ID format is invalid (not a valid ObjectId)
    except (InvalidURL, ValidationError):
        raise HTTPException(status_code=400, detail="Invalid item ID format.")
    
    # Handle case when no item is found
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Item not found.")
    
    # Handle any other unexpected errors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.put("/{item_id}", response_model=dict)
async def update_item(item_id: str, item: ItemSchema):
    if not CategoryItemModel.objects(id=item.cat_id).first():
        raise HTTPException(status_code=404, detail="Category not found")

    try:
        existing = ItemModel.objects.get(id=item_id)
        existing.name = item.name
        existing.image = item.image
        existing.price = item.price
        existing.cat_id = item.cat_id
        existing.save()
        return {"message": "Item updated successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/items/{item_id}", response_model=dict)
async def delete_item(item_id: str):
    try:
        item = ItemModel.objects.get(id=item_id)
        item.delete()
        return {"message": "Item deleted successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Item not found")


# ------------------- CART CRUD -------------------
@router.post("/cart", response_model=dict)
async def create_or_update_cart(cart_data: CartSchema):
    cart = CartModel.objects(user_identifier=cart_data.user_identifier).first()
    items = [CartItem(item_id=i.item_id, quantity=i.quantity) for i in cart_data.items]

    if cart:
        cart.items = items
        cart.updated_at = datetime.utcnow()
        cart.save()
        return {"message": "Cart updated successfully"}
    else:
        new_cart = CartModel(user_identifier=cart_data.user_identifier, items=items)
        new_cart.save()
        return {"message": "Cart created successfully"}

@router.get("/cart/{user_identifier}", response_model=dict)
async def get_cart(user_identifier: str):
    cart = CartModel.objects(user_identifier=user_identifier).first()
    if not cart:
        return {"items": [], "total_amount": 0}

    cart_items = []
    for c in cart.items:
        item = ItemModel.objects(id=c.item_id).first()
        if item:
            cart_items.append({
                "item_id": str(item.id),
                "name": item.name,
                "image": item.image,
                "price": item.price,
                "quantity": c.quantity
            })

    total_amount = sum(i["price"] * i["quantity"] for i in cart_items)
    return {"items": cart_items, "total_amount": total_amount}

@router.put("/cart/{user_identifier}/item/{item_id}/increment", response_model=dict)
async def increment_cart_item(user_identifier: str, item_id: str):
    cart = CartModel.objects(user_identifier=user_identifier).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    item_found = False
    for c in cart.items:
        if c.item_id == item_id:
            c.quantity += 1
            item_found = True
            break

    if not item_found:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    cart.updated_at = datetime.utcnow()
    cart.save()
    return {"message": "Item quantity incremented successfully"}

@router.put("/cart/{user_identifier}/item/{item_id}/decrement", response_model=dict)
async def decrement_cart_item(user_identifier: str, item_id: str):
    cart = CartModel.objects(user_identifier=user_identifier).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    item_found = False
    for c in cart.items:
        if c.item_id == item_id:
            if c.quantity <= 1:
                # Remove item if quantity goes below 1
                cart.items = [i for i in cart.items if i.item_id != item_id]
            else:
                c.quantity -= 1
            item_found = True
            break

    if not item_found:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    cart.updated_at = datetime.utcnow()
    cart.save()
    return {"message": "Item quantity decremented successfully"}


@router.delete("/cart/{user_identifier}/item/{item_id}", response_model=dict)
async def remove_cart_item(user_identifier: str, item_id: str):
    cart = CartModel.objects(user_identifier=user_identifier).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    cart.items = [i for i in cart.items if i.item_id != item_id]
    cart.save()
    return {"message": "Item removed from cart"}

@router.delete("/cart/{user_identifier}", response_model=dict)
async def clear_cart(user_identifier: str):
    cart = CartModel.objects(user_identifier=user_identifier).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    cart.delete()
    return {"message": "Cart cleared successfully"}


# ------------------- PLACE ORDER -------------------
class CartOrderSchema(BaseModel):
    user_name: str
    phone: str
    payment_method: Literal["cash", "upi"]


@router.post("/cart/{user_identifier}/order", response_model=dict)
async def order_from_cart(user_identifier: str, order_data: CartOrderSchema):
    cart = CartModel.objects(user_identifier=user_identifier).first()
    if not cart or len(cart.items) == 0:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order_items = []
    total_amount = 0
    for c in cart.items:
        item = ItemModel.objects(id=c.item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item not found: {c.item_id}")
        total_amount += item.price * c.quantity
        order_items.append(OrderItemModel(item_id=c.item_id, quantity=c.quantity))

    order = OrderModel(
        user_name=order_data.user_name,
        phone=order_data.phone,
        payment_method=order_data.payment_method,
        items=order_items,
        total_amount=total_amount
    )
    order.save()
    cart.delete()
    return {"message": "Order placed successfully", "order_id": str(order.id), "total_amount": total_amount}



# ------------------- GET ALL ORDERS -------------------
@router.get("/order/all", response_model=List[dict])
async def get_all_orders():
    orders = OrderModel.objects().order_by("-created_at")
    return [
        {
            "id": str(o.id),
            "user_name": o.user_name,
            "phone": o.phone,
            "payment_method": o.payment_method,
            "total_amount": o.total_amount,
            "order_status": o.order_status,
            "created_at": o.created_at
        }
        for o in orders
    ]

# ------------------- GET ORDER BY ID -------------------
@router.get("/order/{order_id}", response_model=dict)
async def get_order_by_id(order_id: str):
    try:
        order = OrderModel.objects.get(id=order_id)
        return {
            "id": str(order.id),
            "user_name": order.user_name,
            "phone": order.phone,
            "payment_method": order.payment_method,
            "items": [{"item_id": i.item_id, "quantity": i.quantity} for i in order.items],
            "total_amount": order.total_amount,
            "order_status": order.order_status,
            "created_at": order.created_at
        }
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Order not found")


# ------------------- UPDATE ORDER STATUS -------------------
@router.put("/order/{order_id}/status", response_model=dict)
async def update_order_status(order_id: str, status_update: OrderStatusUpdateSchema):
    # ✅ validate ObjectId
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    try:
        order = OrderModel.objects.get(id=ObjectId(order_id))
        order.order_status = status_update.order_status
        order.save()

        return {
            "message": "Order status updated successfully",
            "order_id": str(order.id),
            "status": order.order_status,
        }

    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Order not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
# ------------------- DELETE ORDER -------------------
@router.delete("/order/{order_id}", response_model=dict)
async def delete_order(order_id: str):
    try:
        order = OrderModel.objects.get(id=order_id)
        order.delete()
        return {"message": "Order deleted successfully", "order_id": order_id}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Order not found")
    
# ------------------- GET PENDING & INPROCESS ORDERS -------------------
@router.get("/order/pending-inprocess", response_model=List[dict])
async def get_pending_inprocess_orders():
    orders = OrderModel.objects(order_status__in=["pending", "inprocess"]).order_by("-created_at")
    return [
        {
            "id": str(o.id),
            "user_name": o.user_name,
            "phone": o.phone,
            "payment_method": o.payment_method,
            "total_amount": o.total_amount,
            "order_status": o.order_status,
            "created_at": o.created_at
        }
        for o in orders
    ]

# ------------------- GET COMPLETED ORDERS -------------------
@router.get("/order/complete", response_model=List[dict])
async def get_completed_orders():
    orders = OrderModel.objects(order_status="complete").order_by("-created_at")
    return [
        {
            "id": str(o.id),
            "user_name": o.user_name,
            "phone": o.phone,
            "payment_method": o.payment_method,
            "total_amount": o.total_amount,
            "order_status": o.order_status,
            "created_at": o.created_at
        }
        for o in orders
    ]
# ------------------- ORDER CRUD -------------------
# @router.post("/order", response_model=dict)
# async def create_order(order: OrderSchema):
#     if not order.items:
#         raise HTTPException(status_code=400, detail="Order must contain at least one item")

#     order_items = []
#     total = 0
#     for oi in order.items:
#         item = ItemModel.objects(id=oi.item_id).first()
#         if not item:
#             raise HTTPException(status_code=404, detail=f"Item not found: {oi.item_id}")
#         total += item.price * oi.quantity
#         order_items.append(OrderItemModel(item_id=oi.item_id, quantity=oi.quantity))

#     new_order = OrderModel(
#         user_name=order.user_name,
#         phone=order.phone,
#         payment_method=order.payment_method,
#         items=order_items,
#         total_amount=total
#     )
#     new_order.save()
#     return {"message": "Order placed successfully", "order_id": str(new_order.id), "total_amount": total, "status": new_order.order_status}


# @router.put("/order/{order_id}/status", response_model=dict)
# async def update_order_status(order_id: str, status_update: OrderStatusUpdate):
#     try:
#         order = OrderModel.objects.get(id=order_id)
#         order.order_status = status_update.order_status
#         order.save()
#         return {"message": "Order status updated", "status": order.order_status}
#     except DoesNotExist:
#         raise HTTPException(status_code=404, detail="Order not found")


# @router.get("/order/all", response_model=List[dict])
# async def get_all_orders():
#     orders = OrderModel.objects().order_by("-created_at")
#     return [
#         {
#             "id": str(o.id),
#             "user_name": o.user_name,
#             "phone": o.phone,
#             "payment_method": o.payment_method,
#             "total_amount": o.total_amount,
#             "order_status": o.order_status,
#             "created_at": o.created_at
#         }
#         for o in orders
#     ]


# @router.get("/order/pending-inprocess", response_model=List[dict])
# async def get_pending_inprocess_orders():
#     orders = OrderModel.objects(order_status__in=["pending", "inprocess"]).order_by("-created_at")
#     return [
#         {
#             "id": str(o.id),
#             "user_name": o.user_name,
#             "phone": o.phone,
#             "payment_method": o.payment_method,
#             "total_amount": o.total_amount,
#             "order_status": o.order_status,
#             "created_at": o.created_at
#         }
#         for o in orders
#     ]


# @router.get("/order/complete", response_model=List[dict])
# async def get_completed_orders():
#     orders = OrderModel.objects(order_status="complete").order_by("-created_at")
#     return [
#         {
#             "id": str(o.id),
#             "user_name": o.user_name,
#             "phone": o.phone,
#             "payment_method": o.payment_method,
#             "total_amount": o.total_amount,
#             "order_status": o.order_status,
#             "created_at": o.created_at
#         }
#         for o in orders
#     ]


# @router.get("/order/{order_id}", response_model=dict)
# async def get_order_by_id(order_id: str):
#     try:
#         order = OrderModel.objects.get(id=order_id)
#         return {
#             "id": str(order.id),
#             "user_name": order.user_name,
#             "phone": order.phone,
#             "payment_method": order.payment_method,
#             "items": [{"item_id": i.item_id, "quantity": i.quantity} for i in order.items],
#             "total_amount": order.total_amount,
#             "order_status": order.order_status,
#             "created_at": order.created_at
#         }
#     except DoesNotExist:
#         raise HTTPException(status_code=404, detail="Order not found")


# @router.delete("/order/{order_id}", response_model=dict)
# async def delete_order(order_id: str):
#     try:
#         order = OrderModel.objects.get(id=order_id)
#         order.delete()
#         return {"message": "Order deleted successfully"}
#     except DoesNotExist:
#         raise HTTPException(status_code=404, detail="Order not found")
