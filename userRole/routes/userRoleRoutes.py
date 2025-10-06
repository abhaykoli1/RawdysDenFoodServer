import json
import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse


router = APIRouter()

from userRole.model.userRoleModel import UserRoleModel , UserRoleTable

@router.post("/api/v1/add-role")
async def create_role(data: UserRoleModel):
    try:
        role = UserRoleTable(**data.dict())
        role.save()

        return JSONResponse(
        content={
            "message": "Role created successfully",
            "data": role.to_json()
        }, 
        status_code=201)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Get all roles
@router.get("/api/v1/all-roles")
async def get_all_roles():
    try:
        allRoles = []
        roles = UserRoleTable.objects.all()

        for value in roles:
            allRoles.append(json.loads(value.to_json()))

        return {
            "message": "Here are all Roles",
            "data": allRoles,
            "status": 200
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Get role by ID
@router.get("/api/v1/role/{id}")
async def get_role_by_id(id: str):
    try:
        role = UserRoleTable.objects.get(id=id)
        return {
            "message": "User Role data",
            "data": json.loads(role.to_json()),
            "status": 200
        }
    
    except UserRoleTable.DoesNotExist:
        raise HTTPException(status_code=404, detail="User Role not found")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Update role by ID
@router.put("/api/v1/update-role/{id}")
async def update_role(id: str, data: UserRoleModel):
    try:
        role = UserRoleTable.objects(id=id).first()
        if not role:
            raise HTTPException(status_code=404, detail="User Role not found")

        role.update(**data.dict())
        updated = UserRoleTable.objects.get(id=id)

        return {
            "message": "User Role updated successfully",
            "data": json.loads(updated.to_json())
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Delete role by ID
@router.delete("/api/v1/delete-role/{id}")
async def delete_role(id: str):
    try:
        role = UserRoleTable.objects(id=id).first()

        if not role:
            raise HTTPException(status_code=404, detail="User Role not found")

        role.delete()

        return {
            "message": "User Role deleted successfully",
            "status": 200
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
