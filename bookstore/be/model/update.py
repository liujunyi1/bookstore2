import sys
sys.path.append(r"C:\Users\19902\Desktop\cdms.xuan_zhou.2025spring.dase\bookstore")

import time
import psycopg2
import uuid
import json
import logging
import datetime
from be.model import db_conn
from be.model import error
from be.model import db_conn


class Scanner(db_conn.DBConn):#该类用于扫描订单，将过期订单状态改为canceled，并将库存量和销量更新

    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.live_number = 300
        self.scan_interval = 6

    def update(self, keep=False):
        tim=0
        while(1): 
           tim+=1
           if tim>=self.live_number:
               break 
            #找到10秒以前的时间
           timestamp = datetime.datetime.now() - datetime.timedelta(seconds=self.scan_interval)
           
           print(timestamp)
            #找到过期订单(状态为unpaid)
           conn=self.conn
           cur=conn.cursor()
           #用set语句对订单状态进行修改
           #找到所有超时的订单
           cur.execute("SELECT order_id,store_id FROM new_order WHERE status='unpaid' AND time<%s",(timestamp,))
           rows=cur.fetchall()
           #遍历超时订单
           for row in rows:
               order_id=row[0]
               store_id=row[1]
               #更新订单状态
               
               #找到该订单对应的商品信息
               cur.execute("SELECT book_id,count FROM new_order_detail WHERE order_id=%s",(order_id,))
               rows2=cur.fetchall()
               for row2 in rows2:
                   book_id=row2[0]
                   count=row2[1]
                   #更新库存量和销量
                   cur.execute("UPDATE store SET stock_level=stock_level+%s,sale_count=sale_count-%s WHERE book_id=%s AND store_id=%s",(count,count,book_id,store_id)) 
                #更新订单状态
                #cur.execute("UPDATE new_order SET status='cancelled' WHERE order_id=%s",(order_id,))
               print(order_id)
               cur.execute("UPDATE new_order SET status='cancelled' WHERE order_id=%s",(order_id,))
               cur.execute(
                "INSERT INTO dead_order (order_id, store_id, user_id, status, time, price) "
                "SELECT order_id, store_id, user_id, status, time, price FROM new_order WHERE order_id = %s",
                (order_id,),
            )
               cur.execute(
                    "INSERT INTO dead_order_detail (order_id, book_id, count, price) "
                    "SELECT order_id, book_id, count, price FROM new_order_detail WHERE order_id = %s",
                    (order_id,),
                )
                #删除相关的信息
               cur.execute(
                    "DELETE FROM new_order_detail WHERE order_id = %s",
                    (order_id,),
                )
               cur.execute(
                    "DELETE FROM new_order WHERE order_id = %s",
                    (order_id,),
                )

           #cur.execute("UPDATE new_order SET status='cancelled' WHERE status='unpaid' AND time<%s",(timestamp,))
           conn.commit()
           time.sleep(self.scan_interval)
           

            

               
s=Scanner()
s.update()