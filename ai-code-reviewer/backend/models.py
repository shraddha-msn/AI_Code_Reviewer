import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Integer

from database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=lambda: uuid.uuid4().hex[:12])
    repo_url = Column(String, nullable=False)
    owner = Column(String)
    repo = Column(String)
    overall_score = Column(Integer)
    result = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
