from .services.tools import tools_service
from .services.agent import agent_service
from .services.model import model_service
import asyncio
import logging
import time
import sys

logger = logging.getLogger(__name__)

async def bootstrap_async():
    """
    Asynchronously bootstrap the application with concurrency optimizations.
    This runs tools and agents bootstrapping concurrently for faster startup.
    
    The function ensures that:
    1. Tools and agents are bootstrapped concurrently
    2. Essential models are loaded first
    3. Non-essential models are loaded in the background
    """
    start_time = time.time()
    logger.info("Starting application bootstrap...")
    
    # Run tools and agents bootstrapping concurrently
    await asyncio.gather(
        tools_service.bootstrap(),
        agent_service.bootstrap()
    )
    
    # Now start loading models with prioritization
    logger.info("Starting model initialization...")
    await model_service.initialize_models()
    
    elapsed_time = time.time() - start_time
    logger.info(f"Application bootstrap completed in {elapsed_time:.2f} seconds")
    logger.info("Non-essential models will continue loading in the background")

def bootstrap():
    """
    Safely bootstrap the application, handling both sync and async contexts.
    This function will work correctly whether called from a synchronous context
    or from within an already running event loop.
    """
    # Check if we're in an event loop already
    try:
        loop = asyncio.get_event_loop()
        
        # Check if the loop is already running
        if loop.is_running():
            logger.info("Event loop already running, creating bootstrap task")
            # We're in an async context with a running loop, so we create a task
            # instead of blocking with run_until_complete
            asyncio.create_task(bootstrap_async())
        else:
            # We have a loop but it's not running, so we can use run_until_complete
            logger.info("Using existing event loop for bootstrap")
            loop.run_until_complete(bootstrap_async())
    except RuntimeError:
        # No event loop exists, create one
        logger.info("No event loop found, creating new loop for bootstrap")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bootstrap_async())