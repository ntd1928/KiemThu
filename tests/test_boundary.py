"""
Kiểm thử giá trị biên (Boundary Value Analysis - BVA)
=====================================================
Biến kiểm thử : order_value (int, 0 ≤ X ≤ 50.000.000)
Biến cố định  : member_tier="Bạc", payment_method="Tiền mặt", is_flash_sale=False
                 → Chỉ có R1 (giảm theo giá trị đơn) tác động.

Miền con:
  Miền 1: [0, 499.999]           → 0%
  Miền 2: [500.000, 2.000.000]   → 5%
  Miền 3: [2.000.001, 50.000.000] → 10%

Chiến lược: BVA thường (4n+1) + BVA mạnh (6n+1) bổ sung min-, max+
Tổng: 15 ca kiểm thử
"""

import pytest
from promotion import calculate_promotion

# ============================================================
# Biến cố định cho tất cả test BVA
# ============================================================
FIXED_TIER = "Bạc"
FIXED_PAYMENT = "Tiền mặt"
FIXED_FLASH = False


def call(order_value):
    """Helper: gọi hàm tính khuyến mại với các biến cố định."""
    return calculate_promotion(order_value, FIXED_TIER, FIXED_PAYMENT, FIXED_FLASH)


# ============================================================
# BVA THƯỜNG (Normal BVA) – 13 ca kiểm thử
# ============================================================

class TestBVA_Boundary500k:
    """Ngưỡng biên 500.000 – ranh giới giữa Miền 1 (0%) và Miền 2 (5%)."""

    def test_BVA01_min_gia_tri_nho_nhat(self):
        """BVA-01: min – Giá trị nhỏ nhất = 0 → 0%"""
        result = call(0)
        assert result["discount_percent"] == 0
        assert result["final_price"] == 0

    def test_BVA02_nom_vung1(self):
        """BVA-02: nom vùng 1 – Giá trị thông thường = 250.000 → 0%"""
        result = call(250_000)
        assert result["discount_percent"] == 0
        assert result["final_price"] == 250_000

    def test_BVA03_max_minus_bien_500k(self):
        """BVA-03: max- biên 500k – Ngay dưới biên = 499.999 → 0%"""
        result = call(499_999)
        assert result["discount_percent"] == 0
        assert result["final_price"] == 499_999

    def test_BVA04_min_bien_500k(self):
        """BVA-04: min biên 500k – Tại biên = 500.000 → 5%"""
        result = call(500_000)
        assert result["discount_percent"] == 5
        assert result["final_price"] == 475_000  # 500.000 * 0.95

    def test_BVA05_min_plus_bien_500k(self):
        """BVA-05: min+ biên 500k – Ngay trên biên = 500.001 → 5%"""
        result = call(500_001)
        assert result["discount_percent"] == 5
        assert result["final_price"] == 475_001  # 500.001 - floor(500.001 * 5/100) = 475.001


class TestBVA_Boundary2M:
    """Ngưỡng biên 2.000.000 – ranh giới giữa Miền 2 (5%) và Miền 3 (10%)."""

    def test_BVA06_nom_vung2(self):
        """BVA-06: nom vùng 2 – Giá trị thông thường = 1.250.000 → 5%"""
        result = call(1_250_000)
        assert result["discount_percent"] == 5
        assert result["final_price"] == 1_187_500  # 1.250.000 * 0.95

    def test_BVA07_max_minus_bien_2tr(self):
        """BVA-07: max- biên 2tr – Ngay dưới biên = 1.999.999 → 5%"""
        result = call(1_999_999)
        assert result["discount_percent"] == 5
        # 1.999.999 - floor(1.999.999 * 5 / 100) = 1.999.999 - 99.999 = 1.900.000
        assert result["final_price"] == 1_900_000

    def test_BVA08_max_bien_2tr(self):
        """BVA-08: max biên 2tr – Tại biên trên vùng 2 = 2.000.000 → 5%"""
        result = call(2_000_000)
        assert result["discount_percent"] == 5
        assert result["final_price"] == 1_900_000  # 2.000.000 * 0.95

    def test_BVA09_min_vung3(self):
        """BVA-09: min vùng 3 – Ngay trên biên = 2.000.001 → 10%"""
        result = call(2_000_001)
        assert result["discount_percent"] == 10
        # 2.000.001 - floor(2.000.001 * 10 / 100) = 2.000.001 - 200.000 = 1.800.001
        assert result["final_price"] == 1_800_001

    def test_BVA10_min_plus_vung3(self):
        """BVA-10: min+ vùng 3 = 2.000.002 → 10%"""
        result = call(2_000_002)
        assert result["discount_percent"] == 10
        assert result["final_price"] == 1_800_002  # 2.000.002 - floor(2.000.002 * 10/100) = 1.800.002


class TestBVA_BoundaryOverall:
    """Biên min/max tổng thể của miền xác định [0, 50.000.000]."""

    def test_BVA11_nom_vung3(self):
        """BVA-11: nom vùng 3 – Giá trị thông thường = 25.000.000 → 10%"""
        result = call(25_000_000)
        assert result["discount_percent"] == 10
        assert result["final_price"] == 22_500_000  # 25.000.000 * 0.90

    def test_BVA12_max_minus(self):
        """BVA-12: max- – Cận biên trên = 49.999.999 → 10%"""
        result = call(49_999_999)
        assert result["discount_percent"] == 10
        # 49.999.999 - floor(49.999.999 * 10 / 100) = 49.999.999 - 4.999.999 = 45.000.000
        assert result["final_price"] == 45_000_000

    def test_BVA13_max(self):
        """BVA-13: max – Biên trên tổng thể = 50.000.000 → 10%"""
        result = call(50_000_000)
        assert result["discount_percent"] == 10
        assert result["final_price"] == 45_000_000  # 50.000.000 * 0.90


# ============================================================
# BVA MẠNH (Robust BVA) – 2 ca kiểm thử bổ sung
# ============================================================

class TestBVA_Robust:
    """Kiểm tra tính hợp lệ đầu vào bằng giá trị ngoài miền (min-, max+)."""

    def test_BVA_R1_min_minus(self):
        """BVA-R1: min- – Giá trị âm = -1 → Error"""
        result = call(-1)
        assert result["error"] is True
        assert "âm" in result["message"] or "order_value" in result["message"]

    def test_BVA_R2_max_plus(self):
        """BVA-R2: max+ – Vượt biên trên = 50.000.001 → Error"""
        result = call(50_000_001)
        assert result["error"] is True
        assert "vượt" in result["message"] or "50" in result["message"]
