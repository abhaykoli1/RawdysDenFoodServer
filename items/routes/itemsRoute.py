from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from mongoengine.errors import DoesNotExist, ValidationError

from items.models.itemsModel import (
    ItemModel, ItemSchema,
    CatagroryItemModel, CategoryItemSchems,
    OrderModel, OrderStatusUpdate, OrderSchema, OrderItem, OrderItemModel
)

from pydantic import BaseModel
from typing import Literal


# ------------------- Pydantic Schemas -------------------




# ------------------- Router -------------------

router = APIRouter(prefix="/api/v1/items", tags=["Items, Categories & Orders"])


# ------------------- CATEGORY CRUD -------------------

@router.post("/category", response_model=dict)
async def create_category(category: CategoryItemSchems):
    try:
        cat = CatagroryItemModel(name=category.name)
        cat.save()
        return {"message": "Category created successfully", "id": str(cat.id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/category", response_model=List[dict])
async def get_all_categories():
    categories = CatagroryItemModel.objects()
    return [{"id": str(cat.id), "name": cat.name} for cat in categories]


@router.get("/category/{cat_id}", response_model=dict)
async def get_category_by_id(cat_id: str):
    try:
        cat = CatagroryItemModel.objects.get(id=cat_id)
        return {"id": str(cat.id), "name": cat.name}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Category not found")


@router.put("/category/{cat_id}", response_model=dict)
async def update_category(cat_id: str, category: CategoryItemSchems):
    try:
        cat = CatagroryItemModel.objects.get(id=cat_id)
        cat.name = category.name
        cat.save()
        return {"message": "Category updated successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Category not found")


@router.delete("/category/{cat_id}", response_model=dict)
async def delete_category(cat_id: str):
    try:
        cat = CatagroryItemModel.objects.get(id=cat_id)
        cat.delete()
        return {"message": "Category deleted successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Category not found")


# ------------------- ITEM CRUD -------------------

@router.post("/", response_model=dict)
async def create_item(item: ItemSchema):
    try:
        if not CatagroryItemModel.objects(id=item.cat_id).first():
            raise HTTPException(status_code=404, detail="Category not found")

        new_item = ItemModel(
            name=item.name,
            image=item.image,
            price=item.price,
            cat_id=item.cat_id
        )
        new_item.save()
        return {"message": "Item created successfully", "id": str(new_item.id)}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[dict])
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


@router.get("/{item_id}", response_model=dict)
async def get_item_by_id(item_id: str):
    try:
        item = ItemModel.objects.get(id=item_id)
        return {
            "id": str(item.id),
            "name": item.name,
            "image": item.image,
            "price": item.price,
            "cat_id": item.cat_id
        }
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Item not found")


@router.put("/{item_id}", response_model=dict)
async def update_item(item_id: str, item: ItemSchema):
    try:
        if not CatagroryItemModel.objects(id=item.cat_id).first():
            raise HTTPException(status_code=404, detail="Category not found")

        existing = ItemModel.objects.get(id=item_id)
        existing.name = item.name
        existing.image = item.image
        existing.price = item.price
        existing.cat_id = item.cat_id
        existing.save()
        return {"message": "Item updated successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/{item_id}", response_model=dict)
async def delete_item(item_id: str):
    try:
        item = ItemModel.objects.get(id=item_id)
        item.delete()
        return {"message": "Item deleted successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Item not found")


# ------------------- ORDER CRUD -------------------

@router.post("/order", response_model=dict)
async def create_order(order: OrderSchema):
    try:
        if not order.items:
            raise HTTPException(status_code=400, detail="Order must contain at least one item")

        total = 0
        order_items = []

        for order_item in order.items:
            item = ItemModel.objects(id=order_item.item_id).first()
            if not item:
                raise HTTPException(status_code=404, detail=f"Item not found: {order_item.item_id}")

            item_price = float(item.price)
            line_total = item_price * order_item.quantity
            total += line_total

            order_items.append({
                "item_id": order_item.item_id,
                "quantity": order_item.quantity
            })

        new_order = OrderModel(
            user_name=order.user_name,
            phone=order.phone,
            payment_method=order.payment_method,
            items=order_items,
            total_amount=total
        )
        new_order.save()

        return {
            "message": "Order placed successfully",
            "order_id": str(new_order.id),
            "total_amount": total,
            "status": new_order.order_status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/order/{order_id}/status", response_model=dict)
async def update_order_status(order_id: str, status_update: OrderStatusUpdate):
    try:
        order = OrderModel.objects.get(id=order_id)
        order.order_status = status_update.order_status
        order.save()
        return {"message": "Order status updated", "status": order.order_status}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Order not found")


@router.get("/order", response_model=List[dict])
async def get_all_orders():
    orders = OrderModel.objects().order_by("-created_at")
    return [
        {
            "id": str(o.id),
            "user_name": o.user_name,
            "phone": o.phone,
            "payment_method": o.payment_method,
            "items": o.items,
            "total_amount": o.total_amount,
            "order_status": o.order_status,
            "created_at": o.created_at
        }
        for o in orders
    ]


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


@router.get("/order/{order_id}", response_model=dict)
async def get_order_by_id(order_id: str):
    try:
        order = OrderModel.objects.get(id=order_id)
        return {
            "id": str(order.id),
            "user_name": order.user_name,
            "phone": order.phone,
            "payment_method": order.payment_method,
            "items": order.items,
            "total_amount": order.total_amount,
            "order_status": order.order_status,
            "created_at": order.created_at
        }
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Order not found")


@router.delete("/order/{order_id}", response_model=dict)
async def delete_order(order_id: str):
    try:
        order = OrderModel.objects.get(id=order_id)
        order.delete()
        return {"message": "Order deleted successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Order not found")
