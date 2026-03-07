from datetime import datetime
from typing import Iterable, Tuple

from models import RegistrationGradePolicy

POLICY_KEY = "student_registration_grade_policy"


def normalize_grades(values: Iterable[int]) -> list[int]:
    parsed = set()
    for value in values or []:
        try:
            year = int(value)
        except Exception:
            continue
        if 1900 <= year <= 3000:
            parsed.add(year)
    return sorted(parsed, reverse=True)


def default_grades() -> list[int]:
    current_year = datetime.now().year
    return list(range(current_year + 1, current_year - 21, -1))


async def get_policy_document() -> RegistrationGradePolicy | None:
    return await RegistrationGradePolicy.find_one({"policy_key": POLICY_KEY})


async def get_effective_grades() -> Tuple[list[int], str]:
    policy = await get_policy_document()
    if policy:
        grades = normalize_grades(policy.allowed_grades)
        if grades:
            return grades, "policy"
    return default_grades(), "default"

