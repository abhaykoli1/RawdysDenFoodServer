from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import cloudinary
import cloudinary.uploader
from io import BytesIO
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
)

router = APIRouter()

MAX_SIZE = 10 * 1024 * 1024  # 10MB in bytes

@router.post("/api/v1/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    # Validate file size using the file's 'file' attribute (avoids reading twice)
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, and JPG are allowed.")
    
    if file.size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds the 10MB limit.")

    # Read image file content once into memory
    file_content = await file.read()
    file_like = BytesIO(file_content)  # Create a file-like object for Cloudinary

    # Upload to Cloudinary
    try:
        upload_response = cloudinary.uploader.upload(file_like, resource_type="auto")

        # Return the image URL
        image_url = upload_response["secure_url"]

        return JSONResponse(
            content={
                "success": True,
                "message": "Image uploaded successfully",
                "result": {
                    "url": image_url,
                },
            },
            status_code=200,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image to Cloudinary: {str(e)}")
