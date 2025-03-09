from fastapi import FastAPI, Request
from .controllers.chat import router as chat_router
from .controllers.agent import router as agent_router
from .controllers.tool import router as tool_router
from .bootstap import bootstrap
app = FastAPI()

app.include_router(chat_router)
app.include_router(agent_router)
app.include_router(tool_router)
bootstrap()


# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     import logging
#     logger = logging.getLogger("uvicorn")
#     body = await request.body()
#     logger.info(f"Request path: {request.url.path}")
#     logger.info(f"Request body: {body}")
#     response = await call_next(request)
#     return response