from fastapi import FastAPI
from .controllers.chat import router as chat_router
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

app = FastAPI()

app.include_router(chat_router)
