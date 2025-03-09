from llama_index.llms.openai import OpenAI
from ..rags.query_engine import RAGQueryEngine
from llama_index.core import StorageContext
from llama_index.core import SimpleKeywordTableIndex
from llama_index.core import get_response_synthesizer
from src.rags.neo4j_retriever import Neo4jRetriever
from llama_index.core import SimpleDirectoryReader
from llama_index.core import PromptTemplate
from typing import List, Optional, AsyncGenerator
from llama_index.core import Settings
from ..domains.chat import ChatMessage, ChatResponse, Choice, Message
import uuid
import time


qa_prompt = PromptTemplate(
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the query.\n"
    "Query: {query_str}\n"
    "Answer: "
)

class BaseRAG:
    """Base class for RAGs."""

    def __init__(self, rag_name: str):
        self.rag_name = rag_name

    def get_query_engine(self):
        """Get the query engine for the RAG."""

        llm = OpenAI(model="gpt-4o-mini")

        retriever = Neo4jRetriever()

        response_synthesizer = get_response_synthesizer(
            response_mode="compact",
            verbose=True,
        )

        query_engine = RAGQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            llm=llm,
            qa_prompt=qa_prompt,
        )
    
        return query_engine


    async def chat_completion(self, messages: List[ChatMessage], max_tokens: Optional[int] = 50, temperature: Optional[float] = 0.7) -> AsyncGenerator[ChatResponse, None]:
        query_engine = self.get_query_engine()
        run_id = str(uuid.uuid4())

        message = f"Session ID: {run_id}\n"
        for msg in messages:
            message += f"{msg.role}: {msg.content}\n"
        
        yield ChatResponse(
                id=run_id,
                object="chat.completion", 
                created=int(time.time()),
                model=self.rag_name,
                choices=[
                    Choice(
                        index=0,
                        message=Message(role="assistant", content=query_engine.custom_query(message))
                    )
                ]
            )
