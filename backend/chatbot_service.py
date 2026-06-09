from bot_core import ChatbotSIRP


class ChatbotSessionManager:
    def __init__(self):
        self._sessoes: dict[str, ChatbotSIRP] = {}

    def get_or_create(self, user_email: str) -> ChatbotSIRP:
        sessao = self._sessoes.get(user_email)
        if not sessao or sessao.finalizado:
            sessao = ChatbotSIRP()
            self._sessoes[user_email] = sessao
        return sessao

    def remover(self, user_email: str):
        self._sessoes.pop(user_email, None)

    def get_ultima_resposta(self, user_email: str) -> str:
        sessao = self._sessoes.get(user_email)
        if not sessao:
            return ""
        return sessao.ultima_resposta
