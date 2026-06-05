import sqlite3
from dataclasses import dataclass
from typing import Optional
from database.db_config import DatabaseManager


@dataclass
class Problem:
    title: str
    description: str
    author: str
    areas: str
    time: str
    id: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "authors": self.author,
            "areas": self.areas,
            "time": self.time
        }


class ProblemRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def add(self, problem: Problem) -> Optional[int]:
        try:
            with self.db_manager.connect() as db:
                sql = '''INSERT INTO problems (title, description, areas, authors, time)
                         VALUES (?, ?, ?, ?, ?)'''
                cursor = db.execute(sql, (problem.title, problem.description, problem.areas, problem.author, problem.time))
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"SQLite error in add_problem: {e}")
            return None
        except Exception as e:
            print(f"General exception in add_problem: {e}")
            return None


    def get(self, problem_id: int) -> Optional[Problem]:
        try:
            with self.db_manager.connect(row_factory=sqlite3.Row) as db:
                db.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
                row = db.fetchone()

                if row:
                    return Problem(
                        id=row["id"],
                        title=row["title"],
                        description=row["description"],
                        author=row["authors"],
                        areas=row["areas"],
                        time=row["time"]
                    )

            return None
        except sqlite3.Error as e:
            print(f"🚨 SQLite error in get_problem: {e}")
            return None
        except Exception as e:
            print(f"💥 General exception in get_problem: {e}")
            return None

    def search(
        self,
        title: str | None = None,
        areas: str | None = None,
        author: str | None = None,
        time: str | None = None
    ) -> list[dict]:
        try:
            with self.db_manager.connect(row_factory=sqlite3.Row) as db:
                sql = "SELECT id, title, description, authors, areas, time FROM problems WHERE 1=1"
                parameters: list[str] = []

                if title and title.strip():
                    sql += " AND LOWER(title) LIKE LOWER(?)"
                    parameters.append(f"%{title.strip()}%")

                if areas and areas.strip():
                    sql += " AND LOWER(areas) LIKE LOWER(?)"
                    parameters.append(f"%{areas.strip()}%")

                if author and author.strip():
                    sql += " AND LOWER(authors) LIKE LOWER(?)"
                    parameters.append(f"%{author.strip()}%")

                if time and time.strip():
                    sql += " AND time LIKE ?"
                    parameters.append(f"%{time.strip()}%")

                db.execute(sql, parameters)
                results = db.fetchall()
                return [dict(row) for row in results]
        except sqlite3.Error as e:
            print(f"🚨 SQLite error in search_problems: {e}")
            return []
        except Exception as e:
            print(f"💥 General exception in search_problems: {e}")
            return []

    def delete(self, problem_id: int) -> bool:
        try:
            with self.db_manager.connect() as db:
                cursor = db.execute("DELETE FROM problems WHERE id = ?", (problem_id,))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"SQLite error in delete_problem: {e}")
            return False
        except Exception as e:
            print(f"General exception in delete_problem: {e}")
            return False


    def get_by_author(self, author_name: str) -> list[dict]:
        try:
            with self.db_manager.connect(row_factory=sqlite3.Row) as db:
                db.execute("SELECT id, title, areas FROM problems WHERE authors = ?", (author_name,))
                rows = db.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"🚨 SQLite error in get_user_problems: {e}")
            return []
        except Exception as e:
            print(f"💥 General exception in get_user_problems: {e}")
            return []

    def update(self, problem_id: int, attribute: str, new_value: str) -> bool:
        column_alias = {
            'author': 'authors',
            'authors': 'authors'
        }
        allowed_columns = {'title', 'description', 'authors', 'areas', 'time'}
        column = column_alias.get(attribute, attribute)

        if column not in allowed_columns:
            return False

        try:
            with self.db_manager.connect() as db:
                sql = f"UPDATE problems SET {column} = ? WHERE id = ?"
                cursor = db.execute(sql, (new_value, problem_id))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"SQLite error in update_problem: {e}")
            return False
        except Exception as e:
            print(f"General exception in update_problem: {e}")
            return False

