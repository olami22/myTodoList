from database import Base
from sqlalchemy import Boolean, Column, String,ForeignKey,Integer
#from app.user import models


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True,index=True)
    task = Column(String)
    completed=Column(Boolean, default = False)
   # user_id =  Column(Integer, ForeignKey("users.id"))
    