from fastapi import APIRouter, Request, Cookie, Query, Path
from fastapi.responses import RedirectResponse, JSONResponse
from backend.dependencies import templates, chat_repository, user_repository

router = APIRouter()


@router.get("/chat")
async def chat_page(
    request: Request,
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return RedirectResponse(url="/", status_code=303)

    user_data = user_repository.find_by_identifier(logged_user)
    if not user_data:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "request": request,
            "logged_user": logged_user,
            "user": user_data.to_dict()
        }
    )


@router.get("/api/conversas")
async def listar_conversas(
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return JSONResponse({"conversas": []}, status_code=401)

    conversas = chat_repository.get_conversas(logged_user)

    for c in conversas:
        participantes = chat_repository.get_participantes(c["id"])
        c["participantes"] = participantes
        c["qtd_participantes"] = len(participantes)

    return JSONResponse({"conversas": conversas})


@router.post("/api/conversas/criar")
async def criar_conversa(
    request: Request,
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return JSONResponse({"erro": "Não autenticado"}, status_code=401)

    body = await request.json()
    nome = body.get("nome", "").strip()
    participantes = body.get("participantes", [])

    if not nome:
        return JSONResponse({"erro": "Nome da conversa é obrigatório"}, status_code=400)

    if logged_user not in participantes:
        participantes.insert(0, logged_user)

    if len(participantes) < 2:
        return JSONResponse({"erro": "É necessário pelo menos 2 participantes"}, status_code=400)

    conversa_id = chat_repository.criar_conversa(nome, participantes)
    if conversa_id is None:
        return JSONResponse({"erro": "Erro ao criar conversa"}, status_code=500)

    return JSONResponse({"id": conversa_id, "nome": nome})


@router.post("/api/conversas/dm")
async def criar_dm(
    request: Request,
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return JSONResponse({"erro": "Não autenticado"}, status_code=401)

    body = await request.json()
    email_outro = body.get("email", "").strip().lower()

    if not email_outro:
        return JSONResponse({"erro": "Email é obrigatório"}, status_code=400)

    if email_outro == logged_user:
        return JSONResponse({"erro": "Não pode conversar consigo mesmo"}, status_code=400)

    outro_user = user_repository.find_by_identifier(email_outro)
    if not outro_user:
        return JSONResponse({"erro": "Usuário não encontrado"}, status_code=404)

    nome_dm = outro_user.username
    conversa_id = chat_repository.criar_ou_obter_dm(logged_user, outro_user.email, nome_dm)
    if conversa_id is None:
        return JSONResponse({"erro": "Erro ao criar conversa"}, status_code=500)

    return JSONResponse({"id": conversa_id, "nome": nome_dm, "tipo": "dm"})


@router.get("/api/conversas/{conversa_id}/mensagens")
async def listar_mensagens(
    conversa_id: int = Path(...),
    ultimo_id: int = Query(0),
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return JSONResponse({"mensagens": []}, status_code=401)

    mensagens = chat_repository.get_mensagens(conversa_id, ultimo_id)
    return JSONResponse({"mensagens": mensagens})


@router.post("/api/conversas/{conversa_id}/mensagens")
async def enviar_mensagem(
    conversa_id: int = Path(...),
    request: Request = None,
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return JSONResponse({"erro": "Não autenticado"}, status_code=401)

    body = await request.json()
    conteudo = body.get("conteudo", "").strip()

    if not conteudo:
        return JSONResponse({"erro": "Mensagem vazia"}, status_code=400)

    msg_id = chat_repository.enviar_mensagem(conversa_id, logged_user, conteudo)
    if msg_id is None:
        return JSONResponse({"erro": "Erro ao enviar mensagem"}, status_code=500)

    return JSONResponse({"id": msg_id, "conteudo": conteudo, "autor_email": logged_user})


@router.post("/api/conversas/{conversa_id}/convidar")
async def convidar_participante(
    conversa_id: int = Path(...),
    request: Request = None,
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return JSONResponse({"erro": "Não autenticado"}, status_code=401)

    body = await request.json()
    email = body.get("email", "").strip()

    if not email:
        return JSONResponse({"erro": "Email é obrigatório"}, status_code=400)

    user = user_repository.find_by_identifier(email)
    if not user:
        return JSONResponse({"erro": "Usuário não encontrado"}, status_code=404)

    ok = chat_repository.adicionar_participante(conversa_id, user.email)
    if not ok:
        return JSONResponse({"erro": "Usuário já é participante"}, status_code=409)

    return JSONResponse({"sucesso": True, "email": user.email})


@router.get("/api/conversas/{conversa_id}/bloqueio")
async def status_bloqueio(
    conversa_id: int = Path(...),
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return JSONResponse({"erro": "Não autenticado"}, status_code=401)

    bloqueado = chat_repository.esta_bloqueado(conversa_id, logged_user)
    return JSONResponse({"bloqueado": bloqueado})


@router.post("/api/conversas/{conversa_id}/bloquear")
async def bloquear_conversa(
    conversa_id: int = Path(...),
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return JSONResponse({"erro": "Não autenticado"}, status_code=401)

    ok = chat_repository.bloquear_conversa(conversa_id, logged_user)
    if not ok:
        return JSONResponse({"erro": "Erro ao bloquear"}, status_code=409)

    return JSONResponse({"sucesso": True})


@router.post("/api/conversas/{conversa_id}/desbloquear")
async def desbloquear_conversa(
    conversa_id: int = Path(...),
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return JSONResponse({"erro": "Não autenticado"}, status_code=401)

    ok = chat_repository.desbloquear_conversa(conversa_id, logged_user)
    if not ok:
        return JSONResponse({"erro": "Erro ao desbloquear"}, status_code=409)

    return JSONResponse({"sucesso": True})
