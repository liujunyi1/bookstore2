from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.buyer import Buyer
from be.model.search_book import searchBook

bp_buyer = Blueprint("buyer", __name__, url_prefix="/buyer")


@bp_buyer.route("/new_order", methods=["POST"])
def new_order():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    books: [] = request.json.get("books")
    id_and_count = []
    for book in books:
        book_id = book.get("id")
        count = book.get("count")
        id_and_count.append((book_id, count)) 
    b = Buyer()
    code, message, order_id = b.new_order(user_id, store_id, id_and_count)
    return jsonify({"message": message, "order_id": order_id}), code


@bp_buyer.route("/payment", methods=["POST"])
def payment():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    password: str = request.json.get("password")
    b = Buyer()
    code, message = b.payment(user_id, password, order_id)
    return jsonify({"message": message}), code

@bp_buyer.route("/receive_order", methods=["POST"])
def receive_order():
    user_id: str = request.json.get("user_id")
    password: str = request.json.get("password")
    order_id: str = request.json.get("order_id")
    b = Buyer()
    code, message = b.receive_order(user_id, password, order_id)
    return jsonify({"message": message}), code

#取消订单
@bp_buyer.route("/cancel_order", methods=["POST"])
def cancel_order():
    user_id: str = request.json.get("user_id")
    password: str = request.json.get("password")
    order_id: str = request.json.get("order_id")
    b = Buyer()
    code, message = b.cancel_order(user_id, password, order_id)
    return jsonify({"message": message}), code

#询问订单状态
@bp_buyer.route("/get_order_status", methods=["POST"])
def get_order_status():
    user_id: str = request.json.get("user_id")
    #如果order
    store_id: str = request.json.get("store_id", None)
    order_id: str = request.json.get("order_id", None)
    status: str = request.json.get("status", None) 
    b = Buyer()
    code, message, order_status = b.get_order_status(user_id, store_id, order_id, status) 
    return jsonify({"message": message, "order_status": order_status}), code
        


@bp_buyer.route("/add_funds", methods=["POST"])
def add_funds():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    add_value = request.json.get("add_value") 
    b = Buyer()
    code, message = b.add_funds(user_id, password, add_value)
    return jsonify({"message": message}), code 

@bp_buyer.route("/search_book", methods=["POST"])
def search_book():
    page_no = request.json.get("page_no", 0)
    page_size = request.json.get("page_size", 10)
    fuzzy_title = request.json.get("fuzzy_title", None)
    req_tags = request.json.get("req_tags", None)
    book_id = request.json.get("book_id", None)
    isbn = request.json.get("isbn", None)
    author = request.json.get("author", None)
    lowest_price = request.json.get("lowest_price", None)
    highest_price = request.json.get("highest_price", None)
    lowest_pub_year = request.json.get("lowest_pub_year", None)
    highest_pub_year = request.json.get("highest_pub_year", None)
    store_id = request.json.get("store_id", None)
    publisher = request.json.get("publisher", None)
    translator = request.json.get("translator", None)
    binding = request.json.get("binding", None)
    order_by_method = request.json.get("order_by_method", None)
    having_stock = request.json.get("having_stock", None)
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print(page_no, page_size, fuzzy_title, req_tags, book_id, isbn, author, lowest_price, highest_price, lowest_pub_year, highest_pub_year, store_id, publisher, translator, binding, order_by_method, having_stock)
    s = searchBook()
    code, message, res = s.search_book(
        page_no=page_no,
        page_size=page_size,
        fuzzy_title=fuzzy_title,
        req_tags=req_tags,
        book_id=book_id,
        isbn=isbn,
        author=author,
        lowest_price=lowest_price,
        highest_price=highest_price,
        lowest_pub_year=lowest_pub_year,
        highest_pub_year=highest_pub_year,
        store_id=store_id,
        publisher=publisher,
        translator=translator,
        binding=binding,
        order_by_method=order_by_method,
        having_stock=having_stock,
        )
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    tmp=jsonify({"message": message, "books": res})
    print(tmp)
    return jsonify({"message": message, "books": res}), code
