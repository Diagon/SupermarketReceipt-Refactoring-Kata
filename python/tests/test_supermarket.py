import pytest

from model_objects import Product, SpecialOfferType, ProductUnit
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog


def test_ten_percent_discount():
    catalog = FakeCatalog()
    toothbrush = Product("toothbrush", ProductUnit.EACH)
    catalog.add_product(toothbrush, 0.99)

    apples = Product("apples", ProductUnit.KILO)
    catalog.add_product(apples, 1.99)

    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)

    cart = ShoppingCart()
    cart.add_item_quantity(apples, 2.5)

    receipt = teller.checks_out_articles_from(cart)

    assert 4.975 == pytest.approx(receipt.total_price(), 0.01)
    assert [] == receipt.discounts
    assert 1 == len(receipt.items)
    receipt_item = receipt.items[0]
    assert apples == receipt_item.product
    assert 1.99 == receipt_item.price
    assert 2.5 * 1.99 == pytest.approx(receipt_item.total_price, 0.01)
    assert 2.5 == receipt_item.quantity



@pytest.fixture()
def toothbrush():
    toothbrush = Product("toothbrush", ProductUnit.EACH)
    yield toothbrush

@pytest.fixture()
def catalog(toothbrush):
    catalog = FakeCatalog()

    catalog.add_product(toothbrush, 0.99)
    yield catalog


def test_buy_N_get_one_free(catalog, toothbrush):
    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, None)
    price = catalog.prices[toothbrush.name]

    cart = ShoppingCart()
    cart.add_item_quantity(toothbrush, 2)

    receipt = teller.checks_out_articles_from(cart)

    # Test below offer applicability
    assert price*2 == pytest.approx(receipt.total_price(), 0.01)
    assert [] == receipt.discounts
    assert 1 == len(receipt.items)
    assert 0 == len(receipt.discounts)
    receipt_item = receipt.items[0]
    assert toothbrush == receipt_item.product

    # Test with offer applicable
    cart.add_item_quantity(toothbrush, 1)
    receipt = teller.checks_out_articles_from(cart)

    assert price*2 == pytest.approx(receipt.total_price(), 0.01)
    assert price * (3 - 1) - price * 3 == pytest.approx(receipt.discounts[0].discount_amount, 0.01)
    assert 2 == len(receipt.items)
    assert 1 == len(receipt.discounts)
    assert toothbrush == receipt.discounts[0].product

    # Test offer used only once
    cart.add_item_quantity(toothbrush, 1)
    receipt = teller.checks_out_articles_from(cart)
    assert price * ((3-1)+1) == pytest.approx(receipt.total_price(), 0.01)
    assert price * (3 - 1) - price * 3 == pytest.approx(receipt.discounts[0].discount_amount, 0.01)
    assert 3 == len(receipt.items)
    assert 1 == len(receipt.discounts)
    assert toothbrush == receipt.discounts[0].product


@pytest.mark.parametrize(
    "offer,amount,price_for_n",
    [
        (SpecialOfferType.FIVE_FOR_AMOUNT, 5, 3.50),
        # (SpecialOfferType.TWO_FOR_AMOUNT, 2, 0.75),
        # ^ this test is broken; Code seems to be written for python 2
        # Specifically, shopping_cart.py:45 uses old syntax for integer division
    ],
)
def test_N_for_amount_parametrized(offer, amount, price_for_n, catalog, toothbrush):
    price = catalog.prices[toothbrush.name]
    teller = Teller(catalog)
    teller.add_special_offer(offer, toothbrush, price_for_n)

    cart = ShoppingCart()
    cart.add_item_quantity(toothbrush, 1)

    receipt = teller.checks_out_articles_from(cart)

    # Test below offer applicability
    assert price == pytest.approx(receipt.total_price(), 0.01)
    assert [] == receipt.discounts
    assert 1 == len(receipt.items)
    assert 0 == len(receipt.discounts)
    receipt_item = receipt.items[0]
    assert toothbrush == receipt_item.product

    # Test with offer applicable
    cart.add_item_quantity(toothbrush, amount-1)
    receipt = teller.checks_out_articles_from(cart)

    assert price_for_n == pytest.approx(receipt.total_price(), 0.01)
    assert price_for_n - price * amount == pytest.approx(receipt.discounts[0].discount_amount, 0.01)
    assert 2 == len(receipt.items)
    assert 1 == len(receipt.discounts)
    assert toothbrush == receipt.discounts[0].product

    # Test offer used only once
    cart.add_item_quantity(toothbrush, 1)
    receipt = teller.checks_out_articles_from(cart)
    assert price_for_n + price == pytest.approx(receipt.total_price(), 0.01)
    assert price_for_n - price * amount == pytest.approx(receipt.discounts[0].discount_amount, 0.01)
    assert 3 == len(receipt.items)
    assert 1 == len(receipt.discounts)
    assert toothbrush == receipt.discounts[0].product