import sqlite3
from typing import Optional, Any

DB_NAME = 'sirp.db'


class DatabaseConnection:
    def __init__(self, db_name: str = DB_NAME, row_factory: Any | None = None):
        self.db_name = db_name
        self.row_factory = row_factory
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        if self.row_factory:
            self.conn.row_factory = self.row_factory
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            self.conn.close()

    def execute(self, query: str, params: tuple | list = ()):
        if self.cursor is None:
            raise RuntimeError("O cursor não foi inicializado. Use o gerenciador de contexto 'with'.")
        
        self.cursor.execute(query, params)
        return self.cursor

    def fetchone(self):
        if self.cursor is None:
            return None
            
        return self.cursor.fetchone()

    def fetchall(self):
        if self.cursor is None:
            return []
            
        return self.cursor.fetchall()



class DatabaseManager:
    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name

    def connect(self, row_factory: Optional[Any] = None):
        return DatabaseConnection(self.db_name, row_factory=row_factory)


def db_user_init():
    try:
        with DatabaseConnection() as db:
            db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    tellNum TEXT
                )
            ''')
    except sqlite3.OperationalError as e:
        print(f"🛑 Erro ao tentar criar a tabela 'users': {e}")
    except Exception as e:
        print(f"💥 Erro imprevisto na inicialização da tabela 'users': {e}")


def db_desafios_init():
    try:
        with DatabaseConnection() as db:
            db.execute('''
                CREATE TABLE IF NOT EXISTS desafios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    autor TEXT NOT NULL,
                    contato TEXT,
                    areas TEXT NOT NULL,
                    contexto TEXT,
                    atores TEXT,
                    impacto TEXT,
                    contornos TEXT,
                    metricas_sucesso TEXT,
                    restricoes TEXT,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    midia_blob BLOB
                )
            ''')
    except sqlite3.OperationalError as e:
        print(f"Erro ao criar tabela 'desafios': {e}")
    except Exception as e:
        print(f"Erro inesperado na tabela 'desafios': {e}")


db_user_init()
db_desafios_init()
