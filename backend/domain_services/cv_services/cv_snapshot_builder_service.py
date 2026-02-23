
class CVSnapshotBuilder:

    def build(self, user_data: dict) -> dict:
        return {
            "full_name": user_data.get("full_name"),
            "job_title": user_data.get("job_title"),
            "summary": user_data.get("objective", ""),
            "contact": {
                "email": user_data.get("email"),
                "phone": user_data.get("phone_number"),
                "address": user_data.get("address"),
                "linkedin": user_data.get("linkedin_profile"),
                "github": user_data.get("github_profile"),
            },
            "experience": user_data.get("experience", []),
            "education": user_data.get("education", []),
            "projects": user_data.get("projects", []),
            "volunteering_experience": user_data.get("volunteering_experience", []),
            "skills": user_data.get("technical_skills", []),
            "languages": user_data.get("languages", []),
            "certifications": user_data.get("certifications", []),
            "awards": user_data.get("awards", []),
            "meta": {
                "years_of_experience": user_data.get("years_of_experience"),
            },
        }