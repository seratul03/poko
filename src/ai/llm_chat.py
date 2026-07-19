import os
from groq import Groq
from dotenv import load_dotenv
import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class LLMChat:
    def __init__(self, memory_system):
        self.memory_system = memory_system
        self.is_ready = False
        self.client = None
        self.model_name = "llama-3.1-8b-instant"
        self.chat_history = []
        
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        env_model = os.getenv("GROQ_MODEL_NAME")
        if env_model:
            self.model_name = env_model
            
        if api_key:
            try:
                self.client = Groq(api_key=api_key)
                self.is_ready = True
                logger.info("Groq AI configured successfully.")
            except Exception as e:
                logger.error(f"Failed to configure Groq: {e}")
        else:
            logger.warning("GROQ_API_KEY not found in .env file. AI chat disabled.")
            
    def start_chat_session(self):
        if not self.is_ready:
            return
            
        self.chat_history = [
            {"role": "system", "content": config.AI_SYSTEM_PROMPT}
        ]
        
        # Load previous history
        saved_history = self.memory_system.get_chat_history()
        for msg in saved_history:
            self.chat_history.append({"role": "user", "content": msg["user"]})
            self.chat_history.append({"role": "assistant", "content": msg["ai"]})
            
    def send_message(self, text: str) -> str:
        if not self.is_ready:
            return "I can't talk right now. Missing API key."
            
        if not self.chat_history:
            self.start_chat_session()
            
        self.chat_history.append({"role": "user", "content": text})
            
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.chat_history,
                temperature=0.7,
                max_tokens=150,
            )
            reply = response.choices[0].message.content.strip()
            self.chat_history.append({"role": "assistant", "content": reply})
            
            # Save to memory
            self.memory_system.add_chat_history(text, reply)
            self.memory_system.increment_conversations()
            return reply
        except Exception as e:
            logger.error(f"Failed to send message to Groq: {e}")
            # Remove the failed user message from history
            self.chat_history.pop()
            return "*Hiss* (Network error)"
