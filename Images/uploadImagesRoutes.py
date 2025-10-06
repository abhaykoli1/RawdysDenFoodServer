
# import io
# import json
# import os
# from typing import List
# import uuid
# from fastapi import APIRouter, File, Form, HTTPException, UploadFile
# from fastapi.responses import JSONResponse

# from boto3 import client
# from mongoengine.errors import DoesNotExist, ValidationError
# from bson import ObjectId
# from datetime import datetime



# PACES_ACCESS_KEY = 'DO00AJFUXFALT4K6L69E'
# SPACES_SECRET_KEY = 'kn2jUm8ox9W6fPQXvJ6E5kBtVZtzF5V5MvY6sJ8Cr8U'
# SPACES_ENDPOINT_URL = 'https://blackwhite.blr1.digitaloceanspaces.com'
# SPACES_BUCKET_NAME = 'UAASITE'

# # S3 client for DigitalOcean Spaces
# s3 = client('s3',
#             region_name='blr1',
#             endpoint_url=SPACES_ENDPOINT_URL,
#             aws_access_key_id=PACES_ACCESS_KEY,
#             aws_secret_access_key=SPACES_SECRET_KEY)

# router = APIRouter()

# # Function to upload file to DigitalOcean Spaces
# def upload_file_to_space(file_content: bytes, filename: str) -> str:
#     try:
#         # Generate a random filename with the original extension
#         random_filename = str(uuid.uuid4())
#         file_extension = os.path.splitext(filename)[1]
#         random_filename_with_extension = f"{random_filename}{file_extension}"

#         # Create a BytesIO stream
#         file_content_stream = io.BytesIO(file_content)

#         # Upload the file without setting ContentLength
#         s3.upload_fileobj(
#             file_content_stream,
#             SPACES_BUCKET_NAME,
#             random_filename_with_extension,
#             ExtraArgs={
#                 'ACL': 'public-read'
#             }
#         )

#         # Return the file's public URL
#         return f"{SPACES_ENDPOINT_URL}/UAASITE/{random_filename_with_extension}"

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
    

# @router.post("/api/v1/upload-image")
# async def upload_image(file: UploadFile = File(...)):
#     try:
#         # Read file content
#         file_content = await file.read()

#         # Upload to DigitalOcean Spaces
#         file_url = upload_file_to_space(file_content, file.filename)

#         return {"message": "File uploaded successfully", "file_url": file_url}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    


import os
import uuid
from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter()

# Ensure uploads directory exists
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Function to save file locally in /uploads
def save_file_locally(file_content: bytes, filename: str) -> str:
    try:
        # Generate random filename with extension
        random_filename = str(uuid.uuid4())
        file_extension = os.path.splitext(filename)[1]
        random_filename_with_extension = f"{random_filename}{file_extension}"

        file_path = os.path.join(UPLOAD_DIR, random_filename_with_extension)

        # Write file to disk
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Return relative path (or you can return absolute if needed)
        return f"/uploads/{random_filename_with_extension}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")


@router.post("/api/v1/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Read file content
        file_content = await file.read()

        # Save locally
        file_url = save_file_locally(file_content, file.filename)

        return {"message": "File uploaded successfully", "file_url": file_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
