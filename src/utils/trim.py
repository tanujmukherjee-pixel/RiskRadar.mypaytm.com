from llama_index.llms.ollama import Ollama

def trim_context(context, max_tokens=1000):
    """Trim context using local Ollama model"""
    llm = Ollama(
        model="deepseek-r1:8b",
        temperature=0.5,
        base_url="http://localhost:11434"
    )

    response = llm.complete(
        prompt=f"""You are a data expert. You need to trim this context to the most relevant information:
        
        {context}
        
        Provide only the most relevant information.""",
        max_tokens=max_tokens
    )
    return response.text