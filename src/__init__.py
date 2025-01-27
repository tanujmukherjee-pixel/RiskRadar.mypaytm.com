from fastapi import FastAPI
from .controllers.chat import router as chat_router

app = FastAPI()

app.include_router(chat_router)
