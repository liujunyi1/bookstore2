import psycopg2
from psycopg2 import sql
from be.model import error


class DBConn:
    def __init__(self):
        # 假设store.get_db_conn()返回PostgreSQL连接参数
        conn_params = {
            'host': 'localhost',
            'database': 'bookstore',
            'user': 'postgres',
            'password': 'junjun123',
            'port': '5432'
        }
        self.conn = psycopg2.connect(**conn_params)
    
    def user_id_exist(self, user_id):
        """检查用户ID是否存在"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    sql.SQL("SELECT 1 FROM users WHERE user_id = %s LIMIT 1"),
                    (user_id,)
                )
                return cursor.fetchone() is not None
        except psycopg2.Error as e:
            print(f"数据库错误: {e}")
            return False
    
    def book_id_exist(self, store_id, book_id):
        """检查书籍在店铺中是否存在"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    sql.SQL("SELECT 1 FROM store WHERE store_id = %s AND book_id = %s LIMIT 1"),
                    (store_id, book_id)
                )
                return cursor.fetchone() is not None
        except psycopg2.Error as e:
            print(f"数据库错误: {e}")
            return False
    
    def store_id_exist(self, store_id):
        """检查店铺ID是否存在"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    sql.SQL("SELECT 1 FROM user_store WHERE store_id = %s LIMIT 1"),
                    (store_id,)
                )
                return cursor.fetchone() is not None
        except psycopg2.Error as e:
            print(f"数据库错误: {e}")
            return False