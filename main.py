from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from routes.admin import admin_router

app = FastAPI()

# Allow CORS for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_router = APIRouter()

@main_router.get("/health")
async def root():
    return {"message": "I am alive!"}

app.include_router(main_router)
app.include_router(admin_router)