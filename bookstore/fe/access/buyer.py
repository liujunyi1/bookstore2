import requests
import simplejson
import datetime
from urllib.parse import urljoin
from fe.access.auth import Auth


class Buyer:
    def __init__(self, url_prefix, user_id, password):
        self.url_prefix = urljoin(url_prefix, "buyer/")
        self.user_id = user_id
        self.password = password
        self.token = ""
        self.terminal = "my terminal"
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.user_id, self.password, self.terminal)
        assert code == 200

    def new_order(self, store_id: str, book_id_and_count: [(str, int)]) -> (int, str):
        print("$$$$$$$$$$$$$$$$$$$$$$")
        print(self.user_id, store_id)
        books = [] 
        for id_count_pair in book_id_and_count:
            books.append({"id": id_count_pair[0], "count": id_count_pair[1]})
        json = {"user_id": self.user_id, "store_id": store_id, "books": books}
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "new_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        response_json = r.json()
        return r.status_code, response_json.get("order_id")

    def payment(self, order_id: str):
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "payment")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code
    
    def receive_order(self, order_id: str):
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "receive_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def cancel_order(self, order_id: str):
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "order_id": order_id,
            }
        url = urljoin(self.url_prefix, "cancel_order")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code
    
    def get_order_status(self,store_id: None,order_id:None,status:None) -> (int, [[str,str,str,str,str,int]]):
         
        json = {
            "user_id": self.user_id, 
            "store_id": store_id,
            "order_id": order_id,
            "status": status,
        }
        url = urljoin(self.url_prefix, "get_order_status")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code, r.json()


    def add_funds(self, add_value: str) -> int:
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "add_value": add_value,
        } 
        url = urljoin(self.url_prefix, "add_funds")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code 

    def search_book(self,page_no=None,page_size=None,
        fuzzy_title=None,req_tags=None,book_id=None,
        isbn=None,author=None,lowest_price=None,highest_price=None,lowest_pub_year=None,
        highest_pub_year=None,store_id=None,publisher=None,translator=None,binding=None,
        order_by_method=None,having_stock=None):
        json = {
            "page_no": page_no,
            "page_size": page_size,
            "fuzzy_title": fuzzy_title,
            "req_tags": req_tags,
            "book_id": book_id,
            "isbn": isbn,
            "author": author,
            "lowest_price": lowest_price,
            "highest_price": highest_price,
            "lowest_pub_year": lowest_pub_year,
            "highest_pub_year": highest_pub_year,
            "store_id": store_id,
            "publisher": publisher,
            "translator": translator,
            "binding": binding,
            "order_by_method": order_by_method,
            "having_stock": having_stock,
        }
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(json)
        url = urljoin(self.url_prefix, "search_book")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code, r.json()