from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import github
import llm
import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Code Reviewer", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/review", response_model=schemas.ReviewDetail)
async def create_review(req: schemas.ReviewRequest, db: Session = Depends(get_db)):
    try:
        repo_data = await github.fetch_repo_code(req.repo_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except github.GitHubError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"GitHub fetch failed: {e}")

    if not repo_data["files"]:
        raise HTTPException(status_code=400, detail="No reviewable code files found in repository")

    try:
        result = llm.review_code(repo_data["files"])
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM review failed: {e}")

    review = models.Review(
        repo_url=req.repo_url,
        owner=repo_data["owner"],
        repo=repo_data["repo"],
        overall_score=result.get("overall_score"),
        result=result,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@app.get("/api/reviews", response_model=list[schemas.ReviewSummary])
def list_reviews(db: Session = Depends(get_db)):
    return (
        db.query(models.Review)
        .order_by(models.Review.created_at.desc())
        .limit(50)
        .all()
    )


@app.get("/api/reviews/{review_id}", response_model=schemas.ReviewDetail)
def get_review(review_id: str, db: Session = Depends(get_db)):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review
