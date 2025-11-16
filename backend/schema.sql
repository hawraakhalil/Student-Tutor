-- Simple schema for Tutor Finder
CREATE TABLE students (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  city TEXT,
  address TEXT,
  preferred_subjects TEXT,
  max_hourly_rate REAL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tutors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT,
  city TEXT,
  address TEXT,
  hourly_rate REAL NOT NULL DEFAULT 0.0,
  teaching_mode TEXT,
  bio TEXT,
  overall_rating REAL DEFAULT 0.0,
  number_of_reviews INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE subjects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE tutor_subjects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tutor_id INTEGER REFERENCES tutors(id),
  subject_id INTEGER REFERENCES subjects(id)
);

CREATE TABLE reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER REFERENCES students(id),
  tutor_id INTEGER REFERENCES tutors(id),
  rating INTEGER NOT NULL,
  comment TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE lesson_requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER REFERENCES students(id),
  tutor_id INTEGER REFERENCES tutors(id),
  subject_id INTEGER REFERENCES subjects(id),
  status TEXT,
  requested_date DATETIME,
  notes TEXT
);
