from bson import ObjectId
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson.errors import InvalidId
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

try:
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    mongo_db = mongo_client[MONGO_DB_NAME]
    templates_collection = mongo_db["cv_templates"]
    print(" MongoDB connection successful.")
except Exception as e:
    print(f"Error connecting to MongoDB: {str(e)}")
    templates_collection = None

async def add_template(template_data: dict) -> dict:
    
    if not templates_collection:
        return {"error": "MongoDB connection failed"}
    
    result = await templates_collection.insert_one(template_data)
    template_data["_id"] = str(result.inserted_id)
    return template_data

async def get_template_by_id(template_id: str) -> dict:
    """
    Retrieve a template by its ID with validation.
    """
    try:
        object_id = ObjectId(template_id)
        template = await templates_collection.find_one({"_id": object_id})
        if template:
            template["_id"] = str(template["_id"])
        return template if template else {"error": "Template not found."}
    except InvalidId:
        return {"error": "Invalid template ID"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

async def list_templates(limit: int = 10, skip: int = 0) -> list:
    """
    Retrieve a paginated list of templates.
    """
    if not templates_collection:
        return {"error": "MongoDB connection failed"}
    
    try:
        templates = await templates_collection.find().skip(skip).limit(limit).to_list(length=limit)
        for template in templates:
            template["_id"] = str(template["_id"])
        return templates
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

async def update_template(template_id: str, update_data: dict) -> dict:
    """
    Update a template by its ID with validation.
    """
    if not templates_collection:
        return {"error": "MongoDB connection failed"}

    try:
        object_id = ObjectId(template_id)
        result = await templates_collection.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )
        if result.modified_count == 0:
            return {"error": "No changes made or template not found."}
        return await get_template_by_id(template_id)
    except InvalidId:
        return {"error": "Invalid template ID"}
    except Exception as e:
        return {"error": str(e)}

async def delete_template(template_id: str) -> dict:
    """
    Delete a template by its ID with validation.
    """
    if not templates_collection:
        return {"error": "MongoDB connection failed"}

    try:
        object_id = ObjectId(template_id)
        result = await templates_collection.delete_one({"_id": object_id})
        if result.deleted_count == 0:
            return {"error": "Template not found."}
        return {"message": "Template deleted successfully."}
    except InvalidId:
        return {"error": "Invalid template ID"}
    except Exception as e:
        return {"error": str(e)}
