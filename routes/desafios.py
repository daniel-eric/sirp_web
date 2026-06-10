from fastapi import APIRouter, Form, Cookie
from fastapi.responses import RedirectResponse
from backend.dependencies import user_repository, desafio_repository
from database.desafios import Desafio

router = APIRouter()


@router.post("/api/desafios/add")
def create_problem(
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

    user_data = user_repository.find_by_identifier(logged_user)
    username = user_data.username if user_data else logged_user
    email = user_data.email if user_data else ""

    desafio = Desafio(
        titulo=titulo,
        autor=email,
        contato=email,
        areas=areas,
        contexto=contexto,
        atores=atores,
        impacto=impacto,
        contornos=contornos,
        metricas_sucesso=metricas_sucesso,
        restricoes=restricoes
    )

    desafio_id = desafio_repository.add(desafio)

    if desafio_id:
        return RedirectResponse(url="/landing-page", status_code=303)

    return RedirectResponse(url="/problems-manager?error=add", status_code=303)


@router.post("/api/desafios/update")
async def modify_problem(
    desafio_id: int = Form(alias="problem_id"),
    attribute: str = Form(...),
    new_value: str = Form(...),
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return RedirectResponse(url="/", status_code=303)

    if desafio_repository.update(desafio_id, attribute, new_value):
        return RedirectResponse(url="/problems-manager", status_code=303)

    return RedirectResponse(url="/problems-manager?error=update", status_code=303)


@router.post("/api/desafios/delete")
async def remove_problem(
    desafio_id: int = Form(alias="problem_id"),
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return RedirectResponse(url="/", status_code=303)

    if desafio_repository.delete(desafio_id):
        return RedirectResponse(url="/problems-manager", status_code=303)

    return RedirectResponse(url="/problems-manager?error=delete", status_code=303)
