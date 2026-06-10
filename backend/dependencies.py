from fastapi.templating import Jinja2Templates
from database.db_config import DatabaseManager
from database.users import UserRepository
from database.desafios import DesafioRepository
from backend.chatbot_service import ChatbotSessionManager

templates = Jinja2Templates(directory="frontend")
db_manager = DatabaseManager()
user_repository = UserRepository(db_manager)
desafio_repository = DesafioRepository(db_manager)
chatbot_sessions = ChatbotSessionManager()
