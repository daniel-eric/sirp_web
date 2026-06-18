import sqlite3
from dataclasses import dataclass
from typing import Optional
from database.db_config import DatabaseManager


@dataclass
class User:
    username: str
    email: str
    password: str
    tellNum: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "email": self.email,
            "tellNum": self.tellNum,
            "password": self.password
        }


class UserRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def create(self, user: User) -> bool:
        try:
            with self.db_manager.connect() as db:
                sql = '''INSERT INTO users (username, email, password, tellNum)
                         VALUES (?, ?, ?, ?)'''
                db.execute(sql, (user.username, user.email, user.password, user.tellNum))
            print(f"👤 User {user.username} registered successfully!")
            return True
        except sqlite3.IntegrityError as e:
            print(f"⚠️ Integrity error in add_user: Email or username already exists. {e}")
            return False
        except sqlite3.OperationalError as e:
            print(f"🛑 Operational error in add_user: Table or columns issue. {e}")
            return False
        except sqlite3.Error as e:
            print(f"🚨 SQLite error in add_user: {e}")
            return False
        except Exception as e:
            print(f"💥 General exception in add_user: {e}")
            return False

    def authenticate(self, identifier: str, password: str) -> Optional[str]:
        try:
            with self.db_manager.connect() as db:
                sql = '''
                    SELECT email FROM users
                    WHERE (email = ? OR username = ?)
                    AND password = ?
                '''
                db.execute(sql, (identifier, identifier, password))
                logged_in = db.fetchone()

                if logged_in:
                    return logged_in[0]

            print("⚠️ Login failed: Incorrect credentials.")
            return None
        except sqlite3.Error as e:
            print(f"🚨 SQLite error in login_user: {e}")
            return None
        except Exception as e:
            print(f"💥 General exception in login_user: {e}")
            return None

    def delete(self, current_email: str) -> bool:
        try:
            with self.db_manager.connect() as db:
                cursor = db.execute("DELETE FROM users WHERE email = ?", (current_email,))
                deleted = cursor.rowcount > 0

                if deleted:
                    print(f"✅ Account [{current_email}] removed successfully.")
                    return True

            print("⚠️ Removal failed: User not found in the system.")
            return False
        except sqlite3.Error as e:
            print(f"🚨 SQLite error in delete_account: {e}")
            return False
        except Exception as e:
            print(f"💥 General exception in delete_account: {e}")
            return False

    def update_username(self, current_email: str, new_username: str) -> bool:
        try:
            with self.db_manager.connect() as db:
                sql = "UPDATE users SET username = ? WHERE email = ?"
                cursor = db.execute(sql, (new_username, current_email))
                return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            print(f"⚠️ Integrity error in update_user_username: Username already in use. {e}")
            return False
        except sqlite3.Error as e:
            print(f"🚨 SQLite error in update_user_username: {e}")
            return False
        except Exception as e:
            print(f"💥 General exception in update_user_username: {e}")
            return False

    def update_tellNum(self, current_email: str, new_tellNum: str) -> bool:
        try:
            with self.db_manager.connect() as db:
                sql = "UPDATE users SET tellNum = ? WHERE email = ?"
                cursor = db.execute(sql, (new_tellNum, current_email))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"🚨 SQLite error in update_user_tellNum: {e}")
            return False
        except Exception as e:
            print(f"💥 General exception in update_user_tellNum: {e}")
            return False

    def update_password(self, current_email: str, new_password: str) -> bool:
        try:
            with self.db_manager.connect() as db:
                sql = "UPDATE users SET password = ? WHERE email = ?"
                cursor = db.execute(sql, (new_password, current_email))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"🚨 SQLite error in update_user_password: {e}")
            return False
        except Exception as e:
            print(f"💥 General exception in update_user_password: {e}")
            return False


    def search(self, query: str, exclude_email: str | None = None) -> list[dict]:
        try:
            with self.db_manager.connect(row_factory=sqlite3.Row) as db:
                sql = '''
                    SELECT username, email, tellNum
                    FROM users
                    WHERE (LOWER(username) LIKE LOWER(?) OR LOWER(email) LIKE LOWER(?))
                '''
                params = [f"%{query.strip()}%", f"%{query.strip()}%"]

                if exclude_email:
                    sql += " AND email != ?"
                    params.append(exclude_email)

                sql += " LIMIT 20"

                db.execute(sql, params)
                return [dict(row) for row in db.fetchall()]
        except sqlite3.Error as e:
            print(f"SQLite error in search_users: {e}")
            return []
        except Exception as e:
            print(f"General exception in search_users: {e}")
            return []

    def find_by_identifier(self, identifier: str) -> Optional[User]:
        try:
            with self.db_manager.connect(row_factory=sqlite3.Row) as db:
                sql = '''
                SELECT username, email, tellNum, password
                FROM users
                WHERE LOWER(email) = LOWER(?) OR LOWER(username) = LOWER(?)
                '''
                db.execute(sql, (identifier, identifier))
                searched_user = db.fetchone()

                if searched_user:
                    return User(
                        username=searched_user["username"],
                        email=searched_user["email"],
                        password=searched_user["password"],
                        tellNum=searched_user["tellNum"]
                    )

            print("⚠️ Search failed: User data not found.")
            return None
        except sqlite3.Error as e:
            print(f"🚨 SQLite error in search_user: {e}")
            return None
        except Exception as e:
            print(f"💥 General exception in search_user: {e}")
            return None
