import jwt
from datetime import datetime, timedelta, timezone
from app.config import settings
from fastapi import HTTPException

def create_access_token(payload: dict, expiration_minutes: int = 60) -> str:
    """
    Generate a JWT access token with the provided payload.

    Args:
        payload (dict): The data to include in the token (e.g., user ID).
        expiration_minutes (int): The token expiration time in minutes (default is 60 minutes).

    Returns:
        str: The encoded JWT token.
    """
    try:
        expiration = datetime.now(timezone.utc) + timedelta(minutes=expiration_minutes)
        payload.update({"exp": expiration})
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token
    except jwt.PyJWTError as e:
        print(f"Error generating token: {e}")
        raise

def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict: The decoded token payload.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
