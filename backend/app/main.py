from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.api.routes import auth, patients, procedures, dashboard, audit


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (use alembic migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="VQI Georgia",
    description="Vascular Quality Initiative Registry for Georgia",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(procedures.router)
app.include_router(dashboard.router)
app.include_router(audit.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "VQI Georgia"}
