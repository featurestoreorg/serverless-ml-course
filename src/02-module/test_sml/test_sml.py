from sml import cc_features, synthetic_data
from unittest import TestCase
import hopsworks
import time
import pytest
from contextlib import nullcontext as does_not_raise

class CreditCardsTest(TestCase):
    @pytest.fixture(autouse=True) 
    def init_ccs(self):
