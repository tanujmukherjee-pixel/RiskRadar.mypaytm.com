from fastapi import FastAPI, Request
from .controllers.chat import router as chat_router
from .controllers.agent import router as agent_router
from .controllers.tool import router as tool_router
from .bootstap import bootstrap
from dotenv import load_dotenv
import logging
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables first
load_dotenv(override=True, dotenv_path=".env")

# Create FastAPI app
app = FastAPI(
    title="Agency API",
    description="API for agent-based services",
    version="1.0.0"
)

# Include routers
app.include_router(chat_router)
app.include_router(agent_router)
app.include_router(tool_router)

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to the specific origins you want to allow
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bootstrap the application
@app.on_event("startup")
async def startup_event():
    """
    FastAPI startup event handler.
    
    This initializes the application in the following order:
    1. Tools and agent repositories are bootstrapped concurrently
    2. Essential models are loaded as a blocking operation
    3. Non-essential models begin loading in the background
    
    The API will be available as soon as essential models are loaded,
    but requests to non-essential models that are still loading will
    receive a "model is loading" message.
    """
    start_time = time.time()
    logger.info("Starting application initialization...")
    
    # Our bootstrap function handles both sync and async contexts
    # It will load essential models first, then start loading non-essential models
    # in the background
    bootstrap()
    
    logger.info(f"Application initialization complete in {time.time() - start_time:.2f}s")
    logger.info("API is now ready to accept requests")
    logger.info("Note: Some models may still be loading in the background")

# Optional request logging middleware
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     import logging
#     logger = logging.getLogger("uvicorn")
#     body = await request.body()
#     logger.info(f"Request path: {request.url.path}")
#     logger.info(f"Request body: {body}")
#     response = await call_next(request)
#     return response