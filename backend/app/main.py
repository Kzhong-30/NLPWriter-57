from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole, UserStatus
from app.api import api_router

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            default_admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="系统管理员",
                role=UserRole.ADMIN.value,
                status=UserStatus.APPROVED.value,
                is_active=True
            )
            db.add(default_admin)
            db.commit()
            db.refresh(default_admin)
    finally:
        db.close()

init_db()

app = FastAPI(
    title="Volunteer Service Platform API",
    description="志愿服务平台 RESTful API",
    version="1.0.0",
)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["root"])
def root():
    return {
        "message": "Welcome to Volunteer Service Platform API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
