"""
Kiểm thử bảng quyết định (Decision Table Testing)
===================================================
Cố định: order_value = 3.000.000 (R1 = 10% giảm giá cơ bản)

3 Điều kiện (nhị phân):
  C1: Hạng thành viên = Kim cương?  (T → +5%, F → Bạc +0%)
  C2: Phương thức thanh toán = Ví điện tử?  (T → +2%, F → Tiền mặt +0%)
  C3: Thời điểm = Flash Sale?  (T → +5%, F → +0%)

4 Hành động:
  A1: Cộng thêm 5% (Kim cương)
  A2: Cộng thêm 2% (Ví điện tử)
  A3: Cộng thêm 5% (Flash Sale)
  A4: Miễn phí vận chuyển (Freeship) – khi C1=T VÀ C2=T VÀ order≥2tr

Bảng quyết định đầy đủ (2³ = 8 rules):
┌──────────────────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│                  │ R1  │ R2  │ R3  │ R4  │ R5  │ R6  │ R7  │ R8  │
├──────────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│ C1: Kim cương?   │  F  │  F  │  F  │  F  │  T  │  T  │  T  │  T  │
│ C2: Ví điện tử?  │  F  │  F  │  T  │  T  │  F  │  F  │  T  │  T  │
│ C3: Flash Sale?  │  F  │  T  │  F  │  T  │  F  │  T  │  F  │  T  │
├──────────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│ A1: +5% (KC)     │     │     │     │     │  ✓  │  ✓  │  ✓  │  ✓  │
│ A2: +2% (VĐT)    │     │     │  ✓  │  ✓  │     │     │  ✓  │  ✓  │
│ A3: +5% (FS)     │     │  ✓  │     │  ✓  │     │  ✓  │     │  ✓  │
│ A4: Freeship     │     │     │     │     │     │     │  ✓  │  ✓  │
├──────────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│ Tổng % giảm      │ 10% │ 15% │ 12% │ 17% │ 15% │ 20% │ 17% │ 22% │
└──────────────────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘

Bổ sung: 2 ca kiểm thử cho hạng Vàng (+3%) để đảm bảo phủ R2.
Tổng: 10 ca kiểm thử.
"""

import pytest
from promotion import calculate_promotion

# ============================================================
# Giá trị cố định
# ============================================================
ORDER = 3_000_000  # R1 = 10% giảm giá cơ bản


def expected_final(discount_percent):
    """Tính giá cuối cùng dựa trên % giảm giá."""
    return ORDER - (ORDER * discount_percent // 100)


# ============================================================
# 8 RULES TỪ BẢNG QUYẾT ĐỊNH
# ============================================================

class TestDecisionTable_8Rules:
    """8 ca kiểm thử tương ứng 8 rules từ bảng quyết định."""

    def test_DT01_R1_bac_tienmat_thuong(self):
        """
        DT-01 | Rule 1: C1=F, C2=F, C3=F
        Bạc + Tiền mặt + Giờ thường → 10% + 0 + 0 + 0 = 10%, No freeship
        """
        result = calculate_promotion(ORDER, "Bạc", "Tiền mặt", False)
        assert result["discount_percent"] == 10
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(10)

    def test_DT02_R2_bac_tienmat_flash(self):
        """
        DT-02 | Rule 2: C1=F, C2=F, C3=T
        Bạc + Tiền mặt + Flash Sale → 10% + 0 + 0 + 5 = 15%, No freeship
        """
        result = calculate_promotion(ORDER, "Bạc", "Tiền mặt", True)
        assert result["discount_percent"] == 15
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(15)

    def test_DT03_R3_bac_vi_thuong(self):
        """
        DT-03 | Rule 3: C1=F, C2=T, C3=F
        Bạc + Ví điện tử + Giờ thường → 10% + 0 + 2 + 0 = 12%, No freeship
        """
        result = calculate_promotion(ORDER, "Bạc", "Ví điện tử", False)
        assert result["discount_percent"] == 12
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(12)

    def test_DT04_R4_bac_vi_flash(self):
        """
        DT-04 | Rule 4: C1=F, C2=T, C3=T
        Bạc + Ví điện tử + Flash Sale → 10% + 0 + 2 + 5 = 17%, No freeship
        """
        result = calculate_promotion(ORDER, "Bạc", "Ví điện tử", True)
        assert result["discount_percent"] == 17
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(17)

    def test_DT05_R5_kimcuong_tienmat_thuong(self):
        """
        DT-05 | Rule 5: C1=T, C2=F, C3=F
        Kim cương + Tiền mặt + Giờ thường → 10% + 5 + 0 + 0 = 15%, No freeship
        """
        result = calculate_promotion(ORDER, "Kim cương", "Tiền mặt", False)
        assert result["discount_percent"] == 15
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(15)

    def test_DT06_R6_kimcuong_tienmat_flash(self):
        """
        DT-06 | Rule 6: C1=T, C2=F, C3=T
        Kim cương + Tiền mặt + Flash Sale → 10% + 5 + 0 + 5 = 20%, No freeship
        """
        result = calculate_promotion(ORDER, "Kim cương", "Tiền mặt", True)
        assert result["discount_percent"] == 20
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(20)

    def test_DT07_R7_kimcuong_vi_thuong(self):
        """
        DT-07 | Rule 7: C1=T, C2=T, C3=F
        Kim cương + Ví điện tử + Giờ thường → 10% + 5 + 2 + 0 = 17%, Freeship
        """
        result = calculate_promotion(ORDER, "Kim cương", "Ví điện tử", False)
        assert result["discount_percent"] == 17
        assert result["freeship"] is True
        assert result["final_price"] == expected_final(17)

    def test_DT08_R8_kimcuong_vi_flash(self):
        """
        DT-08 | Rule 8: C1=T, C2=T, C3=T
        Kim cương + Ví điện tử + Flash Sale → 10% + 5 + 2 + 5 = 22%, Freeship
        """
        result = calculate_promotion(ORDER, "Kim cương", "Ví điện tử", True)
        assert result["discount_percent"] == 22
        assert result["freeship"] is True
        assert result["final_price"] == expected_final(22)


# ============================================================
# BỔ SUNG: HẠNG VÀNG (+3%) – Coverage R2
# ============================================================

class TestDecisionTable_Vang:
    """Bổ sung ca kiểm thử cho hạng Vàng để phủ đầy đủ quy tắc R2."""

    def test_DT09_vang_tienmat_thuong(self):
        """
        DT-09 | Vàng + Tiền mặt + Giờ thường → 10% + 3 + 0 + 0 = 13%
        """
        result = calculate_promotion(ORDER, "Vàng", "Tiền mặt", False)
        assert result["discount_percent"] == 13
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(13)

    def test_DT10_vang_vi_flash(self):
        """
        DT-10 | Vàng + Ví điện tử + Flash Sale → 10% + 3 + 2 + 5 = 20%
        """
        result = calculate_promotion(ORDER, "Vàng", "Ví điện tử", True)
        assert result["discount_percent"] == 20
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(20)


# ============================================================
# BỔ SUNG: KIỂM TRA CAP 25% (R6)
# ============================================================

class TestDecisionTable_Cap25:
    """Kiểm tra giới hạn giảm giá tối đa 25% (R6)."""

    def test_DT11_cap25_scenario(self):
        """
        DT-11 | Tạo tình huống tổng giảm > 25%
        order_value=3.000.000 (10%) + Kim cương (5%) + Ví điện tử (2%) + Flash Sale (5%)
        = 22% → chưa bị cap (< 25%)

        Để test cap, thử một giá trị order ở mức 5% cơ bản nhưng cộng hết bonus:
        Thực tế với đặc tả hiện tại, max = 10+5+2+5 = 22% < 25%.
        Test này xác nhận rằng hệ thống KHÔNG cap khi tổng < 25%.
        """
        result = calculate_promotion(ORDER, "Kim cương", "Ví điện tử", True)
        assert result["discount_percent"] == 22
        assert result["discount_percent"] <= 25  # Không vượt cap


# ============================================================
# BỔ SUNG: KIỂM TRA ĐẦU VÀO KHÔNG HỢP LỆ
# ============================================================

class TestDecisionTable_InvalidInput:
    """Kiểm tra xử lý đầu vào không hợp lệ cho các biến phi số."""

    def test_DT12_invalid_tier(self):
        """DT-12 | Hạng thành viên không tồn tại → Error"""
        result = calculate_promotion(ORDER, "Platinum", "Tiền mặt", False)
        assert result["error"] is True

    def test_DT13_invalid_payment(self):
        """DT-13 | Phương thức thanh toán không hợp lệ → Error"""
        result = calculate_promotion(ORDER, "Bạc", "Bitcoin", False)
        assert result["error"] is True

    def test_DT14_invalid_flash_sale(self):
        """DT-14 | is_flash_sale không phải bool → Error"""
        result = calculate_promotion(ORDER, "Bạc", "Tiền mặt", "yes")
        assert result["error"] is True
