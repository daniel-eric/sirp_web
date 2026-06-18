from fastapi.templating import Jinja2Templates
from database.db_config import DatabaseManager
from database.users import UserRepository
from database.desafios import DesafioRepository
from database.chat_db import ChatRepository
from backend.chatbot_service import ChatbotSessionManager
from backend.crypto_utils import CryptoUtils

templates = Jinja2Templates(directory="frontend")
db_manager = DatabaseManager()
user_repository = UserRepository(db_manager)
desafio_repository = DesafioRepository(db_manager)
crypto = CryptoUtils()
chat_repository = ChatRepository(db_manager, crypto)
chatbot_sessions = ChatbotSessionManager()
