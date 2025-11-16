import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Determine a stable absolute path for the default sqlite file (project root/app.db)
here = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
default_db_path = os.path.join(here, 'app.db')

# Allow override via DATABASE_URL environment variable for production (e.g. Azure SQL)
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{default_db_path}')

# If using sqlite, provide the check_same_thread connect arg
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {}

# echo=True can be enabled for debugging SQL; keep False by default
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

