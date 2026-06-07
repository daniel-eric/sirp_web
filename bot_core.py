import os
import json
import time  # Para o delay entre tentativas automáticas
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
        
        # guarda no histórico interno
        chatbot.historico.append(f"Usuário: {mensagem_usuario}")
        
        # histórico para dar memória a IA
        contexto_da_conversa = "\n".join(chatbot.historico)
        
        dados_ia = None
        tentativas = 3
        
        for i in range(tentativas):
            try:
                response = chatbot.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=contexto_da_conversa,
                    config={
                        "system_instruction": """
                        Você é o assistente analista do SIRP. O SIRP NÃO aceita chamados de manutenção física/TI (lâmpadas, PCs quebrados, buracos). Ele aceita DESAFIOS PRÁTICOS E TEÓRICOS para PROJETOS ou TEMAS DE PESQUISA.
                        
                        DIRETRIZES CRÍTICAS DE LINGUAGEM:
                        1. Seja extremamente DIRETO e OBJETIVO. 
                        2. PROIBIDO dizer saudações como "Olá", "Oi", "Puxa que chato" ou "Que legal" a cada turno. Vá direto ao ponto.
                        3. Não repita a explicação do propósito do SIRP se o usuário já estiver colaborando.
                        
                        Você DEVE responder estritamente em formato JSON com estas chaves:
                        - "contexto_valido": (boolean) True se, somando todo o histórico, você já tem as informações para a fórmula abaixo.
                        - "eh_manutencao": (boolean) True se for infraestrutura quebrada.
                        - "contexto_resumido": (string) Se válido, redija estritamente assim: '[Ambiente/Curso] enfrenta [Gargalo/Desafio] devido a [Causa Raiz/Necessidade]'. Se inválido, retorne "".
                        - "resposta_chat": (string) Sua fala para o usuário. Se faltar dados, peça apenas a peça que falta, sem rodeios ou saudações.
                        """,
                        "response_mime_type": "application/json"
                    }
                )
                dados_ia = json.loads(response.text)
                break
                
            except Exception as e:
                if i < tentativas - 1:
                    time.sleep(1.5) 
                    continue
                else:
                    print("\n[Bot]: O sistema está instável no momento. Poderia tentar enviar sua mensagem novamente?")
                    if chatbot.historico: chatbot.historico.pop() #Não duplica o histórico
                    return


        print(f"\n[Bot]: {dados_ia['resposta_chat']}")
        chatbot.historico.append(f"Bot: {dados_ia['resposta_chat']}")
        
        if dados_ia.get("eh_manutencao"):
            chatbot.tentativas_manutencao += 1
            if chatbot.tentativas_manutencao >= 2:
                print("\n[Sistema]: Atendimento encerrado por insistência em escopo incorreto.")
                chatbot.finalizado = True
            return

        if dados_ia["contexto_valido"]:
            chatbot.detalhamento_problema["Contexto"] = dados_ia["contexto_resumido"]
            chatbot.mudar_estado(EstadoInvestigacao())
            print("\n[Sistema: Avançando para o Estado de Investigação...]")


class EstadoInvestigacao(EstadoBot):
    """Classe Filha 2: Focada em investigar dinamicamente o resto das chaves vazias"""
    def processar_mensagem(self, mensagem_usuario: str, chatbot: 'ChatbotSIRP'):
        print(f"\n[Usuário disse]: {mensagem_usuario}")
        print("[Bot]: Perfeito, guardei os Atores. Indo para o resumo...")
        chatbot.detalhamento_problema["Atores"] = mensagem_usuario
        chatbot.mudar_estado(EstadoResumo())

class EstadoResumo(EstadoBot):
    """Classe Filha 3: Exibe o resultado final estruturado"""
    def processar_mensagem(self, mensagem_usuario: str, chatbot: 'ChatbotSIRP'):
        chatbot.detalhamento_problema["Restrições"] = mensagem_usuario
        print("\n--- RESUMO DO SEU DESAFIO OPERACIONAL ---")
        print(json.dumps(chatbot.detalhamento_problema, indent=4, ensure_ascii=False))
        chatbot.finalizado = True

class ChatbotSIRP:
    """Gerenciador do Contexto da Máquina de Estados"""
    def __init__(self):
        self.estado_atual = EstadoColetaInicial()
        self.finalizado = False
        self.tentativas_manutencao = 0
        self.historico = [] 
        self.detalhamento_problema = {
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