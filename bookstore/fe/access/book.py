import os
import psycopg2
from psycopg2 import sql
import random
import base64
import simplejson as json


class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    currency_unit: str
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    #tags: [str]
    #pictures: [bytes]

    #def __init__(self):
        #self.tags = []
        #self.pictures = []


class BookDB:
    def __init__(self, large: bool = False):
        self.conn_params = {
            'host': 'localhost',
            'database': 'bookstore',
            'user': 'postgres',
            'password': 'junjun123',
            'port': '5432'
        }
        self.conn = psycopg2.connect(**self.conn_params)

    def get_book_count(self):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT count(id) FROM book")
                row = cursor.fetchone()
                return row[0] if row else 0
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return 0

    def get_book_info(self, start, size) -> [Book]:
        books = []
        try:
            with self.conn.cursor() as cursor:
                # 使用SQL参数化查询，避免SQL注入
                query = sql.SQL("""
                    SELECT id, title, author, 
                           publisher, original_title, 
                           translator, pub_year, pages, 
                           price, currency_unit, binding, 
                           isbn, author_intro, book_intro, 
                           content 
                    FROM book 
                    ORDER BY id 
                    LIMIT %s OFFSET %s
                """)
                cursor.execute(query, (size, start))
                
                for row in cursor:
                    book = Book()
                    book.id = row[0]
                    book.title = row[1]
                    book.author = row[2]
                    book.publisher = row[3]
                    book.original_title = row[4]
                    book.translator = row[5]
                    book.pub_year = row[6]
                    book.pages = row[7]
                    book.price = row[8]
                    book.currency_unit = row[9]
                    book.binding = row[10]
                    book.isbn = row[11]
                    book.author_intro = row[12]
                    book.book_intro = row[13]
                    book.content = row[14]
                    
                    # 注意：原代码中的tags和picture变量未定义，这里暂时注释掉
                    # tags = row[15]
                    # picture = row[16]
                    
                    # for tag in tags.split("\n"):
                    #     if tag.strip() != "":
                    #         book.tags.append(tag)
                    # for i in range(0, random.randint(0, 9)):
                    #     if picture is not None:
                    #         encode_str = base64.b64encode(picture).decode("utf-8")
                    #         book.pictures.append(encode_str)
                    
                    books.append(book)
                    
        except psycopg2.Error as e:
            print(f"Database error: {e}")
        return books