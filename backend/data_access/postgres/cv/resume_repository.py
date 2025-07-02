from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
import json

class ResumeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_header_id(self, header_id: int):
        query = text("""
        SELECT 
        h.user_id AS user_id, 
        h.full_name AS full_name, h.job_title, h.email, h.phone_number AS phone_number, h.address,
        h.years_of_experience, h.linkedin_profile, h.github_profile,
        COALESCE(o.description, '') AS objective, 


        COALESCE(json_agg(DISTINCT e.*) FILTER (WHERE e.id IS NOT NULL), '[]') AS education,
        COALESCE(json_agg(DISTINCT exp.*) FILTER (WHERE exp.id IS NOT NULL), '[]') AS experience,
        COALESCE(json_agg(DISTINCT p.*) FILTER (WHERE p.id IS NOT NULL), '[]') AS projects,
        COALESCE(json_agg(DISTINCT v.*) FILTER (WHERE v.id IS NOT NULL), '[]') AS volunteering_experience,

    COALESCE(json_agg(DISTINCT jsonb_build_object(
        'skill', s.skills
    )) FILTER (WHERE s.skills IS NOT NULL AND s.skills <> ''), '[]') AS technical_skills,

    COALESCE(json_agg(DISTINCT jsonb_build_object(
        'language', s.languages,
        'level', s.level
    )) FILTER (WHERE s.languages IS NOT NULL AND s.languages <> ''), '[]') AS languages,

        COALESCE(json_agg(DISTINCT jsonb_build_object(
            'certification_title', c.certification_title, 
            'link', c.link
        )) FILTER (WHERE c.id IS NOT NULL), '[]') AS certifications,

        COALESCE(json_agg(DISTINCT jsonb_build_object(
            'award', a.award, 
            'organization', a.organization, 
            'start_date', a.start_date, 
            'end_date', a.end_date
        )) FILTER (WHERE a.id IS NOT NULL), '[]') AS awards

    FROM header h
    LEFT JOIN objective o ON h.id = o.header_id
    LEFT JOIN education e ON h.id = e.header_id
    LEFT JOIN experience exp ON h.id = exp.header_id
    LEFT JOIN projects p ON h.id = p.header_id
    LEFT JOIN skills_languages s ON h.id = s.header_id  
    LEFT JOIN volunteering_experience v ON h.id = v.header_id
    LEFT JOIN certifications c ON h.id = c.header_id
    LEFT JOIN awards a ON h.id = a.header_id
    WHERE h.id = :header_id
    GROUP BY h.id, o.description;
        """)


        print(f"Executing query for header_id: {header_id}")  

        result = await self.db.execute(query, {"header_id": header_id})
        user = result.mappings().first()  

        if not user:
            print("No user found!")  
            return None  

        user_dict = dict(user)

        for key in ["education", "experience", "projects", "volunteering_experience", "certifications", "awards"]:
            if isinstance(user_dict.get(key), str):
                user_dict[key] = json.loads(user_dict[key])

        if isinstance(user_dict.get("technical_skills"), str):
            user_dict["technical_skills"] = json.loads(user_dict["technical_skills"])

        if isinstance(user_dict.get("languages"), str):
            user_dict["languages"] = json.loads(user_dict["languages"])

        return user_dict
