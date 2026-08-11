from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import recipes, auth, users, search
from app.config import settings

app = FastAPI(title="Recipe App API", version="0.1.0")

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

app.include_router(recipes.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/health")

def health():
    return {"status": "ok"}