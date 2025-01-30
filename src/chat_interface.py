import cmd
from typing import List
from .domains.chat import ChatMessage
from .services.model import ModelService
import os

class ChatInterface(cmd.Cmd):
    intro = """
    🤖 DevRev Copilot Chat Interface
    Type 'help' for a list of commands
    Type 'exit' to quit
    """
    prompt = '🤖 > '

    def __init__(self):
        super().__init__()
        self.model_service = ModelService()
        self.conversation_history: List[ChatMessage] = []
        self.current_model = "dev-rev"

    def do_chat(self, message):
        """Send a message to the AI assistant"""
        if not message:
            print("Please provide a message!")
            return

        try:
            # Add user message to history
            self.conversation_history.append(
                ChatMessage(role="user", content=message)
            )

            print("\n🤔 Thinking...\n")  # Add loading indicator

            # Get response from model
            response = self.model_service.chat_completion(
                self.current_model,
                self.conversation_history
            )

            # Extract and print assistant's response
            if isinstance(response, str):
                assistant_message = response
            else:
                # Handle structured response
                assistant_message = response.choices[0]["message"]["content"] if isinstance(response.choices[0], dict) else str(response)

            print("\n" + str(assistant_message) + "\n")

            # Add assistant response to history
            self.conversation_history.append(
                ChatMessage(role="assistant", content=str(assistant_message))
            )

        except TimeoutError:
            print("\n❌ Error: Request timed out. This could be because:")
            print("1. The model is still loading")
            print("2. The request is too complex")
            print("3. System resources are constrained")
            print("\nTry:")
            print("1. Waiting a few moments and trying again")
            print("2. Breaking your request into smaller parts")
            print("3. Checking 'ollama logs' for any issues\n")

        except ConnectionError:
            print("\n❌ Error: Could not connect to Ollama.")
            print("Make sure Ollama is running with:")
            print("1. 'ollama serve'")
            print("2. Check if the model is pulled: 'ollama pull deepseek-r1:8b'\n")

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("If this persists, try:")
            print("1. Checking Ollama status: 'ollama list'")
            print("2. Restarting Ollama: 'ollama serve'")
            print("3. Pulling the model again: 'ollama pull deepseek-r1:8b'\n")

    def do_clear(self, arg):
        """Clear the conversation history"""
        self.conversation_history = []
        print("\nConversation history cleared.\n")

    def do_history(self, arg):
        """Show conversation history"""
        if not self.conversation_history:
            print("\nNo conversation history.\n")
            return

        print("\nConversation History:")
        for msg in self.conversation_history:
            prefix = "🤖" if msg.role == "assistant" else "👤"
            print(f"\n{prefix} {msg.role.title()}: {msg.content}")
        print("\n")

    def do_models(self, arg):
        """List available models"""
        try:
            models = self.model_service.list_models()
            print("\nAvailable Models:")
            for model in models.data:
                current = "✓" if model.id == self.current_model else " "
                print(f"[{current}] {model.id}")
            print("\n")
        except Exception as e:
            print(f"\nError listing models: {str(e)}\n")

    def do_use(self, model_id):
        """Switch to a different model (use <model_id>)"""
        if not model_id:
            print("\nPlease specify a model ID\n")
            return

        try:
            # Check if model exists
            self.model_service.get_model_info(model_id)
            self.current_model = model_id
            print(f"\nSwitched to model: {model_id}\n")
        except ValueError as e:
            print(f"\nError: {str(e)}\n")

    def do_exit(self, arg):
        """Exit the chat interface"""
        print("\nGoodbye! 👋\n")
        return True

    def default(self, line):
        """Treat any input without a command as a chat message"""
        self.do_chat(line)

    def emptyline(self):
        """Do nothing on empty line"""
        pass

    def start(self):
        """Start the chat interface"""
        # Clear screen for better UX
        os.system('cls' if os.name == 'nt' else 'clear')
        self.cmdloop() 