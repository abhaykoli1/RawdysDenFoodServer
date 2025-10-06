from fastapi import APIRouter, HTTPException
from wishlist.models.wishlistmodel import Wishlist, WishlistCreateSchema
from product.model.productModel import Product
from bson import ObjectId
from datetime import datetime

router = APIRouter()

# ➕ Add product to wishlist
@router.post("/api/v1/wishlist/add")
async def add_to_wishlist(body: WishlistCreateSchema):
    try:
        user_id = body.user_id
        product_id = body.product_id

        product = Product.objects(id=ObjectId(product_id)).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        wishlist = Wishlist.objects(user_id=user_id).first()
        if not wishlist:
            wishlist = Wishlist(user_id=user_id, products=[product])
        else:
            if product not in wishlist.products:
                wishlist.products.append(product)

        wishlist.updated_at = datetime.utcnow()
        wishlist.save()

        return {"message": "Product added to wishlist", "status": 200, "product_id": product_id}

    except Exception as e:
        print("Error adding to wishlist:", e)
        raise HTTPException(status_code=500, detail="Failed to add product to wishlist")


# ❌ Remove product from wishlist
@router.delete("/api/v1/wishlist/remove")
async def remove_from_wishlist(user_id: str, product_id: str):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")

    wishlist = Wishlist.objects(user_id=user_id).first()
    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    # Filter products
    wishlist.products = [p for p in wishlist.products if str(p.id) != product_id]
    wishlist.updated_at = datetime.utcnow()
    wishlist.save()

    return {"message": "Product removed from wishlist", "status": 200}

# 📥 Get all products in a user's wishlist
@router.get("/api/v1/wishlist/{userId}")
async def get_wishlist(userId: str):
    wishlist = Wishlist.objects(user_id=userId).first()
    if not wishlist or not wishlist.products:
        return {"message": "Wishlist is empty", "data": [], "status": 200}

    product_list = []
    for product in wishlist.products:
        product_list.append({
            "id": str(product.id),
            "title": product.title,
            "url_slug" : product.url_slug,
            "brand": product.brand,
            "base_price": product.base_price,
            "sale_price": product.sale_price,
            "images": product.images,
            # "average_review": product.average_review,
            "Status": product.Status
        })

    return {"message": "Wishlist fetched successfully", "data": product_list, "status": 200}
