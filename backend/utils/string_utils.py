def extract_name_from_email(email: str) -> str:
    return email.split('@')[0].capitalize()
