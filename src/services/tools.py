from typing import Dict, List, Any
from llama_index.core.tools import FunctionTool
from ..tools import tools
from ..constants.path import TOOLS_PATH
from ..repositories.tool import get_repository as get_tool_repository
from ..repositories.noop_tool import get_repository as get_noop_tool_repository
from ..utils.file import write_file
from ..utils.python import _install_imports, _fetch_imports
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import logging

logger = logging.getLogger(__name__)

class Tools:
    def __init__(self):
        self.tools: Dict[str, FunctionTool] = {}
        
        # Thread safety locking
        self._tools_lock = asyncio.Lock()
        
        # Thread pool for CPU-bound operations
        self._executor = ThreadPoolExecutor(max_workers=10)
        
        if os.environ.get("DISABLE_DATABASE"):
            self.tool_repository = get_noop_tool_repository()
        else:
            self.tool_repository = get_tool_repository()
            
        self._populate_tools()

    async def bootstrap(self):
        """Bootstrap tools with concurrent processing."""
        logger.info("Bootstrapping tools")
        
        # Fetch tools from repository
        loop = asyncio.get_event_loop()
        tools = await loop.run_in_executor(
            self._executor,
            self.tool_repository.list_tools
        )
        
        # Create tasks for concurrent processing
        tasks = []
        for tool in tools:
            task = asyncio.create_task(self._process_tool(tool))
            tasks.append(task)
            
        # Wait for all tools to be processed
        await asyncio.gather(*tasks)
        
        logger.info(f"Tools bootstrapped - {len(tools)} tools loaded")

    async def _process_tool(self, tool):
        """Process a single tool concurrently."""
        try:
            # Parse imports from tool content
            imports = _fetch_imports(tool['file_content'])
            
            # Install imports in a thread pool to not block
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: _install_imports(imports)
            )
            
            # Create directory if needed
            os.makedirs(os.path.dirname(TOOLS_PATH.format(tool_name=tool['name'])), exist_ok=True)
            
            # Write file in a thread pool to not block
            tool_path = TOOLS_PATH.format(tool_name=tool['name'])
            await loop.run_in_executor(
                self._executor,
                lambda: write_file(tool_path, tool['file_content'])
            )
            
            # Load the tool
            await self._load_tool(tool['name'])
            
            logger.info(f"Tool '{tool['name']}' bootstrapped")
        except Exception as e:
            logger.error(f"Error bootstrapping tool {tool['name']}: {str(e)}")

    def _populate_tools(self):
        """Populate built-in tools."""
        for tool_name, tool in tools.items():
            self.tools[tool_name] = tool

    async def add_tool(self, tool):
        """Add a tool with thread safety."""
        async with self._tools_lock:
            self.tools.append(tool)

    def get_tool(self, tool_name: str) -> FunctionTool:
        """Get a tool by name."""
        if tool_name not in self.tools:
            raise KeyError(f"Tool {tool_name} not found.")
        return self.tools[tool_name]

    def get_all_tools(self) -> Dict[str, FunctionTool]:
        """Get all tools."""
        return self.tools

    async def save_tool(self, tools: Dict[str, str], imports: List[str]) -> Dict[str, str]:
        """Save tools concurrently."""
        # Process file saving operations concurrently
        contents = await self._save_tool_files(tools, imports)
        
        # Process database operations concurrently
        tasks = []
        for tool_name, tool_content in contents.items():
            tool_data = {
                "name": tool_name,
                "description": tool_name,
                "file_content": contents[tool_name],
            }
            task = asyncio.create_task(
                self._save_and_load_tool(tool_data, tool_name)
            )
            tasks.append(task)
            
        # Wait for all save operations to complete
        await asyncio.gather(*tasks)
        
        return contents

    async def _save_and_load_tool(self, tool_data: dict, tool_name: str):
        """Save a tool to the database and load it."""
        try:
            # Run database operation in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: self.tool_repository.create_tool(tool_data)
            )
            
            # Load the tool
            await self._load_tool(tool_name)
            
            logger.info(f"Tool '{tool_name}' saved and loaded")
        except Exception as e:
            logger.error(f"Error saving tool {tool_name}: {str(e)}")

    async def _load_tool(self, tool_name: str) -> FunctionTool:
        """Load a tool with thread safety."""
        try:
            # Import function from saved file path
            spec = importlib.util.spec_from_file_location(tool_name, TOOLS_PATH.format(tool_name=tool_name))
            module = importlib.util.module_from_spec(spec)
            
            # Execute module in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: spec.loader.exec_module(module)
            )
            
            # Create function tool
            function_tool = FunctionTool.from_defaults(fn=getattr(module, tool_name))
            
            # Store with thread safety
            async with self._tools_lock:
                self.tools[tool_name] = function_tool
                
            return function_tool
        except Exception as e:
            logger.error(f"Error loading tool {tool_name}: {str(e)}")
            raise

    async def _save_tool_files(self, tools: Dict[str, str], imports: List[str]) -> Dict[str, str]:
        """Save tool files concurrently."""
        tasks = []
        for tool_name, tool_content in tools.items():
            task = asyncio.create_task(
                self._save_single_tool_file(tool_name, tool_content, imports)
            )
            tasks.append((tool_name, task))
            
        # Wait for all file writes to complete
        contents = {}
        for tool_name, task in tasks:
            try:
                file_content = await task
                contents[tool_name] = file_content
            except Exception as e:
                logger.error(f"Error saving tool file {tool_name}: {str(e)}")
                
        return contents

    async def _save_single_tool_file(self, tool_name: str, tool_content: str, imports: List[str]) -> str:
        """Save a single tool file with thread pool for I/O operations."""
        # Create directory if needed
        os.makedirs(os.path.dirname(TOOLS_PATH.format(tool_name=tool_name)), exist_ok=True)
        tool_path = TOOLS_PATH.format(tool_name=tool_name)
        
        # Prepare file content
        file_content = ""
        for import_statement in imports:
            file_content += import_statement + "\n"
        file_content += "\n"
        file_content += tool_content
        
        # Write file in thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self._executor,
            lambda: write_file(tool_path, file_content)
        )
        
        return file_content

    async def delete_tool(self, tool_name: str) -> None:
        """Delete a tool with thread safety."""
        try:
            # Delete from database in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: self.tool_repository.delete_tool(tool_name)
            )
            
            # Remove from tools dictionary with thread safety
            async with self._tools_lock:
                if tool_name in self.tools:
                    self.tools.pop(tool_name)
            
            # Delete file if it exists
            tool_path = TOOLS_PATH.format(tool_name=tool_name)
            if os.path.exists(tool_path):
                await loop.run_in_executor(
                    self._executor,
                    lambda: os.remove(tool_path)
                )
                
            logger.info(f"Tool '{tool_name}' deleted")
        except Exception as e:
            logger.error(f"Error deleting tool {tool_name}: {str(e)}")
            raise

# Singleton instance
tools_service = Tools()