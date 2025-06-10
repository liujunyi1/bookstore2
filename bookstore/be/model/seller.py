import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from be.model import error
from be.model import db_conn


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        price: int,
        stock_level: int,
    ):
       
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)
        
            
            with self.conn.cursor() as cur:
                cur.execute(
                    sql.SQL(
                        "INSERT INTO store (store_id, book_id, price, sale_count, stock_level) "
                        "VALUES (%s, %s, %s, %s, %s)"
                    ),
                    (store_id, book_id, price, 0, stock_level),
                )
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            return 528, f"{str(e)}"
        except BaseException as e:
            self.conn.rollback()
            return 530, f"{str(e)}"
        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            with self.conn.cursor() as cur:
                cur.execute(
                    sql.SQL(
                        "UPDATE store SET stock_level = stock_level + %s "
                        "WHERE store_id = %s AND book_id = %s"
                    ),
                    (add_stock_level, store_id, book_id),
                )
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            return 528, f"{str(e)}"
        except BaseException as e:
            self.conn.rollback()
            return 530, f"{str(e)}"
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            with self.conn.cursor() as cur:
                cur.execute(
                    sql.SQL("INSERT INTO user_store (store_id, user_id) VALUES (%s, %s)"),
                    (store_id, user_id),
                )
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            return 528, f"{str(e)}"
        except BaseException as e:
            self.conn.rollback()
            return 530, f"{str(e)}"
        return 200, "ok"
    
    def send_order(self, user_id: str, store_id: str, order_id: str) -> (int, str): 
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            
            with self.conn.cursor() as cur:
                #查看这个订单的状态以及店铺
                cur.execute('SELECT status,store_id FROM new_order WHERE order_id = %s FOR UPDATE' , (order_id,))
                #result = cur.fetchone()
                if cur.rowcount == 0:
                    return error.error_invalid_order_id(order_id)
                result = cur.fetchone()
                if result[0].strip() != 'paid':
                    #print(result[0],'paid',"^^^^^^^^^^^^^^^^^^^")
                    return error.error_invalid_order_status(order_id)
                #修改这个订单的状态
                cur.execute('UPDATE new_order SET status = %s WHERE order_id = %s', ('sent', order_id))
                self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            return 528, f"{str(e)}"
        except BaseException as e:
            self.conn.rollback()
            return 530, f"{str(e)}"
        return 200, "ok"
                
                 