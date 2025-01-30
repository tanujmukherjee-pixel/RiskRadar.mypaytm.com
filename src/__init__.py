"""
DevRev Agent Package
"""
from .chat_interface import ChatInterface

__version__ = "0.1.0"

def create_app():
    """For backwards compatibility with ASGI servers"""
    from fastapi import FastAPI
    app = FastAPI()
    return app

def main():
    """Entry point for command-line interface"""
    chat = ChatInterface()
    chat.start()

# This is for ASGI compatibility
app = create_app()

if __name__ == "__main__":
    main()
