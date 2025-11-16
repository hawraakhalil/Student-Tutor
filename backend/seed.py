from sqlalchemy.orm import Session
from .database import engine, SessionLocal
from . import models


def seed():
    db: Session = SessionLocal()
    try:
        # create subjects
        subjects = ["Math", "Physics", "Chemistry", "Programming", "English", "Biology", "Economics"]
        subject_objs = []
        for name in subjects:
            s = models.Subject(name=name)
            db.add(s)
            subject_objs.append(s)
        db.commit()

        # students
        students = [
            models.Student(name="Alice", email="alice@example.com", city="Beirut", address="Hamra", preferred_subjects="Math,Physics", max_hourly_rate=30.0, ),
            models.Student(name="Bob", email="bob@example.com", city="Beirut", address="Antelias", preferred_subjects="Programming,Math", max_hourly_rate=40.0),
        ]
        for s in students:
            db.add(s)
        db.commit()

        # tutors: add a mix
        tutor_data = [
            ("Tamer","tamer@example.com","Beirut","Corniche",33.8886,35.4955,25.0,"online","Experienced Math tutor", ["Math"]),
            ("Lina","lina@example.com","Beirut","Hamra",33.897,35.487,35.0,"in_person","Physics MSc", ["Physics","Math"]),
            ("Omar","omar@example.com","Antelias","Antelias Center",33.888,35.530,20.0,"hybrid","Programming tutor", ["Programming"]),
            ("Sara","sara@example.com","Beirut","Ashrafieh",33.8938,35.5035,28.0,"in_person","Chemistry specialist", ["Chemistry"]),
            ("Nadine","nadine@example.com","Jounieh","Jounieh Mall",34.318,35.649,30.0,"online","English literature", ["English"]),
            ("Hassan","hassan@example.com","Beirut","Dora",33.920,35.500,22.0,"online","Biology tutor", ["Biology"]),
            ("Rami","rami@example.com","Beirut","Verdun",33.892,35.493,45.0,"in_person","Economics and Math", ["Economics","Math"]),
            ("Maya","maya@example.com","Tripoli","Tripoli Center",34.433,35.849,18.0,"online","Entry-level Programming", ["Programming"]),
            ("Youssef","youssef@example.com","Beirut","Hamra",33.897,35.487,50.0,"in_person","Senior Math tutor", ["Math"]),
            ("Rita","rita@example.com","Jounieh","Old Souk",34.318,35.649,26.0,"hybrid","Physics tutor", ["Physics"]),
            ("Khaled","khaled@example.com","Beirut","Zalka",33.900,35.540,15.0,"online","Programming and Math", ["Programming","Math"]),
            ("Mira","mira@example.com","Beirut","Badaro",33.885,35.502,32.0,"in_person","Chemistry and Biology", ["Chemistry","Biology"]),
        ]

        for name,email,city,address,lat,lng,rate,mode,bio,subs in tutor_data:
            t = models.Tutor(name=name, email=email, city=city, address=address, latitude=lat, longitude=lng, hourly_rate=rate, teaching_mode=mode, bio=bio, overall_rating=4.0, number_of_reviews=5)
            db.add(t)
            db.commit()
            # attach subjects
            for sname in subs:
                subj = db.query(models.Subject).filter(models.Subject.name==sname).first()
                if subj:
                    t.subjects.append(subj)
            db.add(t)
            db.commit()

        # add some reviews
        tutors = db.query(models.Tutor).all()
        students = db.query(models.Student).all()
        import random
        for t in tutors:
            for i in range(2):
                st = random.choice(students)
                r = models.Review(student_id=st.id, tutor_id=t.id, rating=random.randint(3,5), comment="Good session")
                db.add(r)
            db.commit()

        print("Seeding done.")
    finally:
        db.close()


if __name__ == '__main__':
    seed()
