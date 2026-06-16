from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "https://mequizin.netlify.app"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

from app.api.routes.category_routes import category_router
from app.api.routes.product_routes import product_router
from app.api.routes.auth_routes import auth_router
from app.api.routes.order_routes import order_router
from app.api.routes.stripe_routes import stripe_router
from app.api.routes.user_routes import user_router

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(stripe_router)
app.include_router(user_router)