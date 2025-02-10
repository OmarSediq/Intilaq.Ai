from bson import ObjectId
from app.dependencies import get_collection

# اسم المجموعة
templates_collection = get_collection("templates")

# ---------------------
# إضافة قالب جديد
# ---------------------
async def add_template(template_data: dict) -> dict:
    """
    Add a new template to the templates collection.

    Args:
        template_data (dict): The template data to add.

    Returns:
        dict: The inserted template with its ID.
    """
    result = await templates_collection.insert_one(template_data)
    template_data["_id"] = str(result.inserted_id)
    return template_data


# ---------------------
# استرجاع قالب باستخدام المعرف
# ---------------------
async def get_template_by_id(template_id: str) -> dict:
    """
    Retrieve a template by its ID.

    Args:
        template_id (str): The ID of the template.

    Returns:
        dict: The template data, or None if not found.
    """
    try:
        template = await templates_collection.find_one({"_id": ObjectId(template_id)})
        if template:
            template["_id"] = str(template["_id"])
        return template
    except Exception as e:
        return {"error": str(e)}


# ---------------------
# استرجاع جميع القوالب
# ---------------------
async def list_templates() -> list:
    """
    Retrieve all templates.

    Returns:
        list: A list of templates.
    """
    templates = []
    async for template in templates_collection.find():
        template["_id"] = str(template["_id"])
        templates.append(template)
    return templates


# ---------------------
# تحديث قالب
# ---------------------
async def update_template(template_id: str, update_data: dict) -> dict:
    """
    Update a template by its ID.

    Args:
        template_id (str): The ID of the template.
        update_data (dict): The fields to update.

    Returns:
        dict: The updated template, or None if not found.
    """
    try:
        result = await templates_collection.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": update_data}
        )
        if result.modified_count == 0:
            return {"message": "Template not found or no changes made."}
        return await get_template_by_id(template_id)
    except Exception as e:
        return {"error": str(e)}


# ---------------------
# حذف قالب
# ---------------------
async def delete_template(template_id: str) -> dict:
    """
    Delete a template by its ID.

    Args:
        template_id (str): The ID of the template.

    Returns:
        dict: The deletion result.
    """
    try:
        result = await templates_collection.delete_one({"_id": ObjectId(template_id)})
        if result.deleted_count == 0:
            return {"message": "Template not found."}
        return {"message": "Template deleted successfully."}
    except Exception as e:
        return {"error": str(e)}