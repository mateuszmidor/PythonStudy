import unittest
from decimal import Decimal
from src.utils.capture_exception import capture_exception
from src.domain.asset import Asset

class AssetTest(unittest.TestCase):
    def test_adding_compatible_assets_results_in_amount_increase(self):
        # given
        phys1 = Asset(Decimal('100'), 'PHYS')
        phys2 = Asset(Decimal('50'), 'PHYS')

        # when
        result = phys1 + phys2 

        # then
        self.assertEqual(result.amount(), Decimal('150'))

    def test_adding_incompatible_assets_results_in_exception(self):
        # given
        phys1 = Asset(Decimal('100'), 'PHYS')
        phys2 = Asset(Decimal('50'), 'PSLV')

        # when
        e = capture_exception(phys1.__add__, phys2)

        # then
        self.assertIsInstance(e, ValueError)