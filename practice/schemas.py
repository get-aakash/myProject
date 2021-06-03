from pydantic import BaseModel
from typing import Optional


class ProjectBase(BaseModel):
    projectName: str
    assigned: str
    status: str


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name: str
    username: str
    status: str
    firstname: str
    lastname: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
