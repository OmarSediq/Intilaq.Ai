from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
import json

class ResumeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_header_id(self, header_id: int):
        query = text("""
        SELECT 
          h.user_id,
          h.full_name,
          h.job_title,
          h.email,
          h.phone_number,
          h.address,
          h.years_of_experience,
          h.linkedin_profile,
          h.github_profile,
          COALESCE(o.description, '') AS objective,

          COALESCE((
            SELECT json_agg(e ORDER BY e.id)
            FROM cv.education e
            WHERE e.header_id = h.id
          ), '[]') AS education,

          COALESCE((
            SELECT json_agg(exp ORDER BY exp.id)
            FROM cv.experience exp
            WHERE exp.header_id = h.id
          ), '[]') AS experience,

          COALESCE((
            SELECT json_agg(p ORDER BY p.id)
            FROM cv.projects p
            WHERE p.header_id = h.id
          ), '[]') AS projects,

          COALESCE((
            SELECT json_agg(v ORDER BY v.id)
            FROM cv.volunteering_experience v
            WHERE v.header_id = h.id
          ), '[]') AS volunteering_experience,

          COALESCE((
            SELECT json_agg(jsonb_build_object('skill', s.skills)) 
            FROM cv.skills_languages s
            WHERE s.header_id = h.id AND s.skills IS NOT NULL AND s.skills <> ''
          ), '[]') AS technical_skills,

          COALESCE((
            SELECT json_agg(jsonb_build_object('language', s.languages, 'level', s.level))
            FROM cv.skills_languages s
            WHERE s.header_id = h.id AND s.languages IS NOT NULL AND s.languages <> ''
          ), '[]') AS languages,

          COALESCE((
            SELECT json_agg(jsonb_build_object('certification_title', c.certification_title, 'link', c.link) ORDER BY c.id)
            FROM cv.certifications c
            WHERE c.header_id = h.id
          ), '[]') AS certifications,

          COALESCE((
            SELECT json_agg(jsonb_build_object('award', a.award, 'organization', a.organization, 'start_date', a.start_date, 'end_date', a.end_date) ORDER BY a.id)
            FROM cv.awards a
            WHERE a.header_id = h.id
          ), '[]') AS awards

        FROM cv.header h
        LEFT JOIN cv.objective o ON h.id = o.header_id
        WHERE h.id = :header_id
        ;
        """)

        print(f"Executing optimized correlated-subqueries query for header_id: {header_id}")
        result = await self.db.execute(query, {"header_id": header_id})
        user = result.mappings().first()

        if not user:
            print("No user found!")
            return None

        user_dict = dict(user)

        return user_dict
