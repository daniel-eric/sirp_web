import json
import re
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

MODELO = 'gemini-3.5-flash'


def _extrair_retry_delay(e: Exception) -> float | None:
    try:
        raw = str(e)
        m = re.search(r'retryDelay["\']:\s*["\'](\d+(?:\.\d+)?)s', raw)
        if m:
            return float(m.group(1))
    except Exception:
        pass
    return None


class EstadoBot:
    def processar_mensagem(self, mensagem_usuario: str, chatbot: 'ChatbotSIRP'):
        pass


class EstadoColetaInicial(EstadoBot):
    def processar_mensagem(self, mensagem_usuario: str, chatbot: 'ChatbotSIRP'):
        chatbot.historico.append(f"Usuário: {mensagem_usuario}")
        contexto_da_conversa = "\n".join(chatbot.historico)
        dados_ia = None

        system_instruction = """
        Você é o assistente analista do SIRP. O SIRP NÃO aceita chamados de manutenção física/TI (lâmpadas, PCs quebrados, buracos). Ele aceita DESAFIOS PRÁTICOS E TEÓRICOS para PROJETOS ou TEMAS DE PESQUISA.

        DIRETRIZES CRÍTICAS DE LINGUAGEM:
        1. Seja extremamente DIRETO e OBJETIVO. Sem saudações ou rodeios.
        2. Não repita a explicação do propósito do SIRP se o usuário já estiver colaborando.

        Você DEVE responder estritamente em formato JSON com estas chaves:
        - "contexto_valido": (boolean) True se tiver as informações para a fórmula abaixo.
        - "eh_manutencao": (boolean) True se for infraestrutura quebrada.
        - "contexto_resumido": (string) Se válido, redija estritamente assim: '[Ambiente/Curso] enfrenta [Gargalo/Desafio] devido a [Causa Raiz/Necessidade]'. Se inválido, retorne "".
        - "resposta_chat": (string) Sua fala para o usuário solicitando o que falta de forma direta.
        """

        dados_ia = chatbot.chamar_gemini(contexto_da_conversa, system_instruction)
        if dados_ia is None:
            chatbot.ultima_resposta = "O serviço de IA está temporariamente indisponível (limite de uso atingido). Tente novamente mais tarde."
            if chatbot.historico:
                chatbot.historico.pop()
            return

        if dados_ia.get("eh_manutencao"):
            chatbot.ultima_resposta = dados_ia['resposta_chat']
            chatbot.historico.append(f"Bot: {dados_ia['resposta_chat']}")
            chatbot.tentativas_manutencao += 1
            if chatbot.tentativas_manutencao >= 2:
                chatbot.finalizado = True
            return

        if dados_ia["contexto_valido"]:
            chatbot.detalhamento_problema["Contexto"] = dados_ia["contexto_resumido"]
            chatbot.mudar_estado(EstadoInvestigacao())
            chatbot.estado_atual.processar_mensagem("", chatbot)
        else:
            chatbot.ultima_resposta = dados_ia['resposta_chat']
            chatbot.historico.append(f"Bot: {dados_ia['resposta_chat']}")


class EstadoInvestigacao(EstadoBot):
    def processar_mensagem(self, mensagem_usuario: str, chatbot: 'ChatbotSIRP'):
        if mensagem_usuario.strip():
            chatbot.historico.append(f"Usuário: {mensagem_usuario}")

        estado_do_dicionario = f"Campos preenchidos atualmente: {chatbot.detalhamento_problema}"
        contexto_da_conversa = estado_do_dicionario + "\n\nHistórico:\n" + "\n".join(chatbot.historico)
        dados_ia = None

        system_instruction = """
        Você é o assistente analista do SIRP. Seu papel é aprofundar, extrair dados e categorizar o problema.

        DIRETRIZES CRÍTICAS:
        1. Seja extremamente DIRETO e OBJETIVO. Sem rodeios ou saudações.
        2. VARRA O HISTÓRICO: Se os dados de alguma chave já foram ditos ou estão implícitos, extraia imediatamente.
        3. CONFRONTE SE NECESSÁRIO: Se o usuário se contradisser, instigue-o a pensar criticamente.

        Você DEVE responder em formato JSON com estas chaves:
        - "titulo_desafio": (string) Uma manchete curta (máx 6 palavras) que exponha a DOR/PROBLEMA de forma instigante. NUNCA use nomes de soluções ou aplicativos.
        - "valores_extraidos": (objeto) Mapeie aqui as chaves identificadas (opções: 'Atores', 'Impacto', 'Contornos', 'Métricas de Sucesso', 'Restrições', 'Áreas').
        - "investigacao_completa": (boolean) True se TODOS os campos técnicos (incluindo Áreas) já estiverem maduros. False caso contrário.
        - "resposta_chat": (string) Sua fala focando estritamente na lacuna atual.

        REGRA DE FORMATAÇÃO PARA 'Áreas':
        Classifique o problema em até 3 categorias, escritas em MAIÚSCULO e separadas por " | ". Opções: TECNOLOGIA DA INFORMAÇÃO, GASTRONOMIA, COMERCIAL, MARKETING, USER EXPERIENCE, AGRÍCOLA, GESTÃO.

        REMOVA TODOS OS COLCHETES [...] E PARÊNTESES DOS VALORES EXTRAÍDOS.
        """

        dados_ia = chatbot.chamar_gemini(contexto_da_conversa, system_instruction)
        if dados_ia is None:
            chatbot.ultima_resposta = "Não foi possível processar sua resposta agora (limite de uso). Vamos continuar daqui mais tarde?"
            return

        CHAVES_PERMITIDAS = {'Atores', 'Impacto', 'Contornos', 'Métricas de Sucesso', 'Restrições', 'Áreas'}
        valores_encontrados = dados_ia.get("valores_extraidos", {})
        for chave, valor in valores_encontrados.items():
            if valor and chave in CHAVES_PERMITIDAS and chave in chatbot.detalhamento_problema:
                chatbot.detalhamento_problema[chave] = valor

        if dados_ia.get("titulo_desafio"):
            chatbot.detalhamento_problema["Título"] = dados_ia["titulo_desafio"]

        if dados_ia.get("investigacao_completa"):
            chatbot.mudar_estado(EstadoConfirmacao())
            chatbot.estado_atual.processar_mensagem("", chatbot)
        else:
            chatbot.ultima_resposta = dados_ia['resposta_chat']
            chatbot.historico.append(f"Bot: {dados_ia['resposta_chat']}")


class EstadoConfirmacao(EstadoBot):
    def processar_mensagem(self, mensagem_usuario: str, chatbot: 'ChatbotSIRP'):
        if not mensagem_usuario.strip():
            rascunho = json.dumps(chatbot.detalhamento_problema, indent=4, ensure_ascii=False)
            chatbot.ultima_resposta = f"--- RASCUNHO DO SEU DESAFIO ---\n{rascunho}\n\nO rascunho ficou pronto. Está perfeito ou deseja ajustar algo?"
            chatbot.rascunho_pronto = True
            return

        palavras_aprovacao = ["perfeito", "ok", "salvar", "aprovar", "pode salvar", "top", "sim", "massa", "fechou"]
        if any(palavra in mensagem_usuario.lower() for palavra in palavras_aprovacao):
            chatbot.ultima_resposta = "Perfeito! Desafio validado e pronto para o feed."
            chatbot.finalizado = True
            return

        chatbot.ultima_resposta = "Processando alteração..."
        contexto_edicao = f"Dicionário Atual: {chatbot.detalhamento_problema}\nPedido do Usuário: {mensagem_usuario}"

        system_instruction = """
        Você é o revisor do SIRP. O usuário apontou uma alteração no rascunho.
        Identifique qual chave ele quer alterar ('Título', 'Áreas', 'Contexto', 'Atores', 'Impacto', 'Contornos', 'Métricas de Sucesso', 'Restrições') e reescreva o valor aplicando a correção.
        Retorne APENAS o objeto JSON completo com todas as chaves atualizadas.
        """

        dados = chatbot.chamar_gemini(contexto_edicao, system_instruction)
        if dados is None:
            chatbot.ultima_resposta = "Não consegui processar o ajuste agora (limite de uso). Pode repetir mais tarde?"
            return

        chatbot.detalhamento_problema.update(dados)
        rascunho = json.dumps(chatbot.detalhamento_problema, indent=4, ensure_ascii=False)
        chatbot.ultima_resposta = f"--- RASCUNHO ATUALIZADO ---\n{rascunho}\n\nAjuste feito! Agora está correto ou quer mudar mais algo?"


class ChatbotSIRP:
    def __init__(self):
        self.estado_atual = EstadoColetaInicial()
        self.finalizado = False
        self.tentativas_manutencao = 0
        self.historico = []
        self.ultima_resposta = ""
        self.rascunho_pronto = False
        self.detalhamento_problema = {
            "Título": "",
            "Autor": "",
            "Contato": "",
            "Áreas": "",
            "Contexto": "",
            "Atores": "",
            "Impacto": "",
            "Contornos": "",
            "Métricas de Sucesso": "",
            "Restrições": ""
        }
        self.client = genai.Client()

        self.ultima_resposta = (
            "Olá! O SIRP conecta gargalos práticos e ideias de pesquisa da universidade "
            "a soluções criativas da comunidade acadêmica.\n"
            "Qual desafio prático ou oportunidade de pesquisa você quer registrar hoje?\n"
            "(Aviso: Problemas de manutenção física devem ser abertos com a TI da instituição.)"
        )

    def chamar_gemini(self, prompt: str, system_instruction: str, tentativas: int = 3) -> dict | None:
        for i in range(tentativas):
            try:
                response = self.client.models.generate_content(
                    model=MODELO,
                    contents=prompt,
                    config={
                        "system_instruction": system_instruction,
                        "response_mime_type": "application/json"
                    }
                )
                return json.loads(response.text)
            except Exception as e:
                delay = _extrair_retry_delay(e)
                if delay is not None:
                    espera = min(delay + 2, 60)
                else:
                    espera = 3 * (i + 1)

                print(f"[DEBUG] chamar_gemini tentativa {i+1}/{tentativas}: {type(e).__name__}: {e} (esperando {espera:.0f}s)")
                if i < tentativas - 1:
                    time.sleep(espera)
                    continue
        return None

    def mudar_estado(self, novo_estado: EstadoBot):
        self.estado_atual = novo_estado

    def receber_mensagem(self, mensagem: str):
        self.ultima_resposta = ""
        self.estado_atual.processar_mensagem(mensagem, self)

    def reiniciar(self):
        self.__init__()
