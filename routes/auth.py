from fastapi import APIRouter, Response, Form, status
from fastapi.responses import RedirectResponse
from backend.dependencies import user_repository
from database.users import User

router = APIRouter()


@router.post("/login")
def process_login(
    response: Response,
    usernameInput: str = Form(...),
    passwordInput: str = Form(...)
):
    current_email = user_repository.authenticate(usernameInput, passwordInput)

    if current_email:
        response_redirect = RedirectResponse(url="/landing-page", status_code=303)
        response_redirect.set_cookie(key="logged_user", value=current_email, httponly=True)
        return response_redirect

    return RedirectResponse(url="/?error=login", status_code=303)


@router.post("/sign-up")
def process_sign_up(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    tellNum: str = Form(...)
):
    new_user = User(username=username, email=email, password=password, tellNum=tellNum)
    success = user_repository.create(new_user)

    if success:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return RedirectResponse(url="/sign-up?error=signup", status_code=status.HTTP_303_SEE_OTHER)
