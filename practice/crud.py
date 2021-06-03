from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user

from practice import models, schemas
from passlib.context import CryptContext
from fastapi.encoders import jsonable_encoder

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def check_password(password, hash_password) -> str:
    return pwd_context.verify(password, hash_password)


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 0):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user_by_username(db: Session, username):
    value = db.query(models.User).filter(models.User.username == username).first()
    print(value)
    return value


def get_user_by_status(db: Session, status: str):
    return db.query(models.User).filter(models.User.status == status).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        username=user.username,
        status=user.status,
        firstname=user.firstname,
        lastname=user.lastname,
        email=user.email,
        password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(
        projectName=project.projectName,
        assigned=project.assigned,
        status=project.status,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def pass_user(db: Session, username):
    user_value = db.query(models.User).filter(models.User.username == username).first()
    user_dict = jsonable_encoder(user_value)
    current_user = schemas.User(**user_dict)
    return current_user
