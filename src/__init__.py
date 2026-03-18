"""Agency FastAPI application."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from .controllers.chat import router as chat_router
from .controllers.mcc import router as mcc_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(chat_router)
app.include_router(mcc_router)

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     import logging
#     logger = logging.getLogger("uvicorn")
#     body = await request.body()
#     logger.info(f"Request path: {request.url.path}")
#     logger.info(f"Request body: {body}")
#     response = await call_next(request)
#     return response
