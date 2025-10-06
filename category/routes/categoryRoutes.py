from datetime import datetime
from fastapi import APIRouter, HTTPException
from category.model.categoryModel import CategoryTable, CategoryModel
from bson import ObjectId

router = APIRouter()

# ➕ Add New Category
@router.post("/api/v1/category")
async def create_category(body: CategoryModel):
    try:
        category = CategoryTable(
            category_name=body.category_name,
            url_slug=body.url_slug,
            # parent_cat_id=body.parent_cat_id,
            Status=body.Status,
            created_at=body.created_at or datetime.utcnow()
        )
        category.save()
        return {"message": "Category added successfully", "status": 201}
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Failed to create category")


# 📥 Get All Categories
@router.get("/api/v1/categories")
async def get_all_categories():
    try:
        categories = CategoryTable.objects()
        category_list = []

        for cat in categories:
            cat_dict = {
                "id": str(cat.id),
                "category_name": cat.category_name,
                "url_slug": cat.url_slug,
                # "parent_cat_id": cat.parent_cat_id,
                "Status": cat.Status,
                "created_at": cat.created_at.isoformat() if cat.created_at else None
            }
            category_list.append(cat_dict)

        return {
            "message": "All categories fetched successfully",
            "data": category_list,
            "status": 200
        }

    except Exception as e:
        print(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



# 🔍 Get Category by ID
@router.get("/api/v1/category/{category_id}")
async def get_category_by_id(category_id: str):
    try:
        category = CategoryTable.objects(id=ObjectId(category_id)).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        # Convert to JSON-safe dictionary
        category_data = category.to_mongo().to_dict()
        category_data["_id"] = str(category_data["_id"])

        return {"data": category_data, "status": 200}
    except Exception as e:
        print("Error fetching category by ID:", e)
        raise HTTPException(status_code=500, detail="Error fetching category by ID")

        
# ✏️ Update Category by ID
@router.put("/api/v1/category/{category_id}")
async def update_category(category_id: str, body: CategoryModel):
    try:
        category = CategoryTable.objects(id=ObjectId(category_id)).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        category.update(
            category_name=body.category_name,
            url_slug=body.url_slug,
            # parent_cat_id=body.parent_cat_id,
            Status=body.Status
        )
        return {"message": "Category updated successfully", "status": 200}
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error updating category")


# ❌ Delete Category by ID
@router.delete("/api/v1/category/{category_id}")
async def delete_category(category_id: str):
    try:
        category = CategoryTable.objects(id=ObjectId(category_id)).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        category.delete()
        return {"message": "Category deleted successfully", "status": 200}
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Error deleting category")
