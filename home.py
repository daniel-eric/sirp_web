from fastapi import FastAPI, Form, status, Response, Request, Cookie
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from database.db_config import DatabaseManager
from database.users import User, UserRepository
from database.desafios import Desafio, salvar_desafio_no_banco, DesafioRepository
from backend.chatbot_service import ChatbotSessionManager

load_dotenv()


class SirpApp:
    def __init__(self):
        self.app = FastAPI()
        self.app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
        self.app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")
        self.templates = Jinja2Templates(directory="frontend")
        self.db_manager = DatabaseManager()
        self.user_repository = UserRepository(self.db_manager)
        self.desafio_repository = DesafioRepository(self.db_manager)
        self.chatbot_sessions = ChatbotSessionManager()
        self.register_routes()

    def register_routes(self):
        self.app.get("/")(self.root)
        self.app.get("/sign-up")(self.sign_up)
        self.app.get("/landing-page")(self.landing_page)
        self.app.get("/profile")(self.profile)
        self.app.get("/problems-manager")(self.problems_manager)

        self.app.post("/login")(self.process_login)
        self.app.post("/sign-up")(self.process_sign_up)
        self.app.post("/api/profile/update-username")(self.change_user_username)
        self.app.post("/api/profile/update-password")(self.change_user_password)
        self.app.post("/api/profile/update-tellNum")(self.change_user_tellNum)
        self.app.post("/api/profile/delete-account")(self.remove_account)
        self.app.post("/api/desafios/add")(self.create_problem)
        self.app.post("/api/desafios/update")(self.modify_problem)
        self.app.post("/api/desafios/delete")(self.remove_problem)
        self.app.post("/api/chat")(self.api_chat_message)
        self.app.get("/api/chat/state")(self.api_chat_state)
        self.app.post("/api/chat/cancel")(self.api_chat_cancel)

    async def root(self, request: Request):
        return self.templates.TemplateResponse(request=request, name="login.html")

    async def sign_up(self, request: Request):
        return self.templates.TemplateResponse(request=request, name="cadastro.html")

    async def landing_page(
        self,
        request: Request,
        title: str | None = None,
        areas: str | None = None,
        author: str | None = None,
        time: str | None = None,
        logged_user: str | None = Cookie(default=None, alias="logged_user")
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        problems_list = self.desafio_repository.search(
            titulo=title,
            areas=areas,
            autor=author,
            data_criacao=time
        )

        return self.templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "problems": problems_list,
                "logged_user": logged_user,
                "title_filter": title or "",
                "areas_filter": areas or "",
                "author_filter": author or "",
                "time_filter": time or ""
            }
        )

    async def profile(
        self,
        request: Request,
        logged_user: str | None = Cookie(None)
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        user_data = self.user_repository.find_by_identifier(logged_user)
        if not user_data:
            return RedirectResponse(url="/", status_code=303)

        return self.templates.TemplateResponse(
            request=request,
            name="perfil.html",
            context={"request": request, "user": user_data.to_dict(), "logged_user": logged_user}
        )

    async def problems_manager(
        self,
        request: Request,
        logged_user: str | None = Cookie(default=None, alias="logged_user")
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        return self.templates.TemplateResponse(
            request=request,
            name="reportar.html",
            context={"request": request, "logged_user": logged_user}
        )

    def process_login(
        self,
        response: Response,
        usernameInput: str = Form(...),
        passwordInput: str = Form(...)
    ):
        current_email = self.user_repository.authenticate(usernameInput, passwordInput)

        if current_email:
            response_redirect = RedirectResponse(url="/landing-page", status_code=303)
            response_redirect.set_cookie(key="logged_user", value=current_email, httponly=True)
            return response_redirect

        return RedirectResponse(url="/?error=login", status_code=303)

    def process_sign_up(
        self,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        tellNum: str = Form(...)
    ):
        new_user = User(username=username, email=email, password=password, tellNum=tellNum)
        success = self.user_repository.create(new_user)

        if success:
            return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

        return RedirectResponse(url="/sign-up?error=signup", status_code=status.HTTP_303_SEE_OTHER)

    def change_user_username(
        self,
        username: str = Form(...),
        logged_user: str | None = Cookie(None)
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        if self.user_repository.update_username(logged_user, username):
            return RedirectResponse(url="/profile", status_code=303)
        return RedirectResponse(url="/profile?erro=username", status_code=303)

    def change_user_password(
        self,
        password: str = Form(...),
        logged_user: str | None = Cookie(None)
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        if self.user_repository.update_password(logged_user, password):
            return RedirectResponse(url="/profile", status_code=303)
        return RedirectResponse(url="/profile?erro=password", status_code=303)

    def change_user_tellNum(
        self,
        tellNum: str = Form(...),
        logged_user: str | None = Cookie(None)
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        if self.user_repository.update_tellNum(logged_user, tellNum):
            return RedirectResponse(url="/profile", status_code=303)
        return RedirectResponse(url="/profile?erro=phone", status_code=303)

    def remove_account(
        self,
        response: Response,
        logged_user: str | None = Cookie(default=None, alias="logged_user")
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        if self.user_repository.delete(logged_user):
            response_redirect = RedirectResponse(url="/", status_code=303)
            response_redirect.delete_cookie(key="logged_user")
            return response_redirect

        return RedirectResponse(url="/profile?error=delete", status_code=303)

    def create_problem(
        self,
        titulo: str = Form(...),
        areas: str = Form(...),
        contexto: str = Form(default=""),
        atores: str = Form(default=""),
        impacto: str = Form(default=""),
        contornos: str = Form(default=""),
        metricas_sucesso: str = Form(default=""),
        restricoes: str = Form(default=""),
        logged_user: str | None = Cookie(default=None, alias="logged_user")
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        user_data = self.user_repository.find_by_identifier(logged_user)
        username = user_data.username if user_data else logged_user
        email = user_data.email if user_data else ""

        desafio = Desafio(
            titulo=titulo,
            autor=username,
            contato=email,
            areas=areas,
            contexto=contexto,
            atores=atores,
            impacto=impacto,
            contornos=contornos,
            metricas_sucesso=metricas_sucesso,
            restricoes=restricoes
        )

        desafio_id = self.desafio_repository.add(desafio)

        if desafio_id:
            return RedirectResponse(url="/landing-page", status_code=303)

        return RedirectResponse(url="/problems-manager?error=add", status_code=303)

    async def modify_problem(
        self,
        desafio_id: int = Form(alias="problem_id"),
        attribute: str = Form(...),
        new_value: str = Form(...),
        logged_user: str | None = Cookie(default=None, alias="logged_user")
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        if self.desafio_repository.update(desafio_id, attribute, new_value):
            return RedirectResponse(url="/problems-manager", status_code=303)

        return RedirectResponse(url="/problems-manager?error=update", status_code=303)

    async def remove_problem(
        self,
        desafio_id: int = Form(alias="problem_id"),
        logged_user: str | None = Cookie(default=None, alias="logged_user")
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        if self.desafio_repository.delete(desafio_id):
            return RedirectResponse(url="/problems-manager", status_code=303)

        return RedirectResponse(url="/problems-manager?error=delete", status_code=303)


    async def api_chat_message(
        self,
        request: Request,
        logged_user: str | None = Cookie(default=None, alias="logged_user")
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        body = await request.json()
        mensagem = body.get("mensagem", "")

        bot = self.chatbot_sessions.get_or_create(logged_user)

        user_data = self.user_repository.find_by_identifier(logged_user)
        if user_data:
            bot.detalhamento_problema["Autor"] = user_data.username
            bot.detalhamento_problema["Contato"] = user_data.email

        bot.receber_mensagem(mensagem)

        if bot.finalizado and user_data and bot.detalhamento_problema.get("Título"):
            salvar_desafio_no_banco(
                bot.detalhamento_problema,
                user_data.username,
                user_data.email,
                self.db_manager
            )
            self.chatbot_sessions.remover(logged_user)
        elif bot.finalizado:
            self.chatbot_sessions.remover(logged_user)

        return {
            "resposta": bot.ultima_resposta,
            "finalizado": bot.finalizado,
            "rascunho_pronto": bot.rascunho_pronto,
            "rascunho": bot.detalhamento_problema if (bot.finalizado or bot.rascunho_pronto) else None
        }

    async def api_chat_state(
        self,
        logged_user: str | None = Cookie(default=None, alias="logged_user")
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        bot = self.chatbot_sessions._sessoes.get(logged_user)
        if not bot:
            return {"ativo": False}

        return {
            "ativo": not bot.finalizado,
            "finalizado": bot.finalizado,
            "rascunho_pronto": bot.rascunho_pronto
        }

    async def api_chat_cancel(
        self,
        logged_user: str | None = Cookie(default=None, alias="logged_user")
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        self.chatbot_sessions.remover(logged_user)
        return {"cancelado": True}


sirp_app = SirpApp()
app = sirp_app.app
