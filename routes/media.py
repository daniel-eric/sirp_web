import os
import uuid
import subprocess
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, Cookie
from backend.dependencies import chatbot_sessions, db_manager
from database.desafios import DesafioRepository

router = APIRouter()

UPLOAD_FOLDER = "uploads"
VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, "videos")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

repo = DesafioRepository(db_manager)

TIPOS_IMAGEM = {"jpg", "jpeg", "png", "webp"}
TIPOS_VIDEO = {"mp4", "mov", "avi", "mkv", "3gp", "webm"}


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


def _comprimir_video(caminho_origem: str, caminho_destino: str) -> bool:
    if not shutil.which("ffmpeg"):
        print("ffmpeg não encontrado no sistema")
        return False

    comando = [
        "ffmpeg", "-y",
        "-i", caminho_origem,
        "-t", "30",
        "-c:v", "libx264", "-crf", "28",
        "-vf", "scale='min(854,iw)':min'(480,ih)':force_original_aspect_ratio=decrease",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        f"{caminho_destino}.mp4"
    ]

    try:
        subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ffmpeg: {e}")
        return False


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

    eh_imagem = extensao in TIPOS_IMAGEM
    eh_video = extensao in TIPOS_VIDEO

    if not eh_imagem and not eh_video:
        return {"error": "Formato não aceito. Use JPG, PNG, WEBP para imagem ou MP4, MOV, AVI, MKV, 3GP, WEBM para vídeo."}

    if eh_imagem:
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

    if eh_video:
        sufixo = uuid.uuid4().hex[:8]
        temp_fd, temp_path = tempfile.mkstemp(suffix=f".{extensao}")
        os.close(temp_fd)

        try:
            conteudo = await arquivo.read()
            with open(temp_path, "wb") as f:
                f.write(conteudo)

            desafio_id = None
            bot = chatbot_sessions._sessoes.get(logged_user)
            if bot:
                desafio_id = bot.ultimo_desafio_id

            if desafio_id is None:
                desafio_id = "temp"

            nome_video = f"{desafio_id}_{sufixo}"
            destino = os.path.join(VIDEO_FOLDER, nome_video)

            convertido = _comprimir_video(temp_path, destino)

            if convertido:
                caminho_final = f"{destino}.mp4"
            else:
                caminho_final = os.path.join(VIDEO_FOLDER, f"{nome_video}.{extensao}")
                shutil.copy2(temp_path, caminho_final)

            if bot and desafio_id != "temp":
                repo.update_video_path(desafio_id, caminho_final)

            return {
                "success": True,
                "path": caminho_final.replace("\\", "/"),
                "tipo": "video"
            }

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
