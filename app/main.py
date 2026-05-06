from fastapi import FastAPI

app = FastAPI()

from app.api.routes.category_routes import category_router
from app.api.routes.product_routes import product_router
from app.api.routes.auth_routes import auth_router

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(product_router)