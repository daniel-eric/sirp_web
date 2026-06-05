class EstadoBot: 
    """Esta é a Classe Base (Superclasse)
    Ela dita a regra: 'Todo estado do bot precisa ter um jeito de processar mensagem"""

    def processar_mensagem(self, mensagem_usuario: str, chatbot: 'ChatbotSIRP'):
        pass

class EstadoColetaInicial(EstadoBot):
    """Classe FIlha 1: Focada apenas em entender o problema inicial"""
    def processar_mensagem(self, mensagem_usuario: str, chatbot:'ChatbotSIRP'):
        print(f"\n[Usuário disse]: {mensagem_usuario}")
        print("[Bot]: Entendi o contexto!Mas quem mais sofre com isso no dia a dia?")
        chatbot.detalhamento_problema["Contexto"] = mensagem_usuario
        

        chatbot.mudar_estado(EstadoInvestigacao())
    
class EstadoInvestigacao(EstadoBot):
    """Classe Filha 1: Focada em cavar as regras e impactos."""
    def processar_mensagem(self, mensagem_usuario: str, chatbot: 'ChatbotSIRP'):
        print(f"\n[Usuário disse]: {mensagem_usuario}")
        print("[Bot]: Faz muito sentido. Existe alguma regra na universidade que impeça a solução disso?")
        chatbot.detalhamento_problema["Atores"] = mensagem_usuario

        chatbot.mudar_estado(EstadoResumo())

class EstadoResumo(EstadoBot):
    """Classe Filha 3: Gera o JSON final e encerra"""
    def processar_mensagem(self, mensagem_usuario: str, chatbot:'ChatbotSIRP'):
        print(f"\n[Usuário disse]: {mensagem_usuario}")
        print("[Bot]: Perfeito! Estruturei o problema aqui. Confirma se está certo para mandarmos para o feed!")
        chatbot.detalhamento_problema["Restrições"] = mensagem_usuario
        print(chatbot.detalhamento_problema)

        chatbot.finalizado = True

class ChatbotSIRP:
    """Gerenciador (Contexto).
    Ele é a casca do bot. O usuário só conversa com ele, e ele
    repassa a mensagem para o estado que estiver ativo no momento"""

    def __init__(self):
        self.estado_atual = EstadoColetaInicial()
        self.finalizado = False
        self.detalhamento_problema = {
        "Contexto": "",
        "Atores" : "",
        "Impacto": "",
        "Contornos": "",
        "Métricas de Sucesso": "",
        "Restrições": ""
        }
        print("[Bot]: Oi! Que legal que você identificou um desafio por aqui. Me conta de forma simples: o que está te incomodando na universidade?")

    def mudar_estado(self, novo_estado: EstadoBot): 
        self.estado_atual = novo_estado

    def receber_mensagem(self, mensagem: str):
        self.estado_atual.processar_mensagem(mensagem, self)

if __name__ == "__main__":
    bot= ChatbotSIRP()
    while not bot.finalizado: 
        msg = input("\nVocê: ")
        bot.receber_mensagem(msg)