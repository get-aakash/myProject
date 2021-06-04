from typing import List
from sqlalchemy import engine
from mytask.database import SessionLocal, engine
from mytask import models, schemas, crud
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from jose import JWTError, jwt

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

models.Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/create/project")
def create_project(
    project: schemas.Project,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Super user creates the project and its attributes. Super user also assigns the project to the users.
    so the user must be logged in as super user to create a project

    """
    user1 = current_user(token, db)
    if user1.status == "superuser":
        return crud.create_project(db, project)
    raise HTTPException(status_code=400, detail="only super user can create")


@app.get("/projects/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    this module displays the list of all the projects and its attributes created by the super user

    """
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return projects


@app.get("/users", response_model=List[schemas.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    This module displays the list of all the user stored in the database

    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/tasks")
def get_all_task(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    This module displays the list of all tasks irrespective of the logged in user.
    So that any one can view the list of tasks

    """
    value = current_user(token, db)
    if value.status == "superuser":
        return crud.get_tasks(db)
    raise HTTPException(status_code=400, detail="the user needs to be super user")


@app.get("/task")
def get_task_username(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    This module provides the list of all the tasks of logged in user

    """
    result = current_user(token, db)
    if result:
        value = crud.get_task_by_username(db, result.username)
        return value
    raise HTTPException(status_code=400, detail="the logged in user has no task")


@app.put("/update/status/task")
async def update_task_status(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    This module updates the task status of the user

    """

    value = current_user(token, db)

    result = crud.update_task(db, value.username, task)
    return result


@app.post("/create/task")
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    A user must be logged in to create their own task.

    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("user")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    return crud.create_task(db, task, token_data.username)


@app.post("/create/user")
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    Inorder to create a user. The logged in user must have a status of superuser.

    """
    user1 = current_user(token, db)
    if user1.status == "superuser":
        return crud.create_user(db, user)
    raise HTTPException(status_code=400, detail="only super user can create")


@app.post("/token")
async def login_for_access_token(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user_value = crud.get_user_by_username(db, form.username)
    username = user_value.username
    password = user_value.password
    verify_password = crud.check_password(form.password, password)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username is incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="password is incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user": username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("user")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    current_user = crud.pass_user(db, username=token_data.username)
    print(current_user)
    if current_user is None:
        raise credentials_exception
    return current_user


@app.get("/current/user", response_model=schemas.User)
def get_current_user(current_user: schemas.User = Depends(current_user)):
    return current_user
