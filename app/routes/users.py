from fastapi import APIRouter
from ..models import User
from ..schemas import UserCreate, UserUpdate, User as UserSchema
from .base import BaseRouter

# Create user router
user_router = BaseRouter(
    model=User,
    create_schema=UserCreate,
    update_schema=UserUpdate,
    response_schema=UserSchema,
    prefix="/users",
    tags=["users"]
).router 