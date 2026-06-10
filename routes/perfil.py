from fastapi import APIRouter, Form, Cookie, Response
from fastapi.responses import RedirectResponse
from backend.dependencies import user_repository

router = APIRouter()


@router.post("/api/profile/update-username")
def change_user_username(
    username: str = Form(...),
    logged_user: str | None = Cookie(None)
):
    if not logged_user:
        return RedirectResponse(url="/", status_code=303)

    if user_repository.update_username(logged_user, username):
        return RedirectResponse(url="/profile", status_code=303)
    return RedirectResponse(url="/profile?erro=username", status_code=303)


@router.post("/api/profile/update-password")
def change_user_password(
    password: str = Form(...),
    logged_user: str | None = Cookie(None)
):
    if not logged_user:
        return RedirectResponse(url="/", status_code=303)

    if user_repository.update_password(logged_user, password):
        return RedirectResponse(url="/profile", status_code=303)
    return RedirectResponse(url="/profile?erro=password", status_code=303)


@router.post("/api/profile/update-tellNum")
def change_user_tellNum(
    tellNum: str = Form(...),
    logged_user: str | None = Cookie(None)
):
    if not logged_user:
        return RedirectResponse(url="/", status_code=303)

    if user_repository.update_tellNum(logged_user, tellNum):
        return RedirectResponse(url="/profile", status_code=303)
    return RedirectResponse(url="/profile?erro=phone", status_code=303)


@router.post("/api/profile/delete-account")
def remove_account(
    response: Response,
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return RedirectResponse(url="/", status_code=303)

    if user_repository.delete(logged_user):
        response_redirect = RedirectResponse(url="/", status_code=303)
        response_redirect.delete_cookie(key="logged_user")
        return response_redirect

    return RedirectResponse(url="/profile?error=delete", status_code=303)
