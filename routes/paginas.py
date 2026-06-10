from fastapi import APIRouter, Request, Cookie
from fastapi.responses import RedirectResponse
from backend.dependencies import templates, desafio_repository, user_repository

router = APIRouter()


@router.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.get("/sign-up")
async def sign_up(request: Request):
    return templates.TemplateResponse(request=request, name="cadastro.html")


@router.get("/landing-page")
async def landing_page(
    request: Request,
    title: str | None = None,
    areas: str | None = None,
    author: str | None = None,
    time: str | None = None,
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return RedirectResponse(url="/", status_code=303)

    problems_list = desafio_repository.search(
        titulo=title,
        areas=areas,
        autor=author,
        data_criacao=time
    )

    return templates.TemplateResponse(
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


@router.get("/profile")
async def profile(
    request: Request,
    logged_user: str | None = Cookie(None)
):
    if not logged_user:
        return RedirectResponse(url="/", status_code=303)

    user_data = user_repository.find_by_identifier(logged_user)
    if not user_data:
        return RedirectResponse(url="/", status_code=303)

    user_desafios = desafio_repository.get_by_autor(logged_user)

    return templates.TemplateResponse(
        request=request,
        name="perfil.html",
        context={
            "request": request,
            "user": user_data.to_dict(),
            "logged_user": logged_user,
            "desafios": user_desafios
        }
    )


@router.get("/problems-manager")
async def problems_manager(
    request: Request,
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="reportar.html",
        context={"request": request, "logged_user": logged_user}
    )
