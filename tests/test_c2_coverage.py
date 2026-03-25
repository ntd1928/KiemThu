import pytest
from src.promotion import calculate_promotion

def test_tc01_invalid_order_value_type():
    # D1-True
    result = calculate_promotion(500.5, "Bạc", "Tiền mặt", False)
    assert result.get("error") is True
    assert "phải là số nguyên" in result["message"]

def test_tc02_negative_order_value():
    # D1-False, D2-True
    result = calculate_promotion(-1, "Bạc", "Tiền mặt", False)
    assert result.get("error") is True
    assert "không được âm" in result["message"]

def test_tc03_exceeds_max_order_value():
    # D2-False, D3-True
    result = calculate_promotion(60_000_000, "Bạc", "Tiền mặt", False)
    assert result.get("error") is True
    assert "vượt quá" in result["message"]

def test_tc04_invalid_member_tier():
    # D3-False, D4-True
    result = calculate_promotion(100_000, "Đồng", "Tiền mặt", False)
    assert result.get("error") is True
    assert "member_tier không hợp lệ" in result["message"]

def test_tc05_invalid_payment_method():
    # D4-False, D5-True
    result = calculate_promotion(100_000, "Bạc", "Bitcoin", False)
    assert result.get("error") is True
    assert "payment_method không hợp lệ" in result["message"]

def test_tc06_invalid_flash_sale_type():
    # D5-False, D6-True
    result = calculate_promotion(100_000, "Bạc", "Tiền mặt", "Yes")
    assert result.get("error") is True
    assert "is_flash_sale phải là bool" in result["message"]

def test_tc07_minimum_value_no_discount():
    # D7-True, D9-False, D10-False, D12-False
    result = calculate_promotion(300_000, "Bạc", "Chuyển khoản", False)
    assert result.get("error") is None
    assert result["discount_percent"] == 0
    assert result["freeship"] is False
    assert result["final_price"] == 300_000

def test_tc08_mid_value_with_ewallet():
    # D7-False, D8-True, D9-True, D12-False
    result = calculate_promotion(1_000_000, "Vàng", "Ví điện tử", False)
    assert result.get("error") is None
    assert result["discount_percent"] == 10
    assert result["freeship"] is False
    assert result["final_price"] == 900_000

def test_tc09_high_value_with_flash_sale_and_freeship():
    # D8-False, D10-True, D12-True
    result = calculate_promotion(3_000_000, "Kim cương", "Ví điện tử", True)
    assert result.get("error") is None
    assert result["discount_percent"] == 22
    assert result["freeship"] is True
    assert result["final_price"] == 2_340_000
    assert "Miễn phí vận chuyển" in result["message"]

def test_tc10_max_discount_cap():
    # D11-True
    result = calculate_promotion(3_000_000, "VIP", "Ví điện tử", True)
    assert result.get("error") is None
    assert result["discount_percent"] == 25
    assert result["freeship"] is False
    assert result["final_price"] == 2_250_000
    assert "Giảm 25%" in result["message"]
