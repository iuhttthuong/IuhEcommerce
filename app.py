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
from controllers.shops import controller as shop_controller

from starlette.middleware.base import BaseHTTPMiddleware

from env import env

# Migrate the database to its latest version
# Not thread safe, so it should be update once we are running multiple instances
alembic.config.main(argv=["--raiseerr", "upgrade", "head"])

app = FastAPI(debug=env.DEBUG)

if AppEnvironment.is_local_env(env.APP_ENV):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(discounts.router, prefix="/discounts")
app.include_router(product_discounts.router, prefix="/product_discounts")
app.include_router(chat.router, prefix="/chats")
app.include_router(customers.router, prefix="/customers")
app.include_router(message.router, prefix="/messages")
app.include_router(products.router, prefix="/products")
app.include_router(search.router, prefix="/search")
app.include_router(faq_loader.router, prefix="/faq_loader")
app.include_router(fqas.router, prefix="/fqas")
app.include_router(polici_agent.router, prefix="/policies_agent")
app.include_router(qdrant_agent.router, prefix="/qdrant_agent")
app.include_router(manager.router, prefix="/manager")
app.include_router(orchestrator_agent.router, prefix="/orchestrator")
app.include_router(review_agent.router, prefix="/reviews")
app.include_router(recommendation_agent.router, prefix="/recommendation")
app.include_router(product_comparison_agent.router, prefix="/product_comparison")
app.include_router(product_info_agent.router, prefix="/product_info")
app.include_router(search_discovery_agent.router, prefix="/search_discovery")
app.include_router(user_profile_agent.router, prefix="/user_profile")
app.include_router(shops.router)
    
class StaticFileMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        static_dir = "static"

        file_path = os.path.join(static_dir, path.lstrip("/"))
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)

        # Nếu không tìm thấy trong static, chuyển đến next middleware
        return await call_next(request)


app.add_middleware(StaticFileMiddleware)
