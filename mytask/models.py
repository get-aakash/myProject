from mytask.database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(20), index=True)
    lastname = Column(String(20), index=True)
    email = Column(String(20), index=True)
    name = Column(String(20), index=True)
    username = Column(String(20), index=True)
    status = Column(String(20), index=True)
    password = Column(String(20), index=True)


class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, index=True)
    projectName = Column(String(20), index=True)
    assigned = Column(String(20), index=True)
    status = Column(String(20), index=True)


class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True, index=True)
    taskId = Column(String(20), ForeignKey("users.username"), index=True)
    taskName = Column(String(20), index=True)
    taskStatus = Column(String(20), index=True)
