from typing import Optional
from beanie import Document
from pydantic import BaseModel, Field
from datetime import datetime
from pymongo import ASCENDING, DESCENDING

from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    SUPERADMIN = "superadmin"

class Student(Document):
    username: Optional[str] = "student" # Default for legacy data or optional
    login_email: Optional[str] = None
    password_hash: Optional[str] = None
    name: str
    grade: Optional[int] = None # e.g. 2025
    desc: str       # Bio/Description
    role: str = "PhD Student"     # e.g. "PhD Student" (Display role)
    user_role: UserRole = UserRole.STUDENT # Auth role
    icon: str = "i-carbon-user" # Default icon
    link: Optional[str] = None
    
    # Expanded Profile Fields
    avatar: Optional[str] = None
    major: Optional[str] = None
    interests: list[str] = []
    bio: Optional[str] = None
    public_email: Optional[str] = None
    must_change_password: bool = False
    password_reset_at: Optional[datetime] = None
    
    class Settings:
        name = "students" # MongoDB collection name

class Teacher(Document):
    username: str
    login_email: Optional[str] = None
    password_hash: Optional[str] = None
    name: str
    desc: str
    role: str = "Professor" # Display role
    user_role: UserRole = UserRole.TEACHER
    icon: str = "i-carbon-education"
    # Profile Fields (Mirrors Student for consistency)
    avatar: Optional[str] = None
    major: Optional[str] = None
    interests: list[str] = []
    bio: Optional[str] = None
    
    # Professional Fields
    title: Optional[str] = None
    office: Optional[str] = None
    public_email: Optional[str] = None
    research_areas: list[str] = []
    must_change_password: bool = False
    password_reset_at: Optional[datetime] = None

    class Settings:
        name = "teachers"

class SuperAdmin(Document):
    username: str
    login_email: Optional[str] = None
    password_hash: Optional[str] = None
    name: str
    desc: str = "Super Admin"
    role: str = "Superadmin"
    user_role: UserRole = UserRole.SUPERADMIN
    icon: str = "i-carbon-user-admin"
    must_change_password: bool = False
    password_reset_at: Optional[datetime] = None

    class Settings:
        name = "superadmins"

class Post(Document):
    title: str
    summary: str = "" # Default for legacy data
    content: str
    cover_image: Optional[str] = None
    author: str = "Lab Team" # Default for legacy data
    date: datetime = datetime.now()
    type: str = "blog"

    class Settings:
        name = "posts"

class LifeItem(Document):
    title: str
    content: str
    date: datetime = datetime.now()

    class Settings:
        name = "life_items"

class ShowcaseItem(Document):
    title: str
    desc: str
    link: Optional[str] = None
    cover: Optional[str] = None # Image URL
    date: datetime = datetime.now()

    class Settings:
        name = "showcase_items"

class Activity(Document):
    title: str
    type: str # "研讨会", "工作坊", "开放日", "讲座"
    date: str # "YYYY-MM-DD"
    location: str
    participants: int = 0
    summary: str
    content: str = ""
    cover_image: Optional[str] = None

    created_by_id: Optional[str] = None
    created_by_username: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "activities"

class Project(Document):
    title: str
    status: str  # "进行中", "已结题", "筹备中"
    category: str # e.g. "数据挖掘", "物联网"
    progress: int = 0  # 0-100
    description: str
    leader: str
    members: list[str] = []
    cover_image: Optional[str] = None
    repo_url: Optional[str] = None
    created_by_id: Optional[str] = None
    created_by_username: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "projects"

class Software(Document):
    name: str
    version: str            # e.g. "v2.3.1"
    category: str           # e.g. "工具软件", "开发套件", "开发库"
    size: str               # e.g. "25.6 MB" (Manual input is fine)
    description: str
    download_url: str       # External link (Drive/GitHub)
    download_count: int = 0
    cover_image: Optional[str] = None
    created_by_id: Optional[str] = None
    created_by_username: Optional[str] = None
    upload_date: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "software"

class InviteCode(Document):
    code: str
    role: UserRole
    max_uses: int = 1
    used_count: int = 0
    expires_at: Optional[datetime] = None
    note: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

    class Settings:
        name = "invite_codes"


class RegistrationGradePolicy(Document):
    policy_key: str = "student_registration_grade_policy"
    allowed_grades: list[int] = Field(default_factory=list)
    updated_by: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "registration_grade_policy"

class ForumPost(Document):
    title: str
    content: str
    author_id: str
    author_name: Optional[str] = None
    tags: list[str] = []
    liked_user_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    is_pinned: bool = False
    is_featured: bool = False

    class Settings:
        name = "forum_posts"
        indexes = [
            [("author_name", ASCENDING), ("created_at", DESCENDING)],
            [("created_at", DESCENDING)],
        ]

class ForumComment(Document):
    post_id: str
    author_id: str
    author_name: Optional[str] = None
    content: str
    liked_user_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "forum_comments"
        indexes = [
            [("author_name", ASCENDING), ("created_at", DESCENDING)],
            [("post_id", ASCENDING), ("created_at", ASCENDING)],
            [("created_at", DESCENDING)],
        ]
