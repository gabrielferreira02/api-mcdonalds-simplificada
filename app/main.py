from fastapi import FastAPI

app = FastAPI()

from app.api.routes.category_routes import category_router

app.include_router(category_router)