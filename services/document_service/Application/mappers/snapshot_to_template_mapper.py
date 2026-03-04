class SnapshotToTemplateMapper:

    @staticmethod
    def map(snapshot: dict) -> dict:

        contact = snapshot.get("contact", {})

        return {
            "full_name": snapshot.get("full_name"),
            "job_title": snapshot.get("job_title"),

            "objective": snapshot.get("summary"),

            "email": contact.get("email"),
            "phone_number": contact.get("phone"),
            "address": contact.get("address"),
            "linkedin_profile": contact.get("linkedin"),
            "github_profile": contact.get("github"),

            "experience": snapshot.get("experience", []),
            "education": snapshot.get("education", []),
            "projects": snapshot.get("projects", []),
            "volunteering_experience": snapshot.get("volunteering_experience", []),

            "technical_skills": snapshot.get("skills", []),
            "languages": snapshot.get("languages", []),

            "certifications": snapshot.get("certifications", []),
            "awards": snapshot.get("awards", []),
        }