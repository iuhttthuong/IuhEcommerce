import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from app_environment import AppEnvironment
from env import env
import alembic.config # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from controllers import (discounts,
                        product_discounts,
                        chat,
                        customers,
                        message,
                        products,
                        search,
                        faq_loader,
                        fqas,
                        polici_agent,
                        qdrant_agent,
                        manager,
                        orchestrator_agent,
                        review_agent,
                        recommendation_agent,
                        product_comparison_agent,
                        product_info_agent,
                        search_discovery_agent,
                        user_profile_agent,
                        shops
)
from controllers.shops import router as shop_controller
from routers.shop_chat import router as shop_chat_router
from routers.shop import router as shop_router

from starlette.middleware.base import BaseHTTPMiddleware

# Migrate the database to its latest version
# Not thread safe, so it should be update once we are running multiple instances
alembic.config.main(argv=["--raiseerr", "upgrade", "head"])

# Create FastAPI app
app = FastAPI(
    title="IUH E-commerce API",
    description="API for IUH E-commerce platform with separate customer and shop chat systems",
    version="1.0.0",
    debug=env.DEBUG
)

# Add CORS middleware for local development
if AppEnvironment.is_local_env(env.APP_ENV):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Customer related endpoints
app.include_router(chat.router, prefix="/api/customer/chat", tags=["Customer Chat"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(message.router, prefix="/api/customer/messages", tags=["Customer Messages"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(discounts.router, prefix="/api/discounts", tags=["Discounts"])
app.include_router(product_discounts.router, prefix="/api/product-discounts", tags=["Product Discounts"])

# Shop related endpoints
app.include_router(shops.router, prefix="/api/shops", tags=["Shops"])
app.include_router(shop_chat_router, prefix="/api/shop/chat", tags=["Shop Chat"])
app.include_router(shop_router, prefix="/api/shop", tags=["Shop Management"])

# FAQ and Policy endpoints
app.include_router(faq_loader.router, prefix="/api/faq-loader", tags=["FAQ Loader"])
app.include_router(fqas.router, prefix="/api/fqas", tags=["FAQs"])
app.include_router(polici_agent.router, prefix="/api/policies-agent", tags=["Policies"])

# AI Agents endpoints
app.include_router(qdrant_agent.router, prefix="/api/qdrant-agent", tags=["Qdrant Agent"])
app.include_router(manager.router, prefix="/api/manager", tags=["Manager"])
app.include_router(orchestrator_agent.router, prefix="/api/orchestrator", tags=["Orchestrator"])
app.include_router(review_agent.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(recommendation_agent.router, prefix="/api/recommendation", tags=["Recommendation"])
app.include_router(product_comparison_agent.router, prefix="/api/product-comparison", tags=["Product Comparison"])
app.include_router(product_info_agent.router, prefix="/api/product-info", tags=["Product Info"])
app.include_router(search_discovery_agent.router, prefix="/api/search-discovery", tags=["Search Discovery"])
app.include_router(user_profile_agent.router, prefix="/api/user-profile", tags=["User Profile"])

# Static file middleware
class StaticFileMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        static_dir = "static"

        file_path = os.path.join(static_dir, path.lstrip("/"))
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)

        return await call_next(request)

app.add_middleware(StaticFileMiddleware)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "chat_systems": {
            "customer_chat": "/api/customer/chat",
            "shop_chat": "/api/shop/chat"
        }
    }
