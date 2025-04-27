from fastapi import APIRouter
from .users import user_router
from .vendors import vendor_router
from .schemes import scheme_router
from .transactions import router as transaction_router

# Create main router
router = APIRouter()

# Include all routers
router.include_router(user_router)
router.include_router(vendor_router)
router.include_router(scheme_router)
router.include_router(transaction_router) 