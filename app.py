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
                        reviews,
)

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

app.include_router(discounts.router, prefix="/api")
app.include_router(product_discounts.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(message.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(faq_loader.router, prefix="/api")
app.include_router(fqas.router, prefix="/api")
app.include_router(polici_agent.router, prefix="/api")
app.include_router(qdrant_agent.router, prefix="/api")
app.include_router(manager.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")


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
