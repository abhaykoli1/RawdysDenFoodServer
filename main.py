# from order.routes import orderRoutes
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from mongoengine import connect

from imageUpload import imageuploadroutes
from items.routes import itemsRoute



# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in .env file")

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file")


connect('RowdysDen', host="mongodb+srv://abhay:ipkoliki@ecommerce.7g0xg.mongodb.net")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  
    allow_methods=["GET", "POST", "PATCH", "DELETE", "PUT"],   
    allow_headers=["Content-Type", "Authorization", "Cache-Control", "Expires", "Pragma"],  # Allowed headers
)

# prefix="/products"
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# app.include_router(uploadImagesRoutes.router, tags=["image Upload"])
# app.include_router(imageuploadroutes.router, tags=["image Upload"])
app.include_router(itemsRoute.router, tags=["Items, Categories & Orders"])



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
