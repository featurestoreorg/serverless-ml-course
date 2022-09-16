from sml import cc_features
from unittest import TestCase
import pytest
from contextlib import nullcontext as does_not_raise

@pytest.mark.parametrize(
    "long, lat, prev_long, prev_lat, excp",
    [(42.30865,-83.48216,37.60876,-77.37331, does_not_raise())
    ,(42.30865,-83.48216,37.60876,-377.37331, pytest.raises(Exception))]
)    
def test_haversine(long, lat, prev_long, prev_lat, excp):
    with excp:
        cc_features.haversine_distance(long, lat, prev_long, prev_lat)

