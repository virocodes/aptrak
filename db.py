from sqlalchemy import create_engine, Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
from datetime import datetime
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

class Application(Base):
    __tablename__ = 'applications'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    job_title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    status = Column(String, nullable=False)
    applied_on = Column(Date, nullable=False)
    link = Column(Text)
    description = Column(Text)
    notes = Column(Text)

Base.metadata.create_all(engine)

def add_user(username, password, email):
    hashed_pwd = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, password=hashed_pwd, email=email)
    session.add(new_user)
    session.commit()

def get_user_by_name(username):
    return session.query(User).filter(User.username == username).first()

def add_application(user_id, job_title, company, status, link="", description=""):
    new_application = Application(
        user_id=user_id,
        job_title=job_title,
        company=company,
        status=status,
        applied_on=datetime.now(),
        link=link,
        description=description
    )
    session.add(new_application)
    session.commit()

def get_applications_by_user(user_id):
    return session.query(Application).filter(Application.user_id == user_id).all()

def get_application_by_id(application_id):
    return session.query(Application).filter(Application.id == application_id).first()

def delete_application_by_id(application_id, user_id):
    application = session.query(Application).filter(Application.id == application_id, Application.user_id == user_id).first()
    if application:
        session.delete(application)
        session.commit()

def update_application_by_id(application_id, user_id, field, value):
    application = session.query(Application).filter(Application.id == application_id, Application.user_id == user_id).first()
    if application:
        setattr(application, field, value)
        session.commit()