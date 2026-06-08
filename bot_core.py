import os
import json
import time 
from google import genai
from dotenv import load_dotenv

load_dotenv()

class EstadoBot: 
    """Superclasse Base para os Estados do Bot"""
    def processar_mensagem(self, mensagem_usuario: str, chatbot: 'ChatbotSIRP'):
        pass

class EstadoColetaInicial(EstadoBot):
    """Classe Filha 1: Focada em validar e entender o contexto do desafio ou pesquisa"""
    def processar_mensagem(self, mensagem_usuario: str, chatbot: 'ChatbotSIRP'):
        chatbot.historico.append(f"Usuário: {mensagem_usuario}")
        contexto_da_conversa = "\n".join(chatbot.historico)
        dados_ia = None
        tentativas = 3
        
        for i in range(tentativas):
            try:
                response = chatbot.client.models.generate_content(
                    model = 'gemini-2.5-flash',
                    contents = contexto_da_conversa,
                    config={
                        "system_instruction": """
                        Você é o assistente analista do SIRP. O SIRP NÃO aceita chamados de manutenção física/TI (lâmpadas, PCs quebrados, buracos). Ele aceita DESAFIOS PRÁTICOS E TEÓRICOS para PROJETOS ou TEMAS DE PESQUISA.
                        
                        DIRETRIZES CRÍTICAS DE LINGUAGEM:
                        1. Seja extremamente DIRETO e OBJETIVO. Sem saudações ou rodeios.
                        2. Não repita a explicação do propósito do SIRP se o usuário já estiver colaborando.
                        
                        Você DEVE responder estritamente em formato JSON com estas chaves:
                        - "contexto_valido": (boolean) True se tiver as informações para a fórmula abaixo.
                        - "eh_manutencao": (boolean) True se for infraestrutura quebrada.
                        - "contexto_resumido": (string) Se válido, redija estritamente assim: '[Ambiente/Curso] enfrenta [Gargalo/Desafio] devido a [Causa Raiz/Necessidade]'. Se inválido, retorne "".
                        - "resposta_chat": (string) Sua fala para o usuário solicitando o que falta de forma direta.
                        """,
                        "response_mime_type": "application/json"
                    }
                )
                dados_ia = json.loads(response.text)
                break
            except Exception as e:
                if i < tentativas - 1: time.sleep(1.5); continue
                else:
                    print("\n[Bot]: O sistema está instável. Poderia reenviar a mensagem?")
                    if chatbot.historico: chatbot.historico.pop()
                    return

        if dados_ia.get("eh_manutencao"):
            print(f"\n[Bot]: {dados_ia['resposta_chat']}")
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
            print(f"\n[Bot]: {dados_ia['resposta_chat']}")
            chatbot.historico.append(f"Bot: {dados_ia['resposta_chat']}")


class EstadoInvestigacao(EstadoBot):
    """Classe Filha 2: Focada em investigar dinamicamente e preencher as chaves técnicas + tags"""
    def processar_mensagem(self, mensagem_usuario: str, chatbot: 'ChatbotSIRP'):
        if mensagem_usuario.strip():
            chatbot.historico.append(f"Usuário : {mensagem_usuario}")
            
        estado_do_dicionario = f"Campos preenchidos atualmente: {chatbot.detalhamento_problema}"
        contexto_da_conversa = estado_do_dicionario + "\n\nHistórico:\n" + "\n".join(chatbot.historico)
        dados_ia = None
        tentativas = 3

        for i in range(tentativas):
            try:
                response = chatbot.client.models.generate_content(
                    model = 'gemini-2.5-flash',
                    contents = contexto_da_conversa,
                    config = {
                        "system_instruction" : """ 
                        Você é o assistente analista do SIRP. Seu papel é aprofundar, extrair dados e categorizar o problema.
                        
                        DIRETRIZES CRÍTICAS:
                        1. Seja extremamente DIRETO e OBJETIVO. Sem rodeios ou saudações.
                        2. VARRA O HISTÓRICO: Se os dados de alguma chave já foram ditos ou estão implícitos, extraia imediatamente.
                        3. CONFRONTE SE NECESSÁRIO: Se o usuário se contradisser, instigue-o a pensar criticamente.
                        
                        Você DEVE responder em formato JSON com estas chaves:
                        - "titulo_desafio": (string) Uma manchete curta (máx 6 palavras) que exponha a DOR/PROBLEMA de forma instigante. NUNCA use nomes de soluções ou aplicativos. Exemplos: 'O Drama dos Projetos Inventados', 'Apagão de Networking no BSI'.
                        - "valores_extraidos": (objeto) Mapeie aqui as chaves identificadas (opções: 'Atores', 'Impacto', 'Contornos', 'Métricas de Sucesso', 'Restrições', 'Áreas').
                        - "investigacao_completa": (boolean) True se TODOS os campos técnicos (incluindo Áreas) já estiverem maduros. False caso contrário.
                        - "resposta_chat": (string) Sua fala focando estritamente na lacuna atual.
                        
                        REGRA DE FORMATAÇÃO PARA 'Áreas':
                        Classifique o problema em até 3 categorias do ecossistema do feed, escritas em MAIÚSCULO e separadas por " | ". Opções permitidas: TECNOLOGIA DA INFORMAÇÃO, GASTRONOMIA, COMERCIAL, MARKETING, USER EXPERIENCE, AGRÍCOLA, GESTÃO.
                        Exemplo: 'TECNOLOGIA DA INFORMAÇÃO | USER EXPERIENCE'
                        
                        REMOVA TODOS OS COLCHETES [...] E PARÊNTESES DOS VALORES EXTRAÍDOS. O texto deve ser limpo e fluido.
                        """,
                        "response_mime_type" : "application/json"
                    },
                )      
                dados_ia = json.loads(response.text)
                break
            except Exception as e:
                if i < tentativas - 1: time.sleep(1.5); continue
                else: return

        valores_encontrados = dados_ia.get("valores_extraidos", {})
        for chave, valor in valores_encontrados.items():
            if valor and chave in chatbot.detalhamento_problema:
                chatbot.detalhamento_problema[chave] = valor
        
        if dados_ia.get("titulo_desafio"):
            chatbot.detalhamento_problema["Título"] = dados_ia["titulo_desafio"]

        if dados_ia.get("investigacao_completa"):  
            chatbot.mudar_estado(EstadoConfirmacao())
            chatbot.estado_atual.processar_mensagem("", chatbot)
        else:
            print(f"\n[Bot]: {dados_ia['resposta_chat']}")
            chatbot.historico.append(f"Bot: {dados_ia['resposta_chat']}")


class EstadoConfirmacao(EstadoBot):
    """Classe Filha 3: Permite o usuário revisar e corrigir informações antes de salvar"""
    def processar_mensagem(self, mensagem_usuario: str, chatbot: 'ChatbotSIRP'):
        # Se for o gatilho inicial de transição (mensagem vazia), mostra o rascunho
        if not mensagem_usuario.strip():
            print("\n--- RASCUNHO DO SEU DESAFIO OPERACIONAL ---")
            print(json.dumps(chatbot.detalhamento_problema, indent=4, ensure_ascii=False))
            print("\n[Bot]: O rascunho do seu desafio ficou pronto. Está perfeito para publicação ou deseja ajustar alguma informação?")
            return

        # Se o usuário aprovar, finaliza
        palavras_aprovacao = ["perfeito", "ok", "salvar", "aprovar", "pode salvar", "top", "sim", "massa", "fechou"]
        if any(palavra in mensagem_usuario.lower() for palabra in palavras_aprovacao):
            print("\n[Bot]: Perfeito! Desafio operacional validado com sucesso e pronto para o feed.")
            chatbot.finalizado = True
            return

        # Caso o usuário queira editar algo, a IA processa o ajuste cirúrgico
        print("\n[Sistema]: Processando alteração solicitada...")
        contexto_edicao = f"Dicionário Atual: {chatbot.detalhamento_problema}\nPedido do Usuário: {mensagem_usuario}"
        
        try:
            response = chatbot.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contexto_edicao,
                config={
                    "system_instruction": """
                    Você é o revisor do SIRP. O usuário apontou uma alteração ou correção no rascunho do problema dele.
                    Identifique qual chave do dicionário ele quer alterar ('Título', 'Áreas', 'Contexto', 'Atores', 'Impacto', 'Contornos', 'Métricas de Sucesso', 'Restrições') e reescreva o valor aplicando a correção de forma limpa e sem colchetes.
                    Retorne APENAS o objeto JSON completo com todas as chaves atualizadas.
                    """,
                    "response_mime_type": "application/json"
                }
            )
            novo_dicionario = json.loads(response.text)
            chatbot.detalhamento_problema.update(novo_dicionario)
            
            # Mostra o resultado corrigido e pede nova confirmação
            print("\n--- RASCUNHO ATUALIZADO ---")
            print(json.dumps(chatbot.detalhamento_problema, indent=4, ensure_ascii=False))
            print("\n[Bot]: Ajuste feito! Agora está correto ou quer mudar mais alguma coisa?")
            
        except Exception as e:
            print("\n[Bot]: Não consegui processar o ajuste. Pode repetir o que deseja alterar?")


class ChatbotSIRP:
    """Gerenciador do Contexto da Máquina de Estados"""
    def __init__(self):
        self.estado_atual = EstadoColetaInicial()
        self.finalizado = False
        self.tentativas_manutencao = 0
        self.historico = [] 
        self.detalhamento_problema = {
            "Título": "",
            "Autor": "",       # Será preenchido automaticamente pela sessão do Front/Banco
            "Contato": "",     # Será preenchido automaticamente pela sessão do Front/Banco
            "Áreas": "",       # Ex: 'TECNOLOGIA DA INFORMAÇÃO | MARKETING'
            "Contexto": "",
            "Atores": "",
            "Impacto": "",
            "Contornos": "",
            "Métricas de Sucesso": "",
            "Restrições": ""
        }
        self.client = genai.Client()
        
        print("\n[Bot]: Olá! O SIRP conecta gargalos práticos e ideias de pesquisa da nossa universidade a soluções criativas da comunidade acadêmica.")
        print("Qual desafio prático ou oportunidade de cooperação científica você quer registrar hoje?")
        print("*(Aviso: Problemas de manutenção física devem ser abertos diretamente com a TI da instituição).*")

    def mudar_estado(self, novo_estado: EstadoBot): 
        self.estado_atual = novo_estado

    def receber_mensagem(self, mensagem: str):
        self.estado_atual.processar_mensagem(mensagem, self)

if __name__ == "__main__":
    bot = ChatbotSIRP()
    while not bot.finalizado: 
        msg = input("\nVocê: ")
        if msg.strip():
            bot.receber_mensagem(msg)