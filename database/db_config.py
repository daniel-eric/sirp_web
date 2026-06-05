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


def db_problems_init():
    try:
        with DatabaseConnection() as db:
            db.execute('''
                CREATE TABLE IF NOT EXISTS problems (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    areas TEXT NOT NULL,
                    authors TEXT NOT NULL,
                    time TEXT NOT NULL
                )
            ''')
    except sqlite3.OperationalError as e:
        print(f"🛑 Erro ao tentar criar a tabela 'problems': {e}")
    except Exception as e:
        print(f"💥 Erro imprevisto na inicialização da tabela 'problems': {e}")


db_user_init()
db_problems_init()
