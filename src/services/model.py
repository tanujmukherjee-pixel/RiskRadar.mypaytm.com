from typing import Dict, List, Optional, AsyncGenerator, Any
from ..agents.base import BaseAgent
from ..agents.funnel.funnel import FunnelAgent
from ..agents.ba.ba import BaAgent
from ..agents.self_heal.self_heal import SelfHealAgent
from ..agents.bitbucket.bitbucket import BitbucketAgent
from ..agents.rc_lookup.rc_lookup import RcLookupAgent
from ..domains.chat import ModelResponse, ModelsResponse, ChatMessage, ChatResponse, Choice, Message
from ..rags.base import BaseRAG
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class ModelStatus(Enum):
    """Status of a model in the system."""
    NOT_LOADED = "not_loaded"  # Model is defined but not loaded yet
    LOADING = "loading"        # Model is currently being loaded
    LOADED = "loaded"          # Model is fully loaded and ready to use
    FAILED = "failed"          # Model failed to load

class ModelService:
    def __init__(self):
        # Define essential models that should be loaded first
        self._essential_models = ["funnel", "ba"]
        
        # Define model factories - don't load anything yet
        self._model_factories = {
            "funnel": lambda: FunnelAgent(),
            "ba": lambda: BaAgent(),
            "bitbucket": lambda: BitbucketAgent(),
            "neo4j": lambda: BaseRAG("neo4j"),
            # "self-heal": lambda: SelfHealAgent(),
            "rc-lookup": lambda: RcLookupAgent()
        }
        
        # Track loaded models
        self._loaded_models: Dict[str, Any] = {}
        
        # Track model loading status
        self._model_status: Dict[str, ModelStatus] = {
            model_id: ModelStatus.NOT_LOADED for model_id in self._model_factories.keys()
        }
        
        # Track loading errors
        self._model_errors: Dict[str, str] = {}
        
        # Thread pool for CPU-bound operations
        self._executor = ThreadPoolExecutor(max_workers=10)
        
        # Locking mechanism for thread safety
        self._models_lock = asyncio.Lock()
        
        # Loading is started in the background by bootstrap process
        # Don't start initialization here to avoid blocking app startup
    
    async def initialize_models(self):
        """
        Initialize all models with a prioritized approach:
        1. Load essential models first (synchronously)
        2. Then load remaining models asynchronously in the background
        """
        await self._load_essential_models()
        asyncio.create_task(self._load_remaining_models())
    
    async def _load_essential_models(self):
        """Load essential models first in a blocking manner."""
        logger.info(f"Loading essential models: {', '.join(self._essential_models)}")
        
        # Load essential models one by one to ensure they're loaded quickly
        for model_id in self._essential_models:
            if model_id in self._model_factories:
                logger.info(f"Loading essential model: {model_id}")
                await self._load_model(model_id)
        
        logger.info("Essential models loaded")
    
    async def _load_remaining_models(self):
        """Load all non-essential models asynchronously in the background."""
        # Get all non-essential models
        remaining_models = [
            model_id for model_id in self._model_factories.keys() 
            if model_id not in self._essential_models
        ]
        
        if not remaining_models:
            logger.info("No remaining models to load")
            return
            
        logger.info(f"Loading remaining models in background: {', '.join(remaining_models)}")
        
        # Create tasks for loading models concurrently
        tasks = []
        for model_id in remaining_models:
            task = asyncio.create_task(self._load_model(model_id))
            tasks.append(task)
        
        # Wait for all models to be loaded
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("All remaining models loaded")
    
    async def _load_model(self, model_id: str) -> Optional[Any]:
        """Load a single model with status tracking."""
        # Check if the model is already loaded
        if model_id in self._loaded_models and self._model_status.get(model_id) == ModelStatus.LOADED:
            return self._loaded_models[model_id]
        
        # Use a lock to ensure only one thread loads a model at a time
        async with self._models_lock:
            # Double-check pattern - check again after acquiring the lock
            if model_id in self._loaded_models and self._model_status.get(model_id) == ModelStatus.LOADED:
                return self._loaded_models[model_id]
            
            # Check if the model factory exists
            if model_id not in self._model_factories:
                logger.error(f"No factory found for model: {model_id}")
                self._model_status[model_id] = ModelStatus.FAILED
                self._model_errors[model_id] = f"No factory found for model: {model_id}"
                return None
            
            # Mark model as loading
            self._model_status[model_id] = ModelStatus.LOADING
            start_time = time.time()
            
            try:
                # Load the model in a thread pool to avoid blocking the event loop
                loop = asyncio.get_event_loop()
                model = await loop.run_in_executor(
                    self._executor,
                    self._model_factories[model_id]
                )
                
                # Store the loaded model
                self._loaded_models[model_id] = model
                self._model_status[model_id] = ModelStatus.LOADED
                
                # Clear any previous errors
                if model_id in self._model_errors:
                    del self._model_errors[model_id]
                
                loading_time = time.time() - start_time
                logger.info(f"Model '{model_id}' loaded successfully in {loading_time:.2f} seconds")
                return model
                
            except Exception as e:
                # Handle loading errors
                error_msg = f"Error loading model '{model_id}': {str(e)}"
                logger.error(error_msg)
                self._model_status[model_id] = ModelStatus.FAILED
                self._model_errors[model_id] = str(e)
                return None

    async def _get_model(self, model_id: str) -> Any:
        """
        Get a model, potentially triggering a load if needed.
        This also handles the case where the model is currently loading.
        """
        # Check if the model is already loaded
        if model_id in self._loaded_models and self._model_status.get(model_id) == ModelStatus.LOADED:
            return self._loaded_models[model_id]
        
        # Check if model exists
        if model_id not in self._model_factories:
            raise ValueError(f"Model {model_id} not found")
        
        # Check model status
        status = self._model_status.get(model_id, ModelStatus.NOT_LOADED)
        
        if status == ModelStatus.LOADING:
            # Model is currently loading
            raise ValueError(f"Model {model_id} is currently loading. Please try again in a few minutes.")
        
        elif status == ModelStatus.FAILED:
            # Model failed to load
            error = self._model_errors.get(model_id, "Unknown error")
            raise ValueError(f"Model {model_id} failed to load: {error}")
        
        elif status == ModelStatus.NOT_LOADED:
            # Model needs to be loaded
            logger.info(f"Loading model on demand: {model_id}")
            model = await self._load_model(model_id)
            if model is None:
                raise ValueError(f"Failed to load model {model_id}")
            return model
        
        else:
            # Should never happen, but just in case
            raise ValueError(f"Unknown model status: {status}")

    async def chat_completion(self, model_id: str, messages: List[ChatMessage], max_tokens: Optional[int] = 50, temperature: Optional[float] = 0.7) -> AsyncGenerator[ChatResponse, None]:
        """Handle chat completion with proper error handling for loading states."""
        try:
            # Try to get the model, which may be loading
            model = await self._get_model(model_id)
            
            # Process the chat completion through the model
            async for response_chunk in model.chat_completion(messages, max_tokens, temperature):
                yield response_chunk
                
        except ValueError as e:
            # Special handling for "model is loading" state
            error_message = str(e)
            is_loading = "currently loading" in error_message
            
            logger.warning(f"Model access issue: {error_message}")
            
            if is_loading:
                # Special message for models that are still loading
                yield ChatResponse(
                    id="loading",
                    object="chat.completion",
                    created=int(time.time()),
                    model=model_id,
                    choices=[
                        Choice(
                            index=0,
                            message=Message(
                                role="assistant", 
                                content=f"The model is currently initializing. Please wait a few minutes and try again."
                            ),
                            finish_reason="stop"
                        )
                    ]
                )
            else:
                # Other model not found or failed errors
                yield ChatResponse(
                    id="error",
                    object="chat.completion",
                    created=int(time.time()),
                    model=model_id,
                    choices=[
                        Choice(
                            index=0,
                            message=Message(role="assistant", content=f"Error: {error_message}"),
                            finish_reason="stop"
                        )
                    ]
                )
        except Exception as e:
            # Other errors
            logger.error(f"Error in chat completion for model {model_id}: {str(e)}")
            yield ChatResponse(
                id="error",
                object="chat.completion",
                created=int(time.time()),
                model=model_id,
                choices=[
                    Choice(
                        index=0,
                        message=Message(role="assistant", content=f"I'm sorry, I encountered an error"),
                        finish_reason="stop"
                    )
                ]
            )

    def list_models(self) -> ModelsResponse:
        """List all available models with their loading status."""
        all_model_ids = list(set(self._loaded_models.keys()) | set(self._model_factories.keys()))
        return ModelsResponse(
            object="list", 
            data=[
                ModelResponse(
                    id=model_id, 
                    object="model", 
                    created=0, 
                    owned_by="system"
                ) 
                for model_id in all_model_ids
            ]
        )
    
    def get_model_info(self, model_id: str) -> dict:
        """Get information about a model including its loading status."""
        if model_id not in self._model_factories and model_id not in self._loaded_models:
            raise ValueError(f"Model {model_id} not found.")
        
        # Get status information
        status = self._model_status.get(model_id, ModelStatus.NOT_LOADED).value
        is_essential = model_id in self._essential_models
        error = self._model_errors.get(model_id, None)
        
        return {
            "model_id": model_id,
            "description": f"Information about {model_id}",
            "status": status,
            "is_essential": is_essential,
            "error": error
        }
    
    async def delete_model(self, model_id: str):
        """Delete a model with proper synchronization."""
        async with self._models_lock:
            # Remove from loaded models if it exists
            self._loaded_models.pop(model_id, None)
            
            # Update status
            if model_id in self._model_status:
                self._model_status[model_id] = ModelStatus.NOT_LOADED
            
            # Remove from errors if present
            self._model_errors.pop(model_id, None)
            
            # Remove from factories if present
            self._model_factories.pop(model_id, None)
            
            logger.info(f"Model '{model_id}' deleted")
    
    async def add_model(self, model_id: str, model: Any):
        """Add a new model with proper synchronization."""
        async with self._models_lock:
            # Store the model directly as loaded
            self._loaded_models[model_id] = model
            
            # Update status
            self._model_status[model_id] = ModelStatus.LOADED
            
            # Add a factory that returns this instance
            self._model_factories[model_id] = lambda: model
            
            logger.info(f"Model '{model_id}' added")

# Singleton instance
model_service = ModelService()