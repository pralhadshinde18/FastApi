# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
#
#
# class User(BaseModel):
#     username: str
#     email: str
#
#
# app = FastAPI()
#
# users_db = {}
#
#
# @app.post("/users/", response_model=User)
# def create_user(user: User):
#     user_id = len(users_db) + 1
#     users_db[user_id] = user
#     return {"user_id": user_id, **user.dict()}
#
#
# @app.get("/users/{user_id}", response_model=User)
# def read_user(user_id: int):
#     if user_id not in users_db:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {"user_id": user_id, **users_db[user_id].dict()}
#
#
# @app.put("/users/{user_id}", response_model=User)
# def update_user(user_id: int, updated_user: User):
#     if user_id not in users_db:
#         raise HTTPException(status_code=404, detail="User not found")
#     users_db[user_id] = updated_user
#     return updated_user
#
#
# @app.delete("/users/{user_id}", response_model=User)
# def delete_user(user_id: int):
#     if user_id not in users_db:
#         raise HTTPException(status_code=404, detail="User not found")
#     deleted_user = users_db.pop(user_id)
#     return deleted_user
#
#
# @app.get("/user/", response_model=dict[int, User])
# def get_all_user():
#     return users_db
#
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# using sqlaalchemy

from fastapi import FastAPI
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi import Query
from fastapi import HTTPException
from dotenv import load_dotenv
import os
#repo
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#model
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)


Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/items/")
@app.post("/items/", response_model=dict)
def create_item(name: str, description: str):
    db = SessionLocal()
    db_item = Item(name=name, description=description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"message": "Item posted successfully"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not foundddd")
    return item


@app.put("/items/{item_id}", response_model=dict)
def update_item(item_id: int, name: str, description: str):
    db = SessionLocal()
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.name = name
    db_item.description = description
    db.commit()
    return {"message": "Item updated successfully"}


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    db = SessionLocal()
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}


@app.get("/items/")
def get_all_item():
    db = SessionLocal()
    item = db.query(Item).all()
    return item


@app.get("/items/")
def get_all_item(name: str = Query(None, title="Name", description="Search by item name or description"),
                 description: str = Query(None, title="Description", description="Search by item description")):
    db = SessionLocal()
    query = db.query(Item)
    if name:
        query = query.filter(Item.name.ilike(f"%{name}%"))
    if description:
        query = query.filter(Item.description.ilike(f"%{description}%"))
    items = query.all()
    return items
