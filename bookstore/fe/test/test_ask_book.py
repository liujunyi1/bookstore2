import pytest

from fe.access.buyer import Buyer
from fe.access.seller import Seller
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
from fe.access.book import Book
import uuid


class TestPayment:
    seller_id: str
    store_id: str
    buyer_id: str
    password: str
    seller: Seller 
    password2: str
    buy_book_info_list: [Book]
    total_price: int
    order_id: str
    buyer: Buyer
      

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id ="test_payment_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_payment_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_payment_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.password2 = self.buyer_id
        gen_book = GenBook(self.seller_id, self.store_id)
        self.seller=gen_book.seller
        ok, buy_book_id_list = gen_book.gen(
            non_exist_book_id=False, low_stock_level=False, max_book_count=5
        )
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.password)
        #self.seller = register_new_seller(self.seller_id, self.password2)
         
        self.buyer = b 
        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            if book.price is None:
                continue
            else:
                self.total_price = self.total_price + book.price * num
        yield

    def test_ok(self):
        code,tmp=self.buyer.search_book(store_id=self.store_id,order_by_method=["price",1])
        assert code == 200 
        books=tmp["books"]
        pre=0
        for book in books:
            assert book[0]==self.store_id
            assert book[1] in [b[0].id for b in self.buy_book_info_list]
            assert pre<=book[2]
            pre=book[2]
        
        
        id=self.buy_book_info_list[0][0].id
        title=self.buy_book_info_list[0][0].title 
        author=self.buy_book_info_list[0][0].author
        publisher=self.buy_book_info_list[0][0].publisher
        original_title=self.buy_book_info_list[0][0].original_title
        translator=self.buy_book_info_list[0][0].translator
        pub_year=self.buy_book_info_list[0][0].pub_year
        pages=self.buy_book_info_list[0][0].pages
        price=self.buy_book_info_list[0][0].price
        currency_unit=self.buy_book_info_list[0][0].currency_unit
        binding=self.buy_book_info_list[0][0].binding
        isbn=self.buy_book_info_list[0][0].isbn
        author_intro=self.buy_book_info_list[0][0].author_intro
        book_intro=self.buy_book_info_list[0][0].book_intro
        content=self.buy_book_info_list[0][0].content
        tags=self.buy_book_info_list[0][0].tags

        code,tmp=self.buyer.search_book(req_tags=tags,lowest_price=price,highest_price=price,fuzzy_title=title,store_id=self.store_id,order_by_method=["price",1])
        assert code == 200 
        #tmp["books"]的大小大于0
        assert len(tmp["books"])>0
