from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import router as auth_router
from app.user.main import router as user_router
from app.vendor.main import router as vendor_router
from app.government.main import router as government_router

app = FastAPI(
    title="Payzee API",
    description="API for Payzee application",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(user_router, prefix="/api/v1/user")
app.include_router(vendor_router, prefix="/api/v1/vendor")
app.include_router(government_router, prefix="/api/v1/government")


@app.get("/health")
def health_check():
    return {"status": "ok"}
