import uuid
import json
import logging
import psycopg2
import time
import datetime
from psycopg2 import sql
from be.model import db_conn
from be.model import error

class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

   

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            
            uid = f"{user_id}_{store_id}_{str(uuid.uuid1())}"
            tot_total = 0
            
            with self.conn:  # 开启事务
                with self.conn.cursor() as cursor:
                    for book_id, count in id_and_count:
                        # 检查书籍存在性和库存
                        print("######################")
                        print(book_id, count)
                        cursor.execute(
                            "SELECT stock_level, price FROM store "
                            "WHERE store_id = %s AND book_id = %s;",  
                            (store_id, book_id)
                        )
                        print("okkkkkkkkkkkkkkkkkkkkk")
                        row = cursor.fetchone()
                        if not row:
                            return error.error_non_exist_book_id(book_id) + (order_id,)
                        
                        stock_level, price = row[0], row[1]
                        if stock_level < count:
                            return error.error_stock_level_low(book_id) + (order_id,)
                        
                        # 扣减库存（使用带条件的UPDATE避免超卖）
                        cursor.execute(
                            "UPDATE store SET stock_level = stock_level - %s "
                            "WHERE store_id = %s AND book_id = %s AND stock_level >= %s "
                            "RETURNING store_id;",
                            (count, store_id, book_id, count)
                        )
                        if cursor.rowcount == 0:
                            return error.error_stock_level_low(book_id) + (order_id,)
                        
                        # 记录订单详情
                        cursor.execute(
                            "INSERT INTO new_order_detail (order_id, book_id, count, price) "
                            "VALUES (%s, %s, %s, %s);",
                            (uid, book_id, count, price)
                        )
                        
                        tot_total += price * count
                    
                    # 记录订单主表
                    #timestamp = datetime.fromtimestamp(time.time())
                    timestamp = datetime.datetime.now() 
                    cursor.execute(
                        "INSERT INTO new_order (order_id, store_id, user_id, status, time, price) "
                        "VALUES (%s, %s, %s, %s, %s, %s);",
                        (uid, store_id, user_id, "unpaid", timestamp, tot_total)
                    )
            
            self.conn.commit()
            order_id = uid
            return 200, "订单创建成功", order_id
    
        except psycopg2.Error as e:
            self.conn.rollback()  # 手动回滚（虽然with self.conn已自动处理）
            print(str(e))
            return 528, f"数据库错误: {str(e)}", order_id
        except Exception as e:
            self.conn.rollback()
            print(str(e))
            return 530, f"系统错误: {str(e)}", order_id
            
    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT order_id, user_id, store_id,price FROM new_order WHERE order_id = %s",
                (order_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            buyer_id = row[1]
            store_id = row[2]
            price = row[3]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            cursor.execute(
                "SELECT balance, password FROM users WHERE user_id = %s;", (buyer_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            cursor.execute(
                "SELECT store_id, user_id FROM user_store WHERE store_id = %s;",
                (store_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            cursor.execute(
                "SELECT book_id, count, price FROM new_order_detail WHERE order_id = %s;",
                (order_id,),
            )
            total_price = price

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            cursor.execute(
                "UPDATE users set balance = balance - %s "
                "WHERE user_id = %s AND balance >= %s "
                "RETURNING user_id;",
                (total_price, buyer_id, total_price),
            )
            if cursor.rowcount == 0:
                return error.error_not_sufficient_funds(order_id)

            cursor.execute(
                "UPDATE users set balance = balance + %s WHERE user_id = %s "
                "RETURNING user_id;",
                (total_price, seller_id),
            )

            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(seller_id)

            cursor.execute(
                "DELETE FROM new_order WHERE order_id = %s", (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            cursor.execute(
                "DELETE FROM new_order_detail where order_id = %s", (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            conn.commit()

        except psycopg2.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT password from users where user_id=%s", (user_id,)
            )
            print("11111111111111")
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()
            print("222222222222222")
            if row[0] != password:
                return error.error_authorization_fail()
            print("33333333333333333")
            cursor.execute(
                "UPDATE users SET balance = balance + %s WHERE user_id = %s "
                "RETURNING user_id;",
                (add_value, user_id),
            )
            print("4444444444444444")
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            self.conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"