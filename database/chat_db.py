import sqlite3
from dataclasses import dataclass
from typing import Optional
from database.db_config import DatabaseManager


@dataclass
class Conversa:
    id: Optional[int]
    nome: str
    tipo: str
    data_criacao: Optional[str] = None


@dataclass
class Participante:
    id: Optional[int]
    conversa_id: int
    user_email: str


@dataclass
class Mensagem:
    id: Optional[int]
    conversa_id: int
    autor_email: str
    conteudo: str
    data_envio: Optional[str] = None


class ChatRepository:
    def __init__(self, db_manager: DatabaseManager, crypto):
        self.db_manager = db_manager
        self.crypto = crypto

    def criar_ou_obter_dm(self, email1: str, email2: str, nome_dm: str) -> Optional[int]:
        try:
            with self.db_manager.connect(row_factory=sqlite3.Row) as db:
                db.execute("""
                    SELECT c.id FROM conversas c
                    WHERE c.tipo = 'dm'
                    AND EXISTS (SELECT 1 FROM participantes p1
                                WHERE p1.conversa_id = c.id AND p1.user_email = ?)
                    AND EXISTS (SELECT 1 FROM participantes p2
                                WHERE p2.conversa_id = c.id AND p2.user_email = ?)
                """, (email1, email2))
                row = db.fetchone()
                if row:
                    return row["id"]
        except sqlite3.Error as e:
            print(f"SQLite error in criar_ou_obter_dm (select): {e}")
            return None

        try:
            with self.db_manager.connect() as db:
                db.execute(
                    "INSERT INTO conversas (nome, tipo) VALUES (?, 'dm')",
                    (nome_dm,)
                )
                conversa_id = db.cursor.lastrowid
                for email in (email1, email2):
                    db.execute(
                        "INSERT INTO participantes (conversa_id, user_email) VALUES (?, ?)",
                        (conversa_id, email)
                    )
                return conversa_id
        except sqlite3.Error as e:
            print(f"SQLite error in criar_ou_obter_dm (insert): {e}")
            return None

    def criar_conversa(self, nome: str, participantes: list[str]) -> Optional[int]:
        try:
            with self.db_manager.connect() as db:
                db.execute(
                    "INSERT INTO conversas (nome, tipo) VALUES (?, 'group')",
                    (nome,)
                )
                conversa_id = db.cursor.lastrowid
                for email in participantes:
                    db.execute(
                        "INSERT INTO participantes (conversa_id, user_email) VALUES (?, ?)",
                        (conversa_id, email)
                    )
                return conversa_id
        except sqlite3.Error as e:
            print(f"SQLite error in criar_conversa: {e}")
            return None

    def get_conversas(self, user_email: str) -> list[dict]:
        try:
            with self.db_manager.connect(row_factory=sqlite3.Row) as db:
                db.execute("""
                    SELECT c.id, c.nome, c.tipo, c.data_criacao,
                           (SELECT COUNT(*) FROM mensagens m WHERE m.conversa_id = c.id) AS total_mensagens
                    FROM conversas c
                    JOIN participantes p ON p.conversa_id = c.id
                    WHERE p.user_email = ?
                    ORDER BY c.data_criacao DESC
                """, (user_email,))
                return [dict(row) for row in db.fetchall()]
        except sqlite3.Error as e:
            print(f"SQLite error in get_conversas: {e}")
            return []

    def get_mensagens(self, conversa_id: int, ultimo_id: int = 0) -> list[dict]:
        try:
            with self.db_manager.connect(row_factory=sqlite3.Row) as db:
                db.execute("""
                    SELECT id, conversa_id, autor_email, conteudo, data_envio
                    FROM mensagens
                    WHERE conversa_id = ? AND id > ?
                    ORDER BY data_envio ASC
                """, (conversa_id, ultimo_id))
                mensagens = []
                for row in db.fetchall():
                    msg = dict(row)
                    msg["conteudo"] = self.crypto.decrypt(msg["conteudo"])
                    mensagens.append(msg)
                return mensagens
        except sqlite3.Error as e:
            print(f"SQLite error in get_mensagens: {e}")
            return []

    def enviar_mensagem(self, conversa_id: int, autor_email: str, conteudo: str) -> Optional[int]:
        try:
            if self.esta_bloqueado(conversa_id):
                print(f"Conversa {conversa_id} bloqueada, mensagem rejeitada")
                return None
            conteudo_criptografado = self.crypto.encrypt(conteudo)
            with self.db_manager.connect() as db:
                db.execute(
                    "INSERT INTO mensagens (conversa_id, autor_email, conteudo) VALUES (?, ?, ?)",
                    (conversa_id, autor_email, conteudo_criptografado)
                )
                return db.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"SQLite error in enviar_mensagem: {e}")
            return None

    def get_participantes(self, conversa_id: int) -> list[dict]:
        try:
            with self.db_manager.connect(row_factory=sqlite3.Row) as db:
                db.execute("""
                    SELECT p.user_email, u.username
                    FROM participantes p
                    JOIN users u ON u.email = p.user_email
                    WHERE p.conversa_id = ?
                """, (conversa_id,))
                return [dict(row) for row in db.fetchall()]
        except sqlite3.Error as e:
            print(f"SQLite error in get_participantes: {e}")
            return []

    def adicionar_participante(self, conversa_id: int, user_email: str) -> bool:
        try:
            with self.db_manager.connect() as db:
                db.execute(
                    "INSERT OR IGNORE INTO participantes (conversa_id, user_email) VALUES (?, ?)",
                    (conversa_id, user_email)
                )
                return db.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"SQLite error in adicionar_participante: {e}")
            return False

    def bloquear_conversa(self, conversa_id: int, user_email: str) -> bool:
        try:
            with self.db_manager.connect() as db:
                db.execute(
                    "UPDATE conversas SET bloqueado_por = ? WHERE id = ? AND bloqueado_por IS NULL",
                    (user_email, conversa_id)
                )
                return db.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"SQLite error in bloquear_conversa: {e}")
            return False

    def desbloquear_conversa(self, conversa_id: int, user_email: str) -> bool:
        try:
            with self.db_manager.connect() as db:
                db.execute(
                    "UPDATE conversas SET bloqueado_por = NULL WHERE id = ? AND bloqueado_por = ?",
                    (conversa_id, user_email)
                )
                return db.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"SQLite error in desbloquear_conversa: {e}")
            return False

    def esta_bloqueado(self, conversa_id: int) -> str | None:
        try:
            with self.db_manager.connect() as db:
                db.execute(
                    "SELECT bloqueado_por FROM conversas WHERE id = ?",
                    (conversa_id,)
                )
                row = db.fetchone()
                return row[0] if row else None
        except sqlite3.Error as e:
            print(f"SQLite error in esta_bloqueado: {e}")
            return None
