from pydantic import BaseModel
from typing import Optional, List
from beanie import PydanticObjectId
from datetime import datetime

class StudentCreate(BaseModel):
    name: str
    desc: str
    role: str
    icon: Optional[str] = "i-carbon-user"
    link: Optional[str] = None

class StudentOut(StudentCreate):
    id: PydanticObjectId
    username: Optional[str] = None
    user_role: Optional[str] = None
    grade: Optional[int] = None
    avatar: Optional[str] = None
    major: Optional[str] = None
    interests: List[str] = []
    bio: Optional[str] = None
    public_email: Optional[str] = None

class UserUpdate(BaseModel):
    avatar: Optional[str] = None
    major: Optional[str] = None
    interests: List[str] = []
    bio: Optional[str] = None
    desc: Optional[str] = None # Allow updating abstract too
    # Teacher fields
    title: Optional[str] = None
    office: Optional[str] = None
    public_email: Optional[str] = None
    research_areas: List[str] = []

class TeacherOut(BaseModel):
    id: PydanticObjectId
    username: str
    name: str
    role: str
    user_role: str
    icon: str
    desc: str
    avatar: Optional[str] = None
    major: Optional[str] = None
    interests: List[str] = []
    bio: Optional[str] = None
    title: Optional[str] = None
    office: Optional[str] = None
    public_email: Optional[str] = None
    research_areas: List[str] = []

class SuperAdminOut(BaseModel):
    id: PydanticObjectId
    username: str
    name: str
    role: str
    user_role: str
    icon: str
    desc: str

class PublicUserOut(BaseModel):
    username: str
    name: str
    user_role: str
    role: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    major: Optional[str] = None
    interests: List[str] = []
    research_areas: List[str] = []
    public_email: Optional[str] = None

class ContributionCountsOut(BaseModel):
    forum_posts: int = 0
    forum_comments: int = 0
    activities: int = 0
    projects: int = 0
    software: int = 0

class ForumPostSummaryOut(BaseModel):
    id: PydanticObjectId
    title: str
    created_at: datetime

class ForumCommentSummaryOut(BaseModel):
    id: PydanticObjectId
    post_id: str
    post_title: str
    created_at: datetime
    content_preview: str

class ActivitySummaryOut(BaseModel):
    id: PydanticObjectId
    title: str
    date: str
    type: str

class ProjectSummaryOut(BaseModel):
    id: PydanticObjectId
    title: str
    status: str
    created_at: datetime

class SoftwareSummaryOut(BaseModel):
    id: PydanticObjectId
    name: str
    version: str
    upload_date: datetime

class UserContributionsOut(BaseModel):
    counts: ContributionCountsOut
    recent_forum_posts: List[ForumPostSummaryOut] = []
    recent_forum_comments: List[ForumCommentSummaryOut] = []
    recent_activities: List[ActivitySummaryOut] = []
    recent_projects: List[ProjectSummaryOut] = []
    recent_software: List[SoftwareSummaryOut] = []

class PostCreate(BaseModel):
    title: str
    summary: Optional[str] = ""
    content: str
    cover_image: Optional[str] = None
    type: str = "blog"

class PostUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None
    type: Optional[str] = None

class PostOut(PostCreate):
    id: PydanticObjectId
    date: datetime
    author: str

class PostAdjacentItemOut(BaseModel):
    id: PydanticObjectId
    title: str
    date: datetime

class PostAdjacentOut(BaseModel):
    previous: Optional[PostAdjacentItemOut] = None
    next: Optional[PostAdjacentItemOut] = None

class LifeItemCreate(BaseModel):
    title: str
    content: str

class ActivityCreate(BaseModel):
    title: str
    type: str
    date: str
    location: str
    participants: int = 0
    summary: str
    content: Optional[str] = ""
    cover_image: Optional[str] = None


class ActivityOut(ActivityCreate):
    id: PydanticObjectId
    created_by_id: Optional[str] = None
    created_by_username: Optional[str] = None
    created_at: datetime

class LifeItemOut(LifeItemCreate):
    id: PydanticObjectId
    date: datetime

class ShowcaseItemCreate(BaseModel):
    title: str
    desc: str
    link: Optional[str] = None
    cover: Optional[str] = None

class ShowcaseItemOut(ShowcaseItemCreate):
    id: PydanticObjectId
    date: datetime

class ProjectCreate(BaseModel):
    title: str
    status: str
    category: str
    progress: int = 0
    description: str
    leader: str
    members: List[str] = []
    cover_image: Optional[str] = None
    repo_url: Optional[str] = None

class ProjectOut(ProjectCreate):
    id: PydanticObjectId
    created_by_id: Optional[str] = None
    created_by_username: Optional[str] = None
    created_at: datetime

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    progress: Optional[int] = None
    description: Optional[str] = None
    leader: Optional[str] = None
    members: Optional[List[str]] = None
    cover_image: Optional[str] = None
    repo_url: Optional[str] = None

class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    participants: Optional[int] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None

class SoftwareCreate(BaseModel):
    name: str
    version: str
    category: str
    size: str
    description: str
    download_url: str
    cover_image: Optional[str] = None

class SoftwareOut(SoftwareCreate):
    id: PydanticObjectId
    download_count: int
    created_by_id: Optional[str] = None
    created_by_username: Optional[str] = None
    upload_date: datetime

class SoftwareUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    category: Optional[str] = None
    size: Optional[str] = None
    description: Optional[str] = None
    download_url: Optional[str] = None
    cover_image: Optional[str] = None

class InviteCreate(BaseModel):
    role: str
    max_uses: int = 1
    expires_at: Optional[datetime] = None
    note: Optional[str] = None

class InviteOut(InviteCreate):
    id: PydanticObjectId
    code: str
    used_count: int
    created_by: Optional[str] = None
    created_at: datetime
    is_active: bool

class GradeOptionsOut(BaseModel):
    grades: List[int] = []
    source: str

class GradePolicyUpdate(BaseModel):
    allowed_grades: List[int] = []

class GradePolicyOut(BaseModel):
    allowed_grades: List[int] = []
    effective_grades: List[int] = []
    source: str
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None

class ForumPostCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []

class ForumPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    is_pinned: Optional[bool] = None
    is_featured: Optional[bool] = None

class ForumPostOut(ForumPostCreate):
    id: PydanticObjectId
    author_id: str
    author_name: Optional[str] = None
    author_display_name: Optional[str] = None
    created_at: datetime
    is_pinned: bool
    is_featured: bool

class ForumCommentCreate(BaseModel):
    content: str

class ForumCommentUpdate(BaseModel):
    content: Optional[str] = None

class ForumCommentOut(ForumCommentCreate):
    id: PydanticObjectId
    post_id: str
    author_id: str
    author_name: Optional[str] = None
    author_display_name: Optional[str] = None
    created_at: datetime

class ForumUserCommentOut(BaseModel):
    id: PydanticObjectId
    post_id: str
    post_title: str
    author_id: str
    author_name: Optional[str] = None
    author_display_name: Optional[str] = None
    content: str
    created_at: datetime
