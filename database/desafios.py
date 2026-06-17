import sqlite3
from dataclasses import dataclass
from typing import Optional
from database.db_config import DatabaseManager


@dataclass
class Desafio:
    titulo: str
    autor: str
    contato: str
    areas: str
    contexto: str = ""
    atores: str = ""
    impacto: str = ""
    contornos: str = ""
    metricas_sucesso: str = ""
    restricoes: str = ""
    midia_blob: Optional[bytes] = None
    video_path: Optional[str] = None
    id: Optional[int] = None
    data_criacao: Optional[str] = None

    def to_dict(self) -> dict:
        d = {
            "id": self.id,
            "titulo": self.titulo,
            "autor": self.autor,
            "contato": self.contato,
            "areas": self.areas,
            "contexto": self.contexto,
            "atores": self.atores,
            "impacto": self.impacto,
            "contornos": self.contornos,
            "metricas_sucesso": self.metricas_sucesso,
            "restricoes": self.restricoes,
            "data_criacao": self.data_criacao
        }
        if self.midia_blob is not None:
            d["tem_midia"] = True
        if self.video_path:
            d["tem_video"] = True
        return d


class DesafioRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def add(self, desafio: Desafio) -> Optional[int]:
        try:
            with self.db_manager.connect() as db:
                sql = '''
                    INSERT INTO desafios
                        (titulo, autor, contato, areas, contexto, atores,
                         impacto, contornos, metricas_sucesso, restricoes,
                         midia_blob, video_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                cursor = db.execute(sql, (
                    desafio.titulo, desafio.autor, desafio.contato,
                    desafio.areas, desafio.contexto, desafio.atores,
                    desafio.impacto, desafio.contornos,
                    desafio.metricas_sucesso, desafio.restricoes,
                    desafio.midia_blob, desafio.video_path
                ))
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"SQLite error in add_desafio: {e}")
            return None
        except Exception as e:
            print(f"General exception in add_desafio: {e}")
            return None

    def get(self, desafio_id: int) -> Optional[Desafio]:
        try:
            with self.db_manager.connect(row_factory=sqlite3.Row) as db:
                db.execute("SELECT * FROM desafios WHERE id = ?", (desafio_id,))
                row = db.fetchone()
                if row:
                    return Desafio(
                        id=row["id"],
                        titulo=row["titulo"],
                        autor=row["autor"],
                        contato=row["contato"],
                        areas=row["areas"],
                        contexto=row["contexto"],
                        atores=row["atores"],
                        impacto=row["impacto"],
                        contornos=row["contornos"],
                        metricas_sucesso=row["metricas_sucesso"],
                        restricoes=row["restricoes"],
                        data_criacao=row["data_criacao"],
                        video_path=row.get("video_path")
                    )
            return None
        except sqlite3.Error as e:
            print(f"SQLite error in get_desafio: {e}")
            return None
        except Exception as e:
            print(f"General exception in get_desafio: {e}")
            return None

    def search(
        self,
        titulo: str | None = None,
        areas: str | None = None,
        autor: str | None = None,
        data_criacao: str | None = None
    ) -> list[dict]:
        try:
            with self.db_manager.connect(row_factory=sqlite3.Row) as db:
                cols = "id, titulo, autor, contato, areas, contexto, atores, impacto, contornos, metricas_sucesso, restricoes, data_criacao, video_path"
                sql = f"SELECT {cols}, CASE WHEN midia_blob IS NOT NULL THEN 1 ELSE 0 END AS tem_midia, CASE WHEN video_path IS NOT NULL THEN 1 ELSE 0 END AS tem_video FROM desafios WHERE 1=1"
                parameters: list[str] = []

                if titulo and titulo.strip():
                    sql += " AND LOWER(titulo) LIKE LOWER(?)"
                    parameters.append(f"%{titulo.strip()}%")

                if areas and areas.strip():
                    sql += " AND LOWER(areas) LIKE LOWER(?)"
                    parameters.append(f"%{areas.strip()}%")

                if autor and autor.strip():
                    sql += " AND LOWER(autor) LIKE LOWER(?)"
                    parameters.append(f"%{autor.strip()}%")

                if data_criacao and data_criacao.strip():
                    sql += " AND data_criacao LIKE ?"
                    parameters.append(f"%{data_criacao.strip()}%")

                sql += " ORDER BY data_criacao DESC"

                db.execute(sql, parameters)
                return [dict(row) for row in db.fetchall()]
        except sqlite3.Error as e:
            print(f"SQLite error in search_desafios: {e}")
            return []
        except Exception as e:
            print(f"General exception in search_desafios: {e}")
            return []

    def update(self, desafio_id: int, attribute: str, new_value: str) -> bool:
        allowed_columns = {'titulo', 'autor', 'contato', 'areas', 'contexto',
                           'atores', 'impacto', 'contornos', 'metricas_sucesso', 'restricoes'}
        if attribute not in allowed_columns:
            return False
        try:
            with self.db_manager.connect() as db:
                sql = f"UPDATE desafios SET {attribute} = ? WHERE id = ?"
                cursor = db.execute(sql, (new_value, desafio_id))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"SQLite error in update_desafio: {e}")
            return False
        except Exception as e:
            print(f"General exception in update_desafio: {e}")
            return False

    def update_midia_blob(self, desafio_id: int, blob: bytes) -> bool:
        try:
            with self.db_manager.connect() as db:
                cursor = db.execute(
                    "UPDATE desafios SET midia_blob = ? WHERE id = ?",
                    (blob, desafio_id)
                )
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"SQLite error in update_midia_blob: {e}")
            return False
        except Exception as e:
            print(f"General exception in update_midia_blob: {e}")
            return False

    def update_video_path(self, desafio_id: int, video_path: str) -> bool:
        try:
            with self.db_manager.connect() as db:
                cursor = db.execute(
                    "UPDATE desafios SET video_path = ? WHERE id = ?",
                    (video_path, desafio_id)
                )
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"SQLite error in update_video_path: {e}")
            return False
        except Exception as e:
            print(f"General exception in update_video_path: {e}")
            return False

    def get_video_path(self, desafio_id: int) -> Optional[str]:
        try:
            with self.db_manager.connect() as db:
                db.execute("SELECT video_path FROM desafios WHERE id = ?", (desafio_id,))
                row = db.fetchone()
                return row[0] if row else None
        except sqlite3.Error as e:
            print(f"SQLite error in get_video_path: {e}")
            return None
        except Exception as e:
            print(f"General exception in get_video_path: {e}")
            return None

    def get_midia_blob(self, desafio_id: int) -> Optional[bytes]:
        try:
            with self.db_manager.connect() as db:
                db.execute("SELECT midia_blob FROM desafios WHERE id = ?", (desafio_id,))
                row = db.fetchone()
                return row[0] if row else None
        except sqlite3.Error as e:
            print(f"SQLite error in get_midia_blob: {e}")
            return None
        except Exception as e:
            print(f"General exception in get_midia_blob: {e}")
            return None

    def delete(self, desafio_id: int) -> bool:
        try:
            with self.db_manager.connect() as db:
                cursor = db.execute("DELETE FROM desafios WHERE id = ?", (desafio_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"SQLite error in delete_desafio: {e}")
            return False
        except Exception as e:
            print(f"General exception in delete_desafio: {e}")
            return False

    def get_by_autor(self, autor: str) -> list[dict]:
        try:
            with self.db_manager.connect(row_factory=sqlite3.Row) as db:
                cols = "id, titulo, autor, contato, areas, contexto, atores, impacto, contornos, metricas_sucesso, restricoes, data_criacao, video_path"
                db.execute(
                    f"SELECT {cols}, CASE WHEN midia_blob IS NOT NULL THEN 1 ELSE 0 END AS tem_midia, CASE WHEN video_path IS NOT NULL THEN 1 ELSE 0 END AS tem_video FROM desafios WHERE autor = ? ORDER BY data_criacao DESC",
                    (autor,)
                )
                return [dict(row) for row in db.fetchall()]
        except sqlite3.Error as e:
            print(f"SQLite error in get_by_autor: {e}")
            return []
        except Exception as e:
            print(f"General exception in get_by_autor: {e}")
            return []


def salvar_desafio_no_banco(
    detalhamento: dict,
    username: str,
    email: str,
    db_manager: DatabaseManager,
    midia_blob: bytes | None = None,
    video_path: str | None = None
) -> Optional[int]:
    detalhamento["Autor"] = email
    detalhamento["Contato"] = email

    desafio = Desafio(
        titulo=detalhamento.get("Título", ""),
        autor=detalhamento.get("Autor", ""),
        contato=detalhamento.get("Contato", ""),
        areas=detalhamento.get("Áreas", ""),
        contexto=detalhamento.get("Contexto", ""),
        atores=detalhamento.get("Atores", ""),
        impacto=detalhamento.get("Impacto", ""),
        contornos=detalhamento.get("Contornos", ""),
        metricas_sucesso=detalhamento.get("Métricas de Sucesso", ""),
        restricoes=detalhamento.get("Restrições", ""),
        midia_blob=midia_blob,
        video_path=video_path
    )

    repo = DesafioRepository(db_manager)
    return repo.add(desafio)


