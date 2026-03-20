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
# R1' – R4': HẠNG KIM CƯƠNG (C1=T, C2=–)
# ============================================================

class TestDT_KimCuong:
    """Rules R1'–R4': Hạng Kim cương, C2 là Indifferent (–)."""

    def test_DT01_R1_kimcuong_tienmat_thuong(self):
        """
        DT-01 | R1': C1=T, C2=–, C3=F, C4=F
        Kim cương + Tiền mặt + Giờ thường
        Discount: 10% (base) + 5% (E1) = 15%, Freeship: No
        """
        result = calculate_promotion(ORDER, "Kim cương", "Tiền mặt", False)
        assert result["discount_percent"] == 15
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(15)

    def test_DT02_R2_kimcuong_tienmat_flash(self):
        """
        DT-02 | R2': C1=T, C2=–, C3=F, C4=T
        Kim cương + Tiền mặt + Flash Sale
        Discount: 10% + 5% (E1) + 5% (E4) = 20%, Freeship: No
        """
        result = calculate_promotion(ORDER, "Kim cương", "Tiền mặt", True)
        assert result["discount_percent"] == 20
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(20)

    def test_DT03_R3_kimcuong_vi_thuong(self):
        """
        DT-03 | R3': C1=T, C2=–, C3=T, C4=F
        Kim cương + Ví điện tử + Giờ thường
        Discount: 10% + 5% (E1) + 2% (E3) = 17%, Freeship: Yes (E5)
        """
        result = calculate_promotion(ORDER, "Kim cương", "Ví điện tử", False)
        assert result["discount_percent"] == 17
        assert result["freeship"] is True
        assert result["final_price"] == expected_final(17)

    def test_DT04_R4_kimcuong_vi_flash(self):
        """
        DT-04 | R4': C1=T, C2=–, C3=T, C4=T
        Kim cương + Ví điện tử + Flash Sale
        Discount: 10% + 5% (E1) + 2% (E3) + 5% (E4) = 22%, Freeship: Yes (E5)
        """
        result = calculate_promotion(ORDER, "Kim cương", "Ví điện tử", True)
        assert result["discount_percent"] == 22
        assert result["freeship"] is True
        assert result["final_price"] == expected_final(22)


# ============================================================
# R5' – R8': HẠNG VÀNG (C1=F, C2=T)
# ============================================================

class TestDT_Vang:
    """Rules R5'–R8': Hạng Vàng."""

    def test_DT05_R5_vang_tienmat_thuong(self):
        """
        DT-05 | R5': C1=F, C2=T, C3=F, C4=F
        Vàng + Tiền mặt + Giờ thường
        Discount: 10% + 3% (E2) = 13%, Freeship: No
        """
        result = calculate_promotion(ORDER, "Vàng", "Tiền mặt", False)
        assert result["discount_percent"] == 13
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(13)

    def test_DT06_R6_vang_tienmat_flash(self):
        """
        DT-06 | R6': C1=F, C2=T, C3=F, C4=T
        Vàng + Tiền mặt + Flash Sale
        Discount: 10% + 3% (E2) + 5% (E4) = 18%, Freeship: No
        """
        result = calculate_promotion(ORDER, "Vàng", "Tiền mặt", True)
        assert result["discount_percent"] == 18
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(18)

    def test_DT07_R7_vang_vi_thuong(self):
        """
        DT-07 | R7': C1=F, C2=T, C3=T, C4=F
        Vàng + Ví điện tử + Giờ thường
        Discount: 10% + 3% (E2) + 2% (E3) = 15%, Freeship: No
        """
        result = calculate_promotion(ORDER, "Vàng", "Ví điện tử", False)
        assert result["discount_percent"] == 15
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(15)

    def test_DT08_R8_vang_vi_flash(self):
        """
        DT-08 | R8': C1=F, C2=T, C3=T, C4=T
        Vàng + Ví điện tử + Flash Sale
        Discount: 10% + 3% (E2) + 2% (E3) + 5% (E4) = 20%, Freeship: No
        """
        result = calculate_promotion(ORDER, "Vàng", "Ví điện tử", True)
        assert result["discount_percent"] == 20
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(20)


# ============================================================
# R9' – R10': HẠNG BẠC (C1=F, C2=F, C4=–)
# ============================================================

class TestDT_Bac:
    """Rules R9'–R10': Hạng Bạc, C4 là Indifferent (–)."""

    def test_DT09_R9_bac_tienmat(self):
        """
        DT-09 | R9': C1=F, C2=F, C3=F, C4=–
        Bạc + Tiền mặt + (không quan tâm Flash Sale)
        Discount: 10% + 0% = 10%, Freeship: No
        Chọn C4=F làm đại diện.
        """
        result = calculate_promotion(ORDER, "Bạc", "Tiền mặt", False)
        assert result["discount_percent"] == 10
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(10)

    def test_DT10_R10_bac_vi(self):
        """
        DT-10 | R10': C1=F, C2=F, C3=T, C4=–
        Bạc + Ví điện tử + (không quan tâm Flash Sale)
        Discount: 10% + 2% (E3) = 12%, Freeship: No
        Chọn C4=F làm đại diện.
        """
        result = calculate_promotion(ORDER, "Bạc", "Ví điện tử", False)
        assert result["discount_percent"] == 12
        assert result["freeship"] is False
        assert result["final_price"] == expected_final(12)


# ============================================================
# BỔ SUNG: KIỂM TRA ĐẦU VÀO KHÔNG HỢP LỆ
# ============================================================

class TestDT_Invalid:
    """Ca kiểm thử đầu vào không hợp lệ."""

    def test_DT11_invalid_tier(self):
        """DT-11 | Hạng thành viên không tồn tại → Error"""
        result = calculate_promotion(ORDER, "Platinum", "Tiền mặt", False)
        assert result["error"] is True

    def test_DT12_invalid_payment(self):
        """DT-12 | Phương thức thanh toán không hợp lệ → Error"""
        result = calculate_promotion(ORDER, "Bạc", "Bitcoin", False)
        assert result["error"] is True

    def test_DT13_invalid_flash_sale(self):
        """DT-13 | is_flash_sale không phải bool → Error"""
        result = calculate_promotion(ORDER, "Bạc", "Tiền mặt", "yes")
        assert result["error"] is True
