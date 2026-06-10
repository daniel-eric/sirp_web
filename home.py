from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from routes.paginas import router as paginas_router
from routes.auth import router as auth_router
from routes.perfil import router as perfil_router
from routes.desafios import router as desafios_router
from routes.chat import router as chat_router

load_dotenv()

app = FastAPI()

app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")
app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")

app.include_router(paginas_router)
app.include_router(auth_router)
app.include_router(perfil_router)
app.include_router(desafios_router)
app.include_router(chat_router)
