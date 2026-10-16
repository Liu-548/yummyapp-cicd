import unittest
from unittest.mock import patch

from yummy_app import YummyApp
import gps_service


# ================================================================
# CAP DO 1: Bo test co ban cho san
# ================================================================
class TestEasyLevel(unittest.TestCase):
    """Kiem thu chuc nang co ban tinh tien don hang"""

    def setUp(self):
        self.app = YummyApp()

    def test_calculate_total_for_single_item(self):
        cart = {"pho": 2}
        self.assertEqual(self.app.calculate_order_total(cart), 100000)

    def test_calculate_total_for_multiple_items(self):
        cart = {"pho": 1, "bun": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 95000)

    def test_calculate_total_for_empty_cart(self):
        self.assertEqual(self.app.calculate_order_total({}), 0.0)

    def test_calculate_total_with_zero_quantity(self):
        cart = {"pho": 0}
        self.assertEqual(self.app.calculate_order_total(cart), 0.0)


# ================================================================
# CAP DO 2: Kiem thu apply_promo_code (mang di dong + phien ban HDH)
# ================================================================
class TestMediumLevel(unittest.TestCase):
    """Gia lap trang thai mang va phien ban HDH qua constructor (stub)."""

    def test_apply_promo_online_valid(self):
        app = YummyApp(network_status="online", os_version=15)
        result = app.apply_promo_code(100000, "GIAM10")
        self.assertAlmostEqual(result, 90000.0)

    def test_apply_promo_offline_raises_connection_error(self):
        app = YummyApp(network_status="offline")
        with self.assertRaises(ConnectionError):
            app.apply_promo_code(100000, "GIAM10")

    def test_apply_special_code_on_os_15(self):
        app = YummyApp(os_version=15)
        result = app.apply_promo_code(100000, "NEW_OS_ONLY")
        self.assertAlmostEqual(result, 80000.0)

    def test_apply_special_code_on_os_14_raises_value_error(self):
        app = YummyApp(os_version=14)
        with self.assertRaises(ValueError) as ctx:
            app.apply_promo_code(100000, "NEW_OS_ONLY")
        self.assertIn("15", str(ctx.exception))


# ================================================================
# CAP DO 3: Mock phan cung GPS cho get_nearby_restaurants
# ================================================================
class TestHardLevel(unittest.TestCase):
    """Dong the ham GPS phan cung bang @patch."""

    def setUp(self):
        self.app = YummyApp()

    @patch('yummy_app.gps_service.get_current_location')
    def test_nearby_restaurants_in_area(self, mock_gps):
        mock_gps.return_value = (10.0, 105.0)
        result = self.app.get_nearby_restaurants()
        self.assertEqual(
            result, ["Nha hang Pho Ly Quoc Su", "Bun cha Huong Lien"]
        )
        mock_gps.assert_called_once()

    @patch('yummy_app.gps_service.get_current_location')
    def test_nearby_restaurants_out_of_area(self, mock_gps):
        mock_gps.return_value = (20.0, 110.0)
        result = self.app.get_nearby_restaurants()
        self.assertEqual(result, [])
        mock_gps.assert_called_once()

    @patch('yummy_app.gps_service.get_current_location')
    def test_nearby_restaurants_gps_lost(self, mock_gps):
        mock_gps.side_effect = gps_service.GPSSignalLostError()
        result = self.app.get_nearby_restaurants()
        self.assertEqual(result, "Khong the xac dinh vi tri.")
        mock_gps.assert_called_once()


if __name__ == '__main__':
    unittest.main()