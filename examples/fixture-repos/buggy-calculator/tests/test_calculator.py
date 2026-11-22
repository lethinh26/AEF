import pytest

from calculator import apply_discount


@pytest.mark.parametrize(
    ("price", "discount_rate", "expected"),
    [
        (100.0, 0.2, 80.0),
        (50.0, 0.0, 50.0),
        (80.0, 1.0, 0.0),
    ],
)
def test_apply_discount_returns_remaining_price(
    price: float, discount_rate: float, expected: float
) -> None:
    assert apply_discount(price, discount_rate) == pytest.approx(expected)
