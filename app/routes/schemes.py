from fastapi import APIRouter
from ..models import Scheme
from ..schemas import SchemeCreate, SchemeUpdate, Scheme as SchemeSchema
from .base import BaseRouter

# Create scheme router
scheme_router = BaseRouter(
    model=Scheme,
    create_schema=SchemeCreate,
    update_schema=SchemeUpdate,
    response_schema=SchemeSchema,
    prefix="/schemes",
    tags=["schemes"]
).router 