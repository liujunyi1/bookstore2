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
    tmp:[(str, int)]
      

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
        self.tmp=buy_book_id_list
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
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.seller.send_order(self.store_id, self.order_id)
        assert code == 200
        code = self.buyer.cancel_order(self.order_id)
        assert code == 200
        code,order_id=self.buyer.new_order(self.store_id, self.tmp)#通过再次购买验证前钱是否退还,以及库存是否更新
        assert code == 200 
        code = self.buyer.payment(order_id)
        assert code == 200
        code = self.buyer.cancel_order(order_id)
        assert code == 200
        code = self.buyer.cancel_order(order_id)
        assert code == 520 #重复取消是否会报错

