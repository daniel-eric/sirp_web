import os
from fastapi import APIRouter, UploadFile, File, Cookie
from backend.dependencies import chatbot_sessions, db_manager
from database.desafios import DesafioRepository

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

repo = DesafioRepository(db_manager)


def _comprimir_imagem(content: bytes, nome_base: str, extensao: str) -> bytes | None:
    import io
    from PIL import Image

    try:
        img = Image.open(io.BytesIO(content))
        if img.mode in ("RGBA", "LA"):
            img = img.convert("RGB")

        buf = io.BytesIO()
        img.save(buf, "WEBP", quality=65)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        print(f"Erro na compressão de imagem: {e}")
        return None


@router.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return {"error": "Não autenticado"}

    if not file.filename:
        return {"error": "Arquivo inválido"}

    extensao = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    nome_base, _ = os.path.splitext(file.filename)

    tipos_permitidos = {"jpg", "jpeg", "png", "webp"}
    if extensao not in tipos_permitidos:
        return {"error": "Formato não aceito. Use JPG, PNG ou WEBP."}

    content = await file.read()
    blob = _comprimir_imagem(content, nome_base, extensao)
    if blob is None:
        blob = content

    caminho_final = os.path.join(UPLOAD_FOLDER, f"{nome_base}.webp")
    with open(caminho_final, "wb") as f:
        f.write(blob)

    return {
        "success": True,
        "path": caminho_final.replace("\\", "/"),
        "tipo": "imagem"
    }


@router.post("/api/upload_final")
async def upload_final(
    arquivo: UploadFile = File(...),
    logged_user: str | None = Cookie(default=None, alias="logged_user")
):
    if not logged_user:
        return {"error": "Não autenticado"}

    if not arquivo.filename:
        return {"error": "Arquivo inválido"}

    extensao = arquivo.filename.rsplit(".", 1)[-1].lower() if "." in arquivo.filename else ""
    nome_base, _ = os.path.splitext(arquivo.filename)

    tipos_permitidos = {"jpg", "jpeg", "png", "webp"}
    if extensao not in tipos_permitidos:
        return {"error": "Formato não aceito. Use JPG, PNG ou WEBP."}

    content = await arquivo.read()
    blob = _comprimir_imagem(content, nome_base, extensao)
    if blob is None:
        blob = content

    caminho_final = os.path.join(UPLOAD_FOLDER, f"{nome_base}_complemento.webp")
    with open(caminho_final, "wb") as f:
        f.write(blob)

    bot = chatbot_sessions._sessoes.get(logged_user)
    if bot:
        bot.vincular_midia_final(caminho_final)

        if bot.ultimo_desafio_id:
            repo.update_midia_blob(bot.ultimo_desafio_id, blob)

    return {
        "success": True,
        "path": caminho_final.replace("\\", "/"),
        "tipo": "imagem"
    }
