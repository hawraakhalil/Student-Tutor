from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, validator
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, crud, ai
from .database import engine, get_db, Base
import os

# Load environment variables from backend/.env if present (supports secrets locally)
try:
    from dotenv import load_dotenv
    here = os.path.dirname(__file__)
    dotenv_path = os.path.join(here, ".env")
    load_dotenv(dotenv_path)
except Exception:
    # dotenv is optional; if not available, environment variables must come from the system
    pass

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tutor Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # Do not expose credentials with a wildcard origin to avoid browser blocking.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    student_id: int
    message: str
    use_ai: bool = True  # you can toggle this from the frontend if you want


@app.get("/api/subjects")
def list_subjects(db: Session = Depends(get_db)):
    subs = db.query(models.Subject).all()
    return [{"id": s.id, "name": s.name} for s in subs]


@app.get("/api/students")
def list_students(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    return [{"id": s.id, "name": s.name, "email": s.email, "city": s.city, "preferred_subjects": s.preferred_subjects, "max_hourly_rate": s.max_hourly_rate} for s in students]


@app.get("/api/cities")
def list_cities(db: Session = Depends(get_db)):
    # distinct cities from tutors
    q = db.query(models.Tutor.city).distinct().all()
    cities = [c[0] for c in q if c[0]]
    return cities


@app.get("/api/tutors/search")
def tutor_search(subject: str = Query(None), city: str = Query(None), max_hourly_rate: float = Query(None),
                 min_rating: float = Query(None), teaching_mode: str = Query(None), student_id: int = Query(None),
                 sort_by: str = Query(None), db: Session = Depends(get_db)):
    student = None
    if student_id:
        student = crud.get_student(db, student_id)
    results = crud.search_tutors(db, subject_name=subject, city=city, max_hourly_rate=max_hourly_rate,
                                 min_rating=min_rating, teaching_mode=teaching_mode, student=student, sort_by=sort_by)
    out = []
    for t, dist in results:
        out.append({
            "id": t.id,
            "name": t.name,
            "city": t.city,
            "hourly_rate": t.hourly_rate,
            "teaching_mode": t.teaching_mode.value if t.teaching_mode else None,
            "overall_rating": t.overall_rating,
            "number_of_reviews": t.number_of_reviews,
            "subjects": [s.name for s in t.subjects],
            "distance_km": round(dist, 2) if dist is not None else None,
        })
    return out


@app.get("/api/tutors/{tutor_id}")
def tutor_details(tutor_id: int, db: Session = Depends(get_db)):
    t = crud.get_tutor(db, tutor_id)
    if not t:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return {
        "id": t.id,
        "email": t.email,
        "phone": t.phone,
        "name": t.name,
        "city": t.city,
        "address": t.address,
        "hourly_rate": t.hourly_rate,
        "teaching_mode": t.teaching_mode.value if t.teaching_mode else None,
        "bio": t.bio,
        "overall_rating": t.overall_rating,
        "number_of_reviews": t.number_of_reviews,
        "subjects": [s.name for s in t.subjects],
        "reviews": [{"rating": r.rating, "comment": r.comment, "created_at": r.created_at.isoformat()} for r in t.reviews]
    }


@app.get("/api/tutors/{tutor_id}/similar")
def similar_tutors(tutor_id: int, db: Session = Depends(get_db)):
    sims = crud.get_similar_tutors(db, tutor_id)
    return [{"id": t.id, "name": t.name, "hourly_rate": t.hourly_rate, "overall_rating": t.overall_rating, "number_of_reviews": t.number_of_reviews, "subjects": [s.name for s in t.subjects]} for t in sims]

@app.post("/api/chat")
def chat_with_recommender(payload: ChatMessage, db: Session = Depends(get_db)):
    student = crud.get_student(db, payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # 1) Get tutors via your existing recommender
    tutors = crud.recommend_for_student(db, student.id)

    # 2) Build explanations for CARDS (not for chat reply)
    explanations = ai.explain_recommendations(student, tutors)
    tutor_payloads = []
    for t, ex in zip(tutors, explanations):
        tutor_payloads.append({
            "id": t.id,
            "name": t.name,
            "city": t.city,
            "hourly_rate": t.hourly_rate,
            "overall_rating": t.overall_rating,
            "number_of_reviews": t.number_of_reviews,
            "subjects": [s.name for s in t.subjects],
            "explanation": ex,  # for UI cards, not chat bubbles
        })

    # 3) ALWAYS generate a chat reply (no model, no None)
    reply = ai.generate_chat_reply(student, payload.message, tutors)

    return {
        "reply": reply,      # <- this is what ChatBox should show as the main bot message
        "tutors": tutor_payloads,
    }

def generate_chat_reply(student, message: str, tutors: list) -> str:
    """
    Simple, deterministic chat reply.
    Does NOT reuse the per-tutor deterministic explanation.
    """
    stu_name = getattr(student, "name", "") or "there"
    first_name = stu_name.split()[0] if stu_name else "there"

    if not tutors:
        return (
            f"Hi {first_name}! I couldn’t find any tutors that match this student’s current profile. "
            "Try changing their preferred subjects, city, or maximum hourly rate and ask me again."
        )

    # some light personalization
    subjects = getattr(student, "preferred_subjects", None) or "your subjects"
    city = getattr(student, "city", None) or "your area"
    budget = getattr(student, "max_hourly_rate", None)
    budget_str = f"${budget}/hr" if budget is not None else "your budget"

    top = tutors[:3]
    names = ", ".join(t.name for t in top)

    return (
        f"Hi {first_name}! Based on what you said and this student’s profile "
        f"({subjects}, {city}, budget around {budget_str}), I’ve found {len(tutors)} tutors. "
        f"A few strong options are: {names}. "
        "You can click their cards for more details or tell me if you’d prefer someone cheaper, closer, or in a different subject."
    )

@app.get("/api/students/{student_id}/recommendations")
def student_recommendations(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    recs = crud.recommend_for_student(db, student_id)

    out = []
    for t in recs:
        explanation = ai._deterministic_explanation(student, t)
        out.append({
            "id": t.id,
            "name": t.name,
            "hourly_rate": t.hourly_rate,
            "overall_rating": t.overall_rating,
            "number_of_reviews": t.number_of_reviews,
            "subjects": [s.name for s in t.subjects],
            "explanation": explanation,
        })

    return out



# ----- CRUD schemas and endpoints (Tutors + Students) -----


class TutorCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    city: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    hourly_rate: float = 0.0
    teaching_mode: str | None = None
    bio: str | None = None
    subjects: list[str] | None = None

    @validator("latitude", "longitude", pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v

class TutorUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    city: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    hourly_rate: float | None = None
    teaching_mode: str | None = None
    bio: str | None = None
    subjects: list[str] | None = None

    @validator("latitude", "longitude", pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    city: str | None = None
    address: str | None = None
    preferred_subjects: str | None = None
    max_hourly_rate: float | None = None


class StudentUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    city: str | None = None
    address: str | None = None
    preferred_subjects: str | None = None
    max_hourly_rate: float | None = None


@app.post("/api/tutors", status_code=201)
def add_tutor(t: TutorCreate, db: Session = Depends(get_db)):
    tutor = crud.create_tutor(db, **t.dict())
    return {"id": tutor.id, "name": tutor.name, "email": tutor.email, "hourly_rate": tutor.hourly_rate, "subjects": [s.name for s in tutor.subjects]}


@app.put("/api/tutors/{tutor_id}")
def put_tutor(tutor_id: int, updates: TutorUpdate, db: Session = Depends(get_db)):
    u = crud.update_tutor(db, tutor_id, updates.dict(exclude_unset=True))
    if not u:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return {"id": u.id, "name": u.name, "email": u.email, "hourly_rate": u.hourly_rate, "subjects": [s.name for s in u.subjects]}


@app.delete("/api/tutors/{tutor_id}")
def del_tutor(tutor_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_tutor(db, tutor_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return {"deleted": True}


@app.post("/api/students", status_code=201)
def add_student(s: StudentCreate, db: Session = Depends(get_db)):
    stu = crud.create_student(db, **s.dict())
    return {"id": stu.id, "name": stu.name, "email": stu.email}


@app.put("/api/students/{student_id}")
def put_student(student_id: int, updates: StudentUpdate, db: Session = Depends(get_db)):
    u = crud.update_student(db, student_id, updates.dict(exclude_unset=True))
    if not u:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": u.id, "name": u.name, "email": u.email}


@app.delete("/api/students/{student_id}")
def del_student(student_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_student(db, student_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"deleted": True}