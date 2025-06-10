import logging
import os
import threading
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class Store:
    database: str
    conn_params: dict

    def __init__(self, db_path):
        self.conn_params = {
            'host': 'localhost',
            'database': 'bookstore',
            'user': 'postgres',
            'password': 'junjun123',
            'port': '5432'
        }
        self.init_tables()

    def get_db_conn(self) -> psycopg2.extensions.connection:
        try:
            conn = psycopg2.connect(**self.conn_params)
            return conn
        except psycopg2.Error as e:
            logging.error(f"Error connecting to PostgreSQL: {e}")
            raise

    def init_tables(self):
        try:
            conn = self.get_db_conn()
            conn.autocommit = True  
            ''' 
            try:
                with conn.cursor() as cursor:
                    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.database}'")
                    if not cursor.fetchone():
                        cursor.execute(f"CREATE DATABASE {self.database}")
                        logging.info(f"Created new database {self.database}")
            except Exception as e:
                logging.error(f"Error checking/creating database: {e}")
                raise
            
            conn.close()
            self.conn_params['database'] = self.database
            conn = self.get_db_conn()
            '''
            with conn.cursor() as cursor:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY, 
                    password TEXT NOT NULL, 
                    balance INT NOT NULL, 
                    token TEXT, 
                    terminal TEXT
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_store(
                    user_id TEXT, 
                    store_id TEXT, 
                    PRIMARY KEY(user_id, store_id)
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS store(
                    store_id TEXT, 
                    book_id TEXT, 
                    price INT, 
                    sale_count INT,
                    stock_level INT,
                    PRIMARY KEY(store_id, book_id)
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS new_order(
                order_id TEXT PRIMARY KEY,
                user_id TEXT,
                store_id TEXT,
                status CHAR(20),
                time TIMESTAMP,
                price INT
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS new_order_detail(
                    order_id TEXT, 
                    book_id TEXT, 
                    count INT, 
                    price INT,
                    PRIMARY KEY(order_id, book_id)
                )
                """)

                conn.commit()
        except psycopg2.Error as e:
            logging.error(f"PostgreSQL error: {e}")
            if 'conn' in locals():
                conn.rollback()
            raise
        finally:
            if 'conn' in locals():
                conn.close()

database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()

def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)

def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()