import psycopg2
import json
import logging
from be.model import db_conn
from be.model import error

DB_CONFIG = {
    "dbname": "bookstore",
    "user": "postgres",
    "password": "junjun123",
    "host": "localhost",
    "port": "5432"
}

class searchBook(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.order_by_conditions = [
            'stock_level', 'sale_count', 'price'
        ]#排序条件，可选值为'stock_level','sales', 'pub_year', 'price'

    def search_book(
    self,
    page_no=0,
    page_size=10,
    fuzzy_title=None,
    req_tags=None,#格式为json数组，如["tag1","tag2"]
    book_id=None,
    isbn=None,
    author=None,
    lowest_price=None,
    highest_price=None,
    lowest_pub_year=None,
    highest_pub_year=None,
    store_id=None,
    publisher=None,
    translator=None,
    binding=None,
    order_by_method=None,  # [stock_level, sales, price] + [1,-1]  1 means increasingly and -1 means decreasingly
    having_stock=None,
    ):
        books = []
        query = "SELECT id FROM book"
        conditions = []
        params = []
        
        try:
            # 构建查询条件
            if fuzzy_title is not None:
                conditions.append("title LIKE %s")
                params.append(r"%" + fuzzy_title + "%")
                
            if req_tags is not None:
                conditions.append("tag @> %s")
                
                tags = json.dumps(req_tags)
                params.append(tags)
                
            if book_id is not None:
                conditions.append("id = %s")
                params.append(book_id)
                
            if isbn is not None:
                conditions.append("isbn = %s")
                params.append(isbn)
                
            if author is not None:
                conditions.append("author = %s")
                params.append(author)
                
            if lowest_price is not None:
                conditions.append("price >= %s")
                params.append(lowest_price)
                
            if highest_price is not None:
                conditions.append("price <= %s")
                params.append(highest_price)
            '''
            if store_id is not None:
                conditions.append("store_id = %s")
                params.append(store_id)
            '''  
            if lowest_pub_year is not None:
                conditions.append("pub_year >= %s")
                params.append(lowest_pub_year)
                
            if highest_pub_year is not None:
                conditions.append("pub_year < %s")
                params.append(str(int(highest_pub_year) + 1))
                
            if publisher is not None:
                conditions.append("publisher = %s")
                params.append(publisher)
                
            if translator is not None:
                conditions.append("translator = %s")
                params.append(translator)
                
            if binding is not None:
                conditions.append("binding = %s")
                params.append(binding)
            '''
            if having_stock is True:
                conditions.append("stock_level > 0")
            '''
            # 构建排序条件

            # 构建 WHERE 子句
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            
            
            # 执行查询
            preres=[] 
            res=[]
            conn=self.conn
            with self.conn as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params) 
                    #[dict(row) for row in cur.fetchall()]
                    for row in cur.fetchall():
                        #print(row[0]) 
                        preres.append(row[0])  
                    '''
                    for book in books:
                        print(book['title'],book['price'])
                    '''
                    #从store库中选择book_id在preres中的书籍信息，用原来的cur
                    query2 = "SELECT * FROM store WHERE book_id IN %s"
                    params2 = [tuple(preres)]
                    # having stock
                    if having_stock is not None:
                        query2 += " AND stock_level > 0"
                    if store_id is not None:
                        query2 += " AND store_id = %s"
                        params2.append(store_id)
                    #构造order by子句
                    if order_by_method is not None:
                        if order_by_method[0] in self.order_by_conditions:
                            query2 += " ORDER BY " + order_by_method[0]
                            if order_by_method[1] == 1:
                                query2 += " ASC"
                            else:
                                query2 += " DESC"
                    # 添加分页
                    # 添加分页
                    if page_size is not None:
                        query += " LIMIT %s OFFSET %s"
                        params.extend([page_size, page_no * page_size])
                    #print(query2,params2)
                    with conn.cursor() as cur2:
                        cur2.execute(query2, params2)
                        for row in cur2.fetchall():
                            #将row转化为列表
                            res.append(list(row))
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            print(res)
            return 200, "ok",res
            
        except psycopg2.Error as e:
            logging.error(f"Database error (528): {str(e)}")
            return 528, str(e), []
        except Exception as e:
            logging.error(f"Unexpected error (530): {str(e)}")
            return 530, str(e), []
         