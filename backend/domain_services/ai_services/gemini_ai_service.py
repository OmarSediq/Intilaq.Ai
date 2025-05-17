from datetime import date
from typing import Optional
from fastapi import HTTPException
import re
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from google.generativeai import GenerativeModel
import google.generativeai as genai

class GeminiAIService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = GenerativeModel(model_name="gemini-1.5-flash")

    async def generate_objective(self, job_title: str, years_of_experience: int) -> list:
        system_message = (
                "You are a CV generation assistant. Your task is to provide a clear and concise "
                "professional summary or career objective tailored to the role and experience level provided. "
                "Suggest 4 different descriptions, each with a maximum of 4 lines, temperature=0."
            )
        user = f"Generate a career objective for the job title '{job_title}' with {years_of_experience} years of experience."
        prompt = f"{system_message}\n\nUser: {user}"

        try:
            response = self.model.generate_content(prompt)
            return response.text.split("\n")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate objective: {str(e)}")

    async def fetch_project_descriptions(self, project_name: str) -> list:
        system_message = (
            "You are an AI assistant specialized in CV generation. Your task is to generate concise and impactful "
            "descriptions for projects. Include the project's goals, technologies used, and measurable outcomes. "
            "Suggest 4 different descriptions, each with a maximum of 2 lines."
        )
        user = f"Generate a project description for the project titled '{project_name}'."
        prompt = f"{system_message}\n\nUser: {user}"

        try:
            response = self.model.generate_content(prompt)
            return response.text.split("\n")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch project descriptions: {str(e)}")

    async def generate_experience(self, role: str, start_date: date, end_date: Optional[date]) -> list:
        system_message = (
            "You are an AI assistant specialized in generating CV work experience sections. Your task is to provide "
            "detailed and structured work experience entries tailored to the role and dates provided. Include "
            "the start date and end date in the format 'Role, Company Name (Month YYYY – Month YYYY)' and focus on "
            "accomplishments. Suggest 5 different descriptions, each with a maximum of 5 lines."
        )
        user = f"Generate a work experience section for the role '{role}', starting from {start_date} to {end_date or 'present'}."
        prompt = f"{system_message}\n\nUser: {user}"

        try:
            response = self.model.generate_content(prompt)
            return response.text.split("\n")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate experience: {str(e)}")

    async def generate_skills(self, job_title: str, years_of_experience: int) -> dict:
        system_message = (
            "You are an AI assistant for CV generation. Your task is to generate essential skills for a job title "
            "based on the user's years of experience. Provide a structured list with the following categories: "
            "- Technical Skills\n"
            "- Programming Skills\n"
            "- Language Skills\n"
            "Each skill should be listed without descriptions, only the title of the skill itself."
            "Ensure the skills are highly relevant and sorted by importance."
        )
        user = f"Generate a list of technical, programming, and language skills for a {job_title} with {years_of_experience} years of experience."
        prompt = f"{system_message}\n\nUser: {user}"

        try:
            response = self.model.generate_content(prompt)
            lines = response.text.strip().split("\n")
            skills = {"Technical Skills": [], "Programming Skills": [], "Language Skills": []}
            category = None
            for line in lines:
                if "Technical Skills" in line:
                    category = "Technical Skills"
                elif "Programming Skills" in line:
                    category = "Programming Skills"
                elif "Language Skills" in line:
                    category = "Language Skills"
                elif category and line.strip():
                    skills[category].append(line.strip())
            return skills
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate skills: {str(e)}")

    async def generate_volunteering_description(self, activity_role: str) -> list:
        system_message = (
            "You are a CV writing assistant. Your task is to generate concise and impactful volunteering activity descriptions "
            "tailored to the given role. Ensure the descriptions are professional and avoid any mention of organization names, locations, roles, or dates. "
            "Suggest 4 different descriptions, each with a maximum of 2 lines, temperature=0."
        )
        user = (
            f"Write volunteering activity descriptions for a CV targeting a {activity_role}. "
            "Focus on significant accomplishments and responsibilities, quantifying them wherever possible, without including placeholders like "
            "organization names, city, state, roles, or dates."
        )
        prompt = f"System: {system_message}\nHuman: {user}"

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip().split("\n")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate volunteering descriptions: {str(e)}")

    async def generate_interview_questions(self, role: str, level: Optional[str] = None, job_description: Optional[str] = None) -> str:
        system_message = (
        "You are a professional interview assistant specializing in crafting comprehensive and role-specific interview questions. "
        "Your responsibility is to generate 10 targeted virtual interview questions for the given role. "
        "If a job description is provided, seamlessly integrate its details to refine the questions. "
        "Focus on evaluating the candidate's technical skills and expertise relevant to the role. "
        "Present the questions in a clear and concise numbered list."
    )
        if job_description:
            user = f"Generate interview questions for the role of '{role}' based on the following job description:\n{job_description}"
        else:
            user = f"Generate interview questions for the role of '{role}'."
        prompt = f"System: {system_message}\nHuman: {user}"

        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            return f"An error occurred: {e}"

    async def generate_questions_for_hr(self, job_name: str, job_level: str, job_requirements: str) -> str:
        system_message = (
            f"Generate exactly 10 unique technical interview questions for a {job_level} {job_name} role "
            f"based on these job requirements: {job_requirements}.\n"
            "Return only the questions, each on a new line, without numbering, labels, explanations, or additional formatting."
        )
        user = f"Generate 10 interview questions for a {job_level} {job_name} role."
        prompt = f"System: {system_message}\nHuman: {user}"

        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

    async def generate_best_answer(self, question: str) -> str:
        system_message = (
        "Generate the best possible answer for the given interview question "
        "that helps candidates understand their mistakes and learn."
        )

        prompt = f"System: {system_message}\nHuman: Question: \"{question}\""

        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating model answer: {e}"

    async def generate_feedback(self, user_answer: str, question: str, ideal_answer: str):
            system_message = (
                "You are an expert interview evaluator. Based on the interview question and the ideal answer, "
                "analyze the user's answer and provide feedback in the following format:\n"
                "**Strengths:** [What the user did well in relation to the question and ideal answer.]\n"
                "**Weaknesses:** [Where the user fell short or missed key points.]\n"
                "**Constructive Feedback:** [How the user can improve their answer to better match expectations.]\n"
                "Make sure your analysis is specific, detailed, and focuses on alignment with the ideal answer."
            )

            prompt = f"""
        {system_message}
        Interview Question:
        {question}

        Ideal Answer:
        {ideal_answer}

        User's Answer:
        {user_answer}

        Provide your feedback:
        """.strip()

            try:
                    response = await self.model.generate_content_async(prompt)
                    text = response.text.strip()
                    return {
                        "strengths": self._extract_section(text, "Strengths"),
                        "weaknesses": self._extract_section(text, "Weaknesses"),
                        "constructive_feedback": self._extract_section(text, "Constructive Feedback"),
                    }
            except Exception as e:
                    return {
                        "strengths": "Error",
                        "weaknesses": "Error",
                        "constructive_feedback": f"An error occurred: {e}"
                    }


    def _extract_section(self, text, section_name):
                        match = re.search(rf"\*\*{section_name}:\*\*\s*(.*?)(?=\n\*\*|\Z)", text, re.DOTALL)
                        return match.group(1).strip() if match else "N/A"

    def analyze_similarity_score(self, answer: str, model_answer: str) -> float:
                        vectorizer = TfidfVectorizer().fit_transform([answer, model_answer])
                        similarity_matrix = cosine_similarity(vectorizer[0:1], vectorizer[1:2])
                        return round(similarity_matrix[0][0] * 10, 2)

