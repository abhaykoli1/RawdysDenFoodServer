from fastapi import APIRouter, HTTPException
from order.model.orderModel import Order, OrderItem, Address, Payment ,OrderCreateSchema
from bson import ObjectId
from datetime import datetime

router = APIRouter()


@router.post("/api/v1/create-order")
def create_order(order_data: OrderCreateSchema):
    # Prepare embedded items
    items = [
        OrderItem(
            product_id=ObjectId(item.product_id),
            quantity=item.quantity,
            price=item.price,
            sku=item.sku,
            name=item.name
        )
        for item in order_data.items
    ]

    # Prepare addresses
    shipping_address = Address(**order_data.shipping_address.dict())
    billing_address = Address(**order_data.billing_address.dict())

    # Prepare payment
    payment = Payment(**order_data.payment.dict())

    # Calculate total price (items + tax + shipping - discount)
    subtotal = sum(item.price * item.quantity for item in items)
    total_price = subtotal + order_data.tax + order_data.shipping_fee - order_data.discount

    order = Order(
        user_id=ObjectId(order_data.user_id),
        items=items,
        shipping_address=shipping_address,
        billing_address=billing_address,
        payment=payment,
        total_price=total_price,
        discount=order_data.discount,
        tax=order_data.tax,
        shipping_fee=order_data.shipping_fee,
        notes=order_data.notes,
        status="pending",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    try:
        order.save()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": 200, "message": "Order created successfully", "order_id": str(order.id)}
