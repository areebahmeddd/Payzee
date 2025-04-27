from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, TypeVar, Generic, Type
from pydantic import BaseModel
from ..database import get_db

T = TypeVar('T')
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)
ResponseSchema = TypeVar('ResponseSchema', bound=BaseModel)

class BaseRouter(Generic[T, CreateSchema, UpdateSchema, ResponseSchema]):
    def __init__(
        self,
        model: Type[T],
        create_schema: Type[CreateSchema],
        update_schema: Type[UpdateSchema],
        response_schema: Type[ResponseSchema],
        prefix: str,
        tags: List[str]
    ):
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.response_schema = response_schema
        
        # Register routes
        self.router.add_api_route(
            "/",
            self.create,
            response_model=response_schema,
            methods=["POST"]
        )
        self.router.add_api_route(
            "/",
            self.read_all,
            response_model=List[response_schema],
            methods=["GET"]
        )
        self.router.add_api_route(
            "/{item_id}",
            self.read_one,
            response_model=response_schema,
            methods=["GET"]
        )
        self.router.add_api_route(
            "/{item_id}",
            self.update,
            response_model=response_schema,
            methods=["PUT"]
        )
        self.router.add_api_route(
            "/{item_id}",
            self.delete,
            response_model=response_schema,
            methods=["DELETE"]
        )

    async def create(self, item: CreateSchema, db: Session = Depends(get_db)) -> ResponseSchema:
        db_item = self.model(**item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    async def read_all(self, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[ResponseSchema]:
        items = db.query(self.model).offset(skip).limit(limit).all()
        return items

    async def read_one(self, item_id: str, db: Session = Depends(get_db)) -> ResponseSchema:
        item = db.query(self.model).filter(self.model.id == item_id).first()
        if item is None:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        return item

    async def update(self, item_id: str, item: UpdateSchema, db: Session = Depends(get_db)) -> ResponseSchema:
        db_item = db.query(self.model).filter(self.model.id == item_id).first()
        if db_item is None:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        
        for key, value in item.dict(exclude_unset=True).items():
            setattr(db_item, key, value)
        
        db.commit()
        db.refresh(db_item)
        return db_item

    async def delete(self, item_id: str, db: Session = Depends(get_db)) -> ResponseSchema:
        db_item = db.query(self.model).filter(self.model.id == item_id).first()
        if db_item is None:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        
        db.delete(db_item)
        db.commit()
        return db_item 