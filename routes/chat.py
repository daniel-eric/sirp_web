from fastapi import APIRouter, Request, Cookie
from fastapi.responses import RedirectResponse
from backend.dependencies import chatbot_sessions, user_repository, db_manager
from database.desafios import salvar_desafio_no_banco

router = APIRouter()


@router.post("/api/chat")
async def api_chat_message(
    request: Request,
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return RedirectResponse(url="/", status_code=303)

    body = await request.json()
    mensagem = body.get("mensagem", "")

    bot = chatbot_sessions.get_or_create(logged_user)

    user_data = user_repository.find_by_identifier(logged_user)
    if user_data:
        bot.detalhamento_problema["Autor"] = user_data.email
        bot.detalhamento_problema["Contato"] = user_data.email

    bot.receber_mensagem(mensagem)

    if bot.finalizado and user_data and bot.detalhamento_problema.get("Título"):
        salvar_desafio_no_banco(
            bot.detalhamento_problema,
            user_data.username,
            user_data.email,
            db_manager
        )
        chatbot_sessions.remover(logged_user)
    elif bot.finalizado:
        chatbot_sessions.remover(logged_user)

    return {
        "resposta": bot.ultima_resposta,
        "finalizado": bot.finalizado,
        "rascunho_pronto": bot.rascunho_pronto,
        "rascunho": bot.detalhamento_problema if (bot.finalizado or bot.rascunho_pronto) else None
    }


@router.get("/api/chat/state")
async def api_chat_state(
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return RedirectResponse(url="/", status_code=303)

    bot = chatbot_sessions._sessoes.get(logged_user)
    if not bot:
        return {"ativo": False}

    return {
        "ativo": not bot.finalizado,
        "finalizado": bot.finalizado,
        "rascunho_pronto": bot.rascunho_pronto
    }


@router.post("/api/chat/cancel")
async def api_chat_cancel(
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return RedirectResponse(url="/", status_code=303)

    chatbot_sessions.remover(logged_user)
    return {"cancelado": True}
