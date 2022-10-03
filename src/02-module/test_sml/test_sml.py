from sml import synthetic_data
from unittest import TestCase
import pytest
from contextlib import nullcontext as does_not_raise

@pytest.mark.parametrize(
    "credit_card_number, cash_amounts, length, delta, radius, country_code, excp",
    [("1111 2222 3333 4444",[112.10, 11.23], 1, 1, 10.0, 'US', does_not_raise())
    ,("1111 2222 3333 44",[-12.00], -1, 1, 1.0, 'IE', pytest.raises(Exception))]
)    
def test_generate_atm_withdrawal(credit_card_number: str, cash_amounts: list, length: int, \
                                 delta: int, radius: float, country_code, excp):
    with excp:
        synthetic_data.generate_atm_withdrawal(credit_card_number, cash_amounts, length, delta, radius, country_code)
        
