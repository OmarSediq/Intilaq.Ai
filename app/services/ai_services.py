from google.generativeai import GenerativeModel
import google.generativeai as genai
from fastapi import HTTPException
from typing import Optional
from datetime import date
import os
from dotenv import load_dotenv


# تحميل متغيرات البيئة
load_dotenv()

# تعيين مفتاح API بأمان
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# إعداد النموذج التوليدي
model = GenerativeModel(model_name="gemini-1.5-flash")

async def generate_objective_from_ai(job_title: str, years_of_experience: int) -> list:
    """
    Generate a career objective using AI API based on job title and years of experience.
    """
    try:
        system_message = (
            "You are an AI assistant for CV generation. Your task is to generate professional career objectives. "
            "Provide clear, concise, and tailored descriptions based on the job title and years of experience. "
            "Suggest 4 different descriptions, each with a maximum of 4 lines."
        )
        human_message = f"Generate a career objective for the job title '{job_title}' with {years_of_experience} years of experience."
        
        # إنشاء الـ prompt الصحيح
        prompt = f"{system_message}\n\nUser: {human_message}"
        response = model.generate_content(prompt)

        return response.text.split("\n")  # تقسيم الرد إلى أسطر
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate objective: {str(e)}")

async def fetch_project_descriptions_from_ai(project_name: str) -> list:
    """
    Generate project descriptions using AI API.
    """
    try:
        system_message = (
            "You are an AI assistant specialized in CV generation. Your task is to generate concise and impactful "
            "descriptions for projects. Include the project's goals, technologies used, and measurable outcomes. "
            "Suggest 4 different descriptions, each with a maximum of 2 lines."
        )
        human_message = f"Generate a project description for the project titled '{project_name}'."
        
        # إنشاء الـ prompt الصحيح
        prompt = f"{system_message}\n\nUser: {human_message}"
        response = model.generate_content(prompt)

        return response.text.split("\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch project descriptions: {str(e)}")

async def generate_experience_from_ai(role: str, start_date: date, end_date: Optional[date]) -> list:
    """
    Generate experience descriptions using AI API.
    """
    try:
        system_message = (
            "You are an AI assistant specialized in generating CV work experience sections. Your task is to provide "
            "detailed and structured work experience entries tailored to the role and dates provided. Include "
            "the start date and end date in the format 'Role, Company Name (Month YYYY – Month YYYY)' and focus on "
            "accomplishments. Suggest 5 different descriptions, each with a maximum of 5 lines."
        )
        human_message = (
            f"Generate a work experience section for the role '{role}', starting from {start_date} and ending on "
            f"{end_date if end_date else 'present'}. Include accomplishments and format dates as 'Month YYYY'."
        )

        # إنشاء الـ prompt الصحيح
        prompt = f"{system_message}\n\nUser: {human_message}"
        response = model.generate_content(prompt)

        return response.text.split("\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate experience: {str(e)}")

async def generate_skills_from_ai(job_title: str, years_of_experience: int) -> dict:
    """
    Generate AI-based skills suggestions based on job title and years of experience using Google Gemini AI.
    """
    try:
        system_message = (
            "You are an AI assistant for CV generation. Your task is to generate essential skills for a job title "
            "based on the user's years of experience. Provide a structured list with the following categories: "
            "- Technical Skills\n"
            "- Programming Skills\n"
            "- Language Skills\n"
            "Each skill should be listed without descriptions, only the title of the skill itself."
            "Ensure the skills are highly relevant and sorted by importance."
        )
        human_message = f"Generate a list of technical, programming, and language skills for a {job_title} with {years_of_experience} years of experience."
        
        # إنشاء الـ prompt الصحيح
        prompt = f"{system_message}\n\nUser: {human_message}"
        response = model.generate_content(prompt)

        # تحويل الاستجابة إلى JSON (لأن Google Gemini يعيد النصوص كـ `response.text`)
        skills_text = response.text.strip().split("\n")

        # تنظيم الاستجابة في هيكل بيانات مناسب
        skills = {
            "Technical Skills": [],
            "Programming Skills": [],
            "Language Skills": []
        }

        category = None
        for skill in skills_text:
            skill = skill.strip()
            if "Technical Skills" in skill:
                category = "Technical Skills"
            elif "Programming Skills" in skill:
                category = "Programming Skills"
            elif "Language Skills" in skill:
                category = "Language Skills"
            elif category and skill:
                skills[category].append(skill)

        return skills

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate skills: {str(e)}")

async def generate_volunteering_description_from_ai(activity_role: str) -> list:
    """
    Generate AI-based descriptions for volunteering experience based on role.
    """
    try:
        system_message = (
            "You are a CV writing assistant. Your task is to generate concise and impactful volunteering activity descriptions "
            "tailored to the given role. Ensure the descriptions are professional and avoid any mention of organization names, locations, roles, or dates. "
            "Suggest 4 different descriptions, each with a maximum of 2 lines, temperature=0."
        )
        human_message = (
            f"Write volunteering activity descriptions for a CV targeting a {activity_role}. "
            "Focus on significant accomplishments and responsibilities, quantifying them wherever possible, without including placeholders like "
            "organization names, city, state, roles, or dates."
        )

        # إعداد الـ prompt
        prompt = f"System: {system_message}\nHuman: {human_message}"
        response = model.generate_content(prompt)

        return response.text.strip().split("\n")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate volunteering descriptions: {str(e)}")