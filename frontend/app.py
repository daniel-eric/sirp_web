from flask import Flask, request, jsonify, send_from_directory
import os
import subprocess
from PIL import Image
from bot_core import ChatbotSIRP

# Verifica se o plugin do AVIF está disponível no ambiente local do Python
try:
    import pillow_avif
    SUPORTE_AVIF = True
except ImportError:
    SUPORTE_AVIF = False

app = Flask(__name__, static_folder='.', static_url_path='')

# Instancia o cérebro da inteligência artificial
chatbot = ChatbotSIRP()

# Configura o diretório padrão para armazenamento seguro
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/reportar.html')
def reportar():
    return send_from_directory('.', 'reportar.html')

@app.route('/uploads/<filename>')
def serve_uploads(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# =========================================================================
# ROTA UNIFICADA DO CHAT (ENTREGA A TABELA + TEXTO)
# =========================================================================
@app.route('/api/chat', methods=['POST'])
def chat():
    dados = request.json or {}
    mensagem = dados.get('mensagem', '')
    
    if not mensagem:
        return jsonify({'error': 'Mensagem vazia.'}), 400
    
    # Processa a mensagem na máquina de estados do bot_core
    chatbot.receber_mensagem(mensagem)
    
    # Coleta os dados gerados do core do sistema
    resposta_texto = chatbot.ultima_resposta_bot
    abstracao_atual = chatbot.obter_rascunho_abstracao()  # Seu detalhamento_problema original
    fluxo_concluido = chatbot.verificar_conclusao()       # Mapeia se a IA finalizou o processo
    
    # Retorno híbrido: Garante o funcionamento de chaves antigas e novas no Front-End!
    return jsonify({
        'success': True,
        'resposta_bot': resposta_texto,
        'mensagem': resposta_texto,
        'dossie_parcial': abstracao_atual,
        'abstracao': abstracao_atual,
        'finalizado': fluxo_concluido,
        'concluido': fluxo_concluido
    })


# =========================================================================
# ROTA UNIFICADA DE RESET (BOTÃO REFRESH / NOVO RELATO)
# =========================================================================
@app.route('/api/reset', methods=['POST'])
def reset_chat():
    global chatbot
    chatbot = ChatbotSIRP()  # Recria a IA do zero, limpando estados e memórias
    
    return jsonify({
        'success': True,
        'status': 'sucesso', 
        'mensagem_inicial': chatbot.ultima_resposta_bot,
        'message': 'Histórico redefinido com sucesso.'
    })


# =========================================================================
# ROTAS DE UPLOAD E COMPRESSÃO EXTREMA (MÍDIAS)
# =========================================================================

@app.route('/api/upload', methods=['POST'])
def upload():
    """Mantida para compatibilidade caso o sistema chame uploads isolados"""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
    
    arquivo = request.files['file']
    if arquivo.filename == '':
        return jsonify({'error': 'Arquivo inválido.'}), 400

    extensao = arquivo.filename.split('.')[-1].lower()
    nome_base, _ = os.path.splitext(arquivo.filename)
    
    caminho_original = os.path.join(UPLOAD_FOLDER, arquivo.filename)
    arquivo.save(caminho_original)

    tipo_detectado = ""
    caminho_final = ""

    try:
        # 📸 COMPRESSÃO E TRATAMENTO DE IMAGENS
        if extensao in ['jpg', 'jpeg', 'png', 'webp', 'heic']:
            tipo_detectado = 'imagem'
            img = Image.open(caminho_original)
            
            if img.mode in ('RGBA', 'LA') and not SUPORTE_AVIF:
                img = img.convert('RGB')

            if SUPORTE_AVIF:
                caminho_final = os.path.join(UPLOAD_FOLDER, f"{nome_base}.avif")
                img.save(caminho_final, 'AVIF', quality=50)
            else:
                caminho_final = os.path.join(UPLOAD_FOLDER, f"{nome_base}.webp")
                img.save(caminho_final, 'WEBP', quality=65)
            
            if caminho_original != caminho_final:
                os.remove(caminho_original)

        # 🎥 CONVERSÃO EXTREMA DE VÍDEOS VIA FFMPEG (VP9/WebM)
        elif extensao in ['mp4', 'mkv', 'avi', 'mov', '3gp']:
            tipo_detectado = 'video'
            caminho_final = os.path.join(UPLOAD_FOLDER, f"{nome_base}.webm")
            
            comando = [
                'ffmpeg', '-y', '-i', caminho_original,
                '-c:v', 'libvpx-vp9', '-crf', '38', '-b:v', '0',
                '-c:a', 'libopus', caminho_final
            ]
            
            try:
                subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                os.remove(caminho_original)
            except Exception:
                caminho_final = caminho_original
        else:
            return jsonify({'error': 'Formato não aceito pelo SIRP.'}), 400

        return jsonify({
            'success': True, 
            'path': caminho_final.replace('\\', '/'), 
            'tipo': tipo_detectado
        })

    except Exception as e:
        return jsonify({'error': f'Falha no processamento: {str(e)}'}), 500


@app.route('/api/upload_final', methods=['POST'])
def upload_final():
    """Rota do Modal Final - Processa e vincula o anexo único diretamente à abstração"""
    if 'arquivo' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
        
    arquivo = request.files['arquivo']
    if arquivo.filename == '':
        return jsonify({'error': 'Arquivo inválido.'}), 400
    
    extensao = arquivo.filename.split('.')[-1].lower()
    nome_base, _ = os.path.splitext(arquivo.filename)
    
    caminho_original = os.path.join(UPLOAD_FOLDER, arquivo.filename)
    arquivo.save(caminho_original)
    
    tipo_detectado = ""
    caminho_final = ""
    
    try:
        # Aplica a mesma compressão extrema inteligente do SIRP na mídia final
        if extensao in ['jpg', 'jpeg', 'png', 'webp', 'heic']:
            tipo_detectado = 'imagem'
            img = Image.open(caminho_original)
            if img.mode in ('RGBA', 'LA') and not SUPORTE_AVIF:
                img = img.convert('RGB')
                
            if SUPORTE_AVIF:
                caminho_final = os.path.join(UPLOAD_FOLDER, f"{nome_base}_complemento.avif")
                img.save(caminho_final, 'AVIF', quality=50)
            else:
                caminho_final = os.path.join(UPLOAD_FOLDER, f"{nome_base}_complemento.webp")
                img.save(caminho_final, 'WEBP', quality=65)
                
            if caminho_original != caminho_final:
                os.remove(caminho_original)
                
        elif extensao in ['mp4', 'mkv', 'avi', 'mov', '3gp']:
            tipo_detectado = 'video'
            caminho_final = os.path.join(UPLOAD_FOLDER, f"{nome_base}_complemento.webm")
            
            comando = [
                'ffmpeg', '-y', '-i', caminho_original,
                '-c:v', 'libvpx-vp9', '-crf', '38', '-b:v', '0',
                '-c:a', 'libopus', caminho_final
            ]
            try:
                subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                os.remove(caminho_original)
            except Exception:
                caminho_final = caminho_original
        else:
            return jsonify({'error': 'Formato não aceito.'}), 400
            
        # Alimenta o bot_core com o path definitivo para o Daniel converter em Blob
        chatbot.vincular_midia_final(caminho_final)
        
        return jsonify({
            'success': True, 
            'path': caminho_final.replace('\\', '/'),
            'tipo': tipo_detectado
        })
        
    except Exception as e:
        return jsonify({'error': f'Falha no processamento final: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)