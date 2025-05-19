from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.shop.chat import router as shop_chat_router
from controllers.shop.controller import router as shop_router
from controllers.shop.product_management import router as product_router
from controllers.shop.inventory import router as inventory_router
from controllers.shop.order import router as order_router
from controllers.shop.marketing import router as marketing_router
from controllers.shop.analytics import router as analytics_router
from controllers.shop.finance import router as finance_router
from controllers.shop.policy import router as policy_router
from controllers.shop.customer_service import router as customer_service_router

app = FastAPI(title="IUH-Ecommerce API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(shop_router)
app.include_router(shop_chat_router)  # Add shop chat router
app.include_router(product_router)
app.include_router(inventory_router)
app.include_router(order_router)
app.include_router(marketing_router)
app.include_router(analytics_router)
app.include_router(finance_router)
app.include_router(policy_router)
app.include_router(customer_service_router)

@app.get("/")
async def root():
    return {"message": "Welcome to IUH-Ecommerce API"} 