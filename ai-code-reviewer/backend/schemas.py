from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    repo_url: str = Field(..., description="Public GitHub repository URL")


class ReviewSummary(BaseModel):
    id: str
    repo_url: str
    owner: Optional[str] = None
    repo: Optional[str] = None
    overall_score: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewDetail(ReviewSummary):
    result: dict[str, Any]
