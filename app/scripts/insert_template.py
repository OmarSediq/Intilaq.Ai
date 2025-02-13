import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# تحميل متغيرات البيئة من .env
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:84000@localhost:27017")  # تعيين localhost كقيمة افتراضية
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "intilaq_db")

print(f"🔍 Connecting to MongoDB at: {MONGO_URI}")
print(f"📂 Using Database: {MONGO_DB_NAME}")

try:
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    mongo_db = mongo_client[MONGO_DB_NAME]
    templates_collection = mongo_db["cv_templates"]
    print("✅ Successfully connected to MongoDB.")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")
    exit(1)

async def insert_default_template():
    try:
        print("🔄 Checking if Default CV Template exists...")
        existing_template = await templates_collection.find_one({"name": "Default CV Template"})

        if not existing_template:
            template_data = {
        "name": "Default CV Template",
        "html_content": """ 
        <html>
        <head>
            <title>CV - {{ name }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1, h2 { color: #2C3E50; }
                p { line-height: 1.6; }
                .header { text-align: center; }
                .section { margin-top: 20px; }
                .page-break { page-break-before: always; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ name }}</h1>
                <p><strong>{{ job_title }}</strong></p>
                <p>{{ location }} | {{ email }} | {{ phone }}</p>
                <p><a href="{{ linkedin }}">LinkedIn</a> | <a href="{{ portfolio }}">Portfolio</a></p>
            </div>
            <div class="section">
                <h2>Career Objective</h2>
                <p>{{ career_objective }}</p>
            </div>
            <div class="section">
                <h2>Education</h2>
                {% for edu in education %}
                <p><strong>{{ edu.degree_and_major }}</strong> - {{ edu.school }} ({{ edu.start_date }} - {{ edu.end_date }})</p>
                {% if edu.grade %}
                <p>Grade: {{ edu.grade }}</p>
                {% endif %}
                {% endfor %}
            </div>
            <div class="section">
                <h2>Experience</h2>
                {% for job in experience %}
                <p><strong>{{ job.role }}</strong> at {{ job.company_name }} ({{ job.start_date }} - {{ job.end_date }})</p>
                <p>{{ job.description }}</p>
                {% endfor %}
            </div>
            <div class="page-break"></div>
            <div class="section">
                <h2>Skills</h2>
                <ul>
                    {% for skill in skills %}
                    <li>{{ skill }}</li>
                    {% endfor %}
                </ul>
            </div>
        </body>
        </html>
        """
    }


            result = await templates_collection.insert_one(template_data)  
            print(f"✅ Template stored with ID: {result.inserted_id}")
        else:
            print("⚠️ Template already exists in MongoDB.")

    except Exception as e:
        print(f"❌ Error inserting template: {e}")
