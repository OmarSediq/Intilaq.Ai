
from typing import  Dict

def build_verification_context(
    *,
    verification_code=str ,


)-> Dict[str, str]:
    return {
        "verification_code":verification_code
    }