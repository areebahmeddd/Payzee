from fastapi import APIRouter
from ..models import Vendor
from ..schemas import VendorCreate, VendorUpdate, Vendor as VendorSchema
from .base import BaseRouter

# Create vendor router
vendor_router = BaseRouter(
    model=Vendor,
    create_schema=VendorCreate,
    update_schema=VendorUpdate,
    response_schema=VendorSchema,
    prefix="/vendors",
    tags=["vendors"]
).router 