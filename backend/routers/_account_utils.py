import re
from typing import Optional

from models import Student, SuperAdmin, Teacher, UserRole

USER_MODELS = (Student, Teacher, SuperAdmin)


def normalize_username(value: Optional[str]) -> str:
    return (value or "").strip()


def normalize_login_email(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip().lower()
    return normalized or None


def is_valid_username(value: str) -> bool:
    # Allow student ID style numbers and common username symbols.
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]{3,32}", value))


def model_for_role(role: str):
    if role == UserRole.STUDENT:
        return Student
    if role == UserRole.TEACHER:
        return Teacher
    if role == UserRole.SUPERADMIN:
        return SuperAdmin
    return None


async def is_username_taken(username: str, exclude_user_id: Optional[str] = None) -> bool:
    escaped = re.escape(username)
    query = {"username": {"$regex": f"^{escaped}$", "$options": "i"}}
    for model in USER_MODELS:
        user = await model.find_one(query)
        if user and str(user.id) != str(exclude_user_id):
            return True
    return False


async def is_login_email_taken(login_email: str, exclude_user_id: Optional[str] = None) -> bool:
    normalized = normalize_login_email(login_email)
    if not normalized:
        return False
    escaped = re.escape(normalized)
    query = {"login_email": {"$regex": f"^{escaped}$", "$options": "i"}}
    for model in USER_MODELS:
        user = await model.find_one(query)
        if user and str(user.id) != str(exclude_user_id):
            return True
    return False


async def find_user_by_login_identifier(role: str, identifier: str):
    model = model_for_role(role)
    if model is None:
        return None

    normalized_identifier = normalize_username(identifier)
    if not normalized_identifier:
        return None

    user = await model.find_one({"username": normalized_identifier})
    if user:
        return user

    escaped = re.escape(normalized_identifier)
    user = await model.find_one({"username": {"$regex": f"^{escaped}$", "$options": "i"}})
    if user:
        return user

    login_email = normalize_login_email(normalized_identifier)
    if login_email:
        escaped = re.escape(login_email)
        return await model.find_one({"login_email": {"$regex": f"^{escaped}$", "$options": "i"}})

    return None


async def find_user_by_name_identifier(role: str, identifier: str):
    model = model_for_role(role)
    if model is None:
        return None, False

    normalized = normalize_username(identifier)
    if not normalized:
        return None, False

    escaped = re.escape(normalized)
    users = await model.find({"name": {"$regex": f"^{escaped}$", "$options": "i"}}).limit(2).to_list()
    if not users:
        return None, False
    if len(users) > 1:
        return None, True
    return users[0], False
