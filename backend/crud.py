from sqlalchemy.orm import Session
import models
from typing import List, Optional
from math import radians, cos, sin, asin, sqrt


def haversine(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return None
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km


def get_subject_by_name(db: Session, name: str):
    return db.query(models.Subject).filter(models.Subject.name.ilike(name)).first()


def search_tutors(db: Session, subject_name: Optional[str]=None, city: Optional[str]=None,
                  max_hourly_rate: Optional[float]=None, min_rating: Optional[float]=None,
                  teaching_mode: Optional[str]=None, student=None, sort_by: Optional[str]=None):
    q = db.query(models.Tutor)
    if subject_name:
        q = q.join(models.Tutor.subjects).filter(models.Subject.name.ilike(f"%{subject_name}%"))
    if city:
        q = q.filter(models.Tutor.city.ilike(f"%{city}%"))
    if max_hourly_rate is not None:
        q = q.filter(models.Tutor.hourly_rate <= max_hourly_rate)
    if min_rating is not None:
        q = q.filter(models.Tutor.overall_rating >= min_rating)
    if teaching_mode:
        q = q.filter(models.Tutor.teaching_mode == teaching_mode)

    tutors = q.all()

    # if student provided with lat/long, compute distance and sort if requested
    results = []
    for t in tutors:
        dist = None
        results.append((t, dist))

    if sort_by == "distance_asc":
        results.sort(key=lambda x: (x[1] is None, x[1] if x[1] is not None else 1e9))
    elif sort_by == "price_asc":
        results.sort(key=lambda x: x[0].hourly_rate)
    else:
        # default: rating desc, then price asc
        results.sort(key=lambda x: (- (x[0].overall_rating or 0), x[0].hourly_rate))

    return results


def get_tutor(db: Session, tutor_id: int):
    return db.query(models.Tutor).filter(models.Tutor.id == tutor_id).first()


def get_similar_tutors(db: Session, tutor_id: int, limit: int = 6):
    base = get_tutor(db, tutor_id)
    if not base:
        return []
    subject_ids = [s.id for s in base.subjects]
    q = db.query(models.Tutor).join(models.TutorSubject, models.Tutor.id==models.TutorSubject.tutor_id)
    q = q.filter(models.Tutor.id != tutor_id)
    q = q.filter(models.TutorSubject.subject_id.in_(subject_ids))
    q = q.filter(models.Tutor.overall_rating >= 3.5)
    candidates = q.all()

    # score by number of overlapping subjects, rating desc, price closeness
    def score(t):
        overlap = len(set([s.id for s in t.subjects]) & set(subject_ids))
        price_diff = abs((t.hourly_rate or 0) - (base.hourly_rate or 0))
        rating = t.overall_rating or 0
        return (-overlap, -rating, price_diff)

    candidates.sort(key=score)
    return candidates[:limit]


def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def recommend_for_student(db: Session, student_id: int, limit: int = 8):
    student = get_student(db, student_id)
    if not student:
        return []
    prefs = []
    if student.preferred_subjects:
        prefs = [s.strip() for s in student.preferred_subjects.split(",") if s.strip()]

    q = db.query(models.Tutor)
    if prefs:
        # join subjects
        q = q.join(models.Tutor.subjects).filter(models.Subject.name.in_(prefs))
    if student.city:
        q = q.filter(models.Tutor.city.ilike(f"%{student.city}%"))
    if student.max_hourly_rate is not None:
        q = q.filter(models.Tutor.hourly_rate <= student.max_hourly_rate)
    q = q.filter(models.Tutor.overall_rating >= 0.0)

    tutors = q.all()

    # score by subject match count, rating desc, distance if available
    def score(t):
        sub_names = [s.name for s in t.subjects]
        overlap = len(set(sub_names) & set(prefs)) if prefs else 0
        rating = t.overall_rating or 0
        dist = None
        stu_lat = getattr(student, "latitude", None)
        stu_lon = getattr(student, "longitude", None)

        if stu_lat is not None and stu_lon is not None and t.latitude is not None and t.longitude is not None:
            dist = haversine(stu_lat, stu_lon, t.latitude, t.longitude)

        return (-overlap, -rating, dist if dist is not None else 1e6)

    tutors.sort(key=score)
    return tutors[:limit]


def create_or_get_subject(db: Session, name: str):
    name = name.strip()
    if not name:
        return None
    s = db.query(models.Subject).filter(models.Subject.name.ilike(name)).first()
    if s:
        return s
    s = models.Subject(name=name)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def create_tutor(db: Session, *, name: str, email: str, hourly_rate: float = 0.0, phone: str = None,
                 city: str = None, address: str = None, latitude: float = None, longitude: float = None,
                 teaching_mode: str = None, bio: str = None, subjects: list = None):
    t = models.Tutor(name=name, email=email, phone=phone, city=city, address=address,
                     latitude=latitude, longitude=longitude, hourly_rate=hourly_rate,
                     teaching_mode=teaching_mode, bio=bio)
    db.add(t)
    db.flush()
    if subjects:
        for sname in subjects:
            s = create_or_get_subject(db, sname)
            if s:
                t.subjects.append(s)
    db.commit()
    db.refresh(t)
    return t


def update_tutor(db: Session, tutor_id: int, updates: dict):
    t = db.query(models.Tutor).filter(models.Tutor.id == tutor_id).first()
    if not t:
        return None
    # simple scalar fields
    fields = ['name','email','phone','city','address','latitude','longitude','hourly_rate','teaching_mode','bio']
    for f in fields:
        if f in updates:
            setattr(t, f, updates.get(f))
    # handle subjects explicitly
    if 'subjects' in updates:
        t.subjects.clear()
        subs = updates.get('subjects') or []
        for sname in subs:
            s = create_or_get_subject(db, sname)
            if s:
                t.subjects.append(s)
    db.commit()
    db.refresh(t)
    return t


def delete_tutor(db: Session, tutor_id: int):
    t = db.query(models.Tutor).filter(models.Tutor.id == tutor_id).first()
    if not t:
        return False
    # delete related reviews
    db.query(models.Review).filter(models.Review.tutor_id == tutor_id).delete()
    # delete tutor_subjects entries
    db.query(models.TutorSubject).filter(models.TutorSubject.tutor_id == tutor_id).delete()
    db.delete(t)
    db.commit()
    return True


def create_student(db: Session, *, name: str, email: str, city: str = None, address: str = None,
                   preferred_subjects: str = None, max_hourly_rate: float = None):
    s = models.Student(name=name, email=email, city=city, address=address,
                       preferred_subjects=preferred_subjects, max_hourly_rate=max_hourly_rate)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def update_student(db: Session, student_id: int, updates: dict):
    s = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not s:
        return None
    fields = ['name','email','city','address','preferred_subjects','max_hourly_rate']
    for f in fields:
        if f in updates:
            setattr(s, f, updates.get(f))
    db.commit()
    db.refresh(s)
    return s


def delete_student(db: Session, student_id: int):
    s = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not s:
        return False
    # delete related reviews and lesson requests
    db.query(models.Review).filter(models.Review.student_id == student_id).delete()
    db.query(models.LessonRequest).filter(models.LessonRequest.student_id == student_id).delete()
    db.delete(s)
    db.commit()
    return True
