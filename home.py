from fastapi import FastAPI, Form, status, Response, Request, Cookie
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from database.db_config import DatabaseManager
from database.users import User, UserRepository
from database.problems import Problem, ProblemRepository


class SirpApp:
    def __init__(self):
        self.app = FastAPI()
        self.app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
        self.templates = Jinja2Templates(directory="templates")
        self.db_manager = DatabaseManager()
        self.user_repository = UserRepository(self.db_manager)
        self.problem_repository = ProblemRepository(self.db_manager)
        self.register_routes()

    def register_routes(self):
        self.app.get("/")(self.root)
        self.app.get("/sign-up")(self.sign_up)
        self.app.get("/landing-page")(self.landing_page)
        self.app.get("/profile")(self.profile)
        self.app.get("/problems-feed")(self.display_problems_feed)
        self.app.get("/problems-manager")(self.problems_manager)

        self.app.post("/login")(self.process_login)
        self.app.post("/sign-up")(self.process_sign_up)
        self.app.post("/api/profile/update-username")(self.change_user_username)
        self.app.post("/api/profile/update-password")(self.change_user_password)
        self.app.post("/api/profile/update-tellNum")(self.change_user_tellNum)
        self.app.post("/api/profile/delete-account")(self.remove_account)
        self.app.post("/api/problems/add")(self.create_problem)
        self.app.post("/api/problems/update")(self.modify_problem)
        self.app.post("/api/problems/delete")(self.remove_problem)

    async def root(self):
        return FileResponse("templates/index.html")

    async def sign_up(self):
        return FileResponse("templates/sign_up.html")

    async def landing_page(self):
        return FileResponse("templates/landing_page.html")

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
            name="profile.html",
            context={"user": user_data.to_dict()}
        )

    def display_problems_feed(
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

        problems_list = self.problem_repository.search(
            title=title,
            areas=areas,
            author=author,
            time=time
        )

        return self.templates.TemplateResponse(
            request=request,
            name="problems_feed.html",
            context={"problems": problems_list}
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
            name="problems_manager.html",
            context={}
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
        title: str = Form(...),
        description: str = Form(...),
        areas: str = Form(...),
        logged_user: str | None = Cookie(default=None, alias="logged_user")
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        problem = Problem(
            title=title,
            description=description,
            author=logged_user,
            areas=areas,
            time=current_time
        )

        problem_id = self.problem_repository.add(problem)

        if problem_id:
            return RedirectResponse(url="/problems-feed", status_code=303)

        return RedirectResponse(url="/problems-manager?error=add", status_code=303)

    async def modify_problem(
        self,
        problem_id: int = Form(...),
        attribute: str = Form(...),
        new_value: str = Form(...),
        logged_user: str | None = Cookie(default=None, alias="logged_user")
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        if self.problem_repository.update(problem_id, attribute, new_value):
            return RedirectResponse(url="/problems-manager", status_code=303)

        return RedirectResponse(url="/problems-manager?error=update", status_code=303)

    async def remove_problem(
        self,
        problem_id: int = Form(...),
        logged_user: str | None = Cookie(default=None, alias="logged_user")
    ):
        if not logged_user:
            return RedirectResponse(url="/", status_code=303)

        if self.problem_repository.delete(problem_id):
            return RedirectResponse(url="/problems-manager", status_code=303)

        return RedirectResponse(url="/problems-manager?error=delete", status_code=303)


sirp_app = SirpApp()
app = sirp_app.app
