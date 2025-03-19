import os
from pathlib import Path
import pkg_resources
import logging
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.core import Settings, load_index_from_storage, StorageContext
import sys
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import StorageContext
from llama_index.core import Settings
from src.constants.path import DOCS_PATH, STORAGE_GRAPH_PATH

class BaseRAG:

    def __init__(self, name: str):
        self.name = name

    def get_query_engine(self):
        """
        Sets up the query engine using OpenAI for LLM and OpenAI for embeddings.
        """
        llm = OpenAI(
            model=os.environ.get("LLM_MODEL"),
            api_key=os.environ.get("OPENAI_API_KEY"),
            api_base=os.environ.get("OPENAI_API_BASE")
        )

        embed_model = OpenAIEmbedding(
            model_name=os.environ.get("EMBEDDING_MODEL"),
            api_key=os.environ.get("OPENAI_API_KEY"),
            api_base=os.environ.get("OPENAI_API_BASE")
        )

        Settings.llm = llm
        Settings.embed_model = embed_model

        # Check if storage path exists
        storage_path = STORAGE_GRAPH_PATH.format(agent_name=self.name)
        if os.path.exists(storage_path):
            # Load existing index from storage
            storage_context = StorageContext.from_defaults(persist_dir=storage_path)
            index = load_index_from_storage(storage_context)
        else:
            # Create new index from documents
            documents = SimpleDirectoryReader(input_dir=DOCS_PATH.format(agent_name=self.name)).load_data()
            index = VectorStoreIndex.from_documents(documents)
            # Persist index to storage
            index.storage_context.persist(persist_dir=storage_path)

        query_engine = index.as_query_engine(
            include_text=True, response_mode="tree_summarize"
        )

        return query_engine