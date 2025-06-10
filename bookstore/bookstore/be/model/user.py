import jwt
import time
import logging
import psycopg2
from be.model import error
from be.model import db_conn

def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")


def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded

class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "INSERT into users(user_id, password, balance, token, terminal) "
                    "VALUES (%s, %s, %s, %s, %s);",
                    (user_id, password, 0, token, terminal),
                )
            self.conn.commit()
        except psycopg2.Error:
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT token from users where user_id=%s", (user_id,))
                row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()
            db_token = row[0]
            if not self.__check_token(user_id, db_token, token):
                return error.error_authorization_fail()
            return 200, "ok"
        except psycopg2.Error as e:
            logging.error(f"Database error: {e}")
            return 528, f"Database error: {str(e)}"

    def check_password(self, user_id: str, password: str) -> (int, str):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT password from users where user_id=%s", (user_id,)
                )
                row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if password != row[0]:
                return error.error_authorization_fail()

            return 200, "ok"
        except psycopg2.Error as e:
            logging.error(f"Database error: {e}")
            return 528, f"Database error: {str(e)}"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users set token= %s, terminal = %s where user_id = %s "
                    "RETURNING user_id;",
                    (token, terminal, user_id),
                )
                if cursor.rowcount == 0:
                    return error.error_authorization_fail() + ("",)
            self.conn.commit()
        except psycopg2.Error as e:
            logging.error(f"Database error: {e}")
            return 528, f"{str(e)}", ""
        except BaseException as e:
            logging.error(f"General error: {e}")
            return 530, f"{str(e)}", ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> (int, str):
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)

            with self.conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET token = %s, terminal = %s WHERE user_id=%s "
                    "RETURNING user_id;",
                    (dummy_token, terminal, user_id),
                )
                if cursor.rowcount == 0:
                    return error.error_authorization_fail()

            self.conn.commit()
        except psycopg2.Error as e:
            logging.error(f"Database error: {e}")
            return 528, f"{str(e)}"
        except BaseException as e:
            logging.error(f"General error: {e}")
            return 530, f"{str(e)}"
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            with self.conn.cursor() as cursor:
                cursor.execute("DELETE from users where user_id=%s", (user_id,))
                if cursor.rowcount == 1:
                    self.conn.commit()
                else:
                    return error.error_authorization_fail()
        except psycopg2.Error as e:
            logging.error(f"Database error: {e}")
            return 528, f"{str(e)}"
        except BaseException as e:
            logging.error(f"General error: {e}")
            return 530, f"{str(e)}"
        return 200, "ok"

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> (int, str):
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE users set password = %s, token= %s, terminal = %s where user_id = %s "
                    "RETURNING user_id;",
                    (new_password, token, terminal, user_id),
                )
                if cursor.rowcount == 0:
                    return error.error_authorization_fail()

            self.conn.commit()
        except psycopg2.Error as e:
            logging.error(f"Database error: {e}")
            return 528, f"{str(e)}"
        except BaseException as e:
            logging.error(f"General error: {e}")
            return 530, f"{str(e)}"
        return 200, "ok"