import os
from pathlib import Path
import pkg_resources
import logging
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex, load_index_from_storage, StorageContext

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_key = "REDACTED_OPENAI_KEY"

def get_storage_path():
    """Get the storage-graph path for both development and installed modes."""
    # When running as python -m src (development mode)
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    storage_path = project_root / 'storage-graph'
    
    # If not found, try installed package location
    if not storage_path.exists():
        try:
            dist = pkg_resources.get_distribution('src')
            site_packages = Path(dist.location)
            installed_path = site_packages / 'storage-graph'
            if installed_path.exists():
                storage_path = installed_path
        except pkg_resources.DistributionNotFound:
            # If package not found, try one level up from current file
            alternative_path = current_file.parent.parent / 'storage-graph'
            if alternative_path.exists():
                storage_path = alternative_path
    
    if not storage_path.exists():
        raise FileNotFoundError(
            f"Storage directory not found. Tried:\n"
            f"1. Development path: {project_root / 'storage-graph'}\n"
            f"2. Installed path: {storage_path}\n"
            "Make sure you're either:\n"
            "- Running 'python -m src' from the project root\n"
            "- Or the package is installed correctly with pip"
        )
    
    print(f"Using storage path: {storage_path}")  # Debug print
    return str(storage_path)

def get_query_engine():
    """
    Sets up the query engine using Azure OpenAI for LLM and HuggingFace for embeddings.
    Configures Neo4j as a vector store if the database option is enabled.
    """
    llm = OpenAI(
        model="gpt-4o",
        api_key=api_key
    )

    embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    Settings.llm = llm
    Settings.embed_model = embed_model

    # documents = SimpleDirectoryReader(input_dir="./data/agents/devrev/docs", recursive=True).load_data()

    # index = VectorStoreIndex.from_documents(documents)

    # Persist index to storage
    # index.storage_context.persist(persist_dir="./data/agents/devrev/storage-graph")

    storage_context = StorageContext.from_defaults(
        persist_dir="./data/agents/devrev/storage-graph"
    )

    # load index
    index = load_index_from_storage(storage_context)


    query_engine = index.as_query_engine(
        include_text=True, response_mode="tree_summarize"
    )

    return query_engine

# query_engine = get_query_engine()