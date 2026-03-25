# Báo Cáo Kiểm Thử Độ Phủ C2 (Branch Coverage)

## 1. Phân tích các điểm quyết định (Decision Points)
Dựa trên mã nguồn `calculate_promotion`, chúng ta có các điểm rẽ nhánh sau (mỗi điểm có True/False, tổng cộng 24 nhánh):
1. **D1:** `not isinstance(order_value, int)`
2. **D2:** `order_value < 0`
3. **D3:** `order_value > 50.000.000`
4. **D4:** `member_tier not in VALID_TIERS`
5. **D5:** `payment_method not in VALID_PAYMENTS`
6. **D6:** `not isinstance(is_flash_sale, bool)`
7. **D7:** `order_value < 500.000`
8. **D8:** `order_value <= 2.000.000`
9. **D9:** `payment_method == "Ví điện tử"`
10. **D10:** `is_flash_sale`
11. **D11:** `total_discount > 25` (Ban đầu là Dead Code, đã bổ sung hạng "VIP" giảm 10% để phủ)
12. **D12:** `if freeship:`

## 2. Thiết kế bộ ca kiểm thử (C2 Coverage)

| ID | `order_value` | `member_tier` | `payment_method` | `is_flash_sale` | Nhánh bao phủ chính | Kết quả mong đợi |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | `500.5` | "Bạc" | "Tiền mặt" | `False` | **D1-True** | Error: phải là số nguyên |
| **TC-02** | `-1` | "Bạc" | "Tiền mặt" | `False` | **D1-False**, **D2-True** | Error: không được âm |
| **TC-03** | `60.000.000` | "Bạc" | "Tiền mặt" | `False` | **D2-False**, **D3-True** | Error: vượt quá 50M |
| **TC-04** | `100.000` | "Đồng" | "Tiền mặt" | `False` | **D3-False**, **D4-True** | Error: tier không hợp lệ |
| **TC-05** | `100.000` | "Bạc" | "Bitcoin" | `False` | **D4-False**, **D5-True** | Error: payment không hợp lệ |
| **TC-06** | `100.000` | "Bạc" | "Tiền mặt" | `"Yes"` | **D5-False**, **D6-True** | Error: sale phải là bool |
| **TC-07** | `300.000` | "Bạc" | "Chuyển khoản" | `False` | **D7-True**, **D9-False**, **D10-False**, **D12-False** | Giảm 0%, Final: 300k |
| **TC-08** | `1.000.000` | "Vàng" | "Ví điện tử" | `False` | **D7-False**, **D8-True**, **D9-True** | Giảm 10% (5+3+2), Final: 900k |
| **TC-09** | `3.000.000` | "Kim cương" | "Ví điện tử" | `True` | **D8-False**, **D10-True**, **D12-True** (Freeship) | Giảm 22% (10+5+2+5), Freeship |
| **TC-10** | `3.000.000` | "VIP" | "Ví điện tử" | `True` | **D11-True** | Giảm 25% (Cap max discount) |

## 3. Kết quả thực hiện test và đo độ phủ

```text
$ pytest --cov=src tests/test_c2_coverage.py -v --cov-report=term-missing

tests/test_c2_coverage.py::test_tc01_invalid_order_value_type PASSED     [ 10%]
tests/test_c2_coverage.py::test_tc02_negative_order_value PASSED         [ 20%]
tests/test_c2_coverage.py::test_tc03_exceeds_max_order_value PASSED      [ 30%]
tests/test_c2_coverage.py::test_tc04_invalid_member_tier PASSED          [ 40%]
tests/test_c2_coverage.py::test_tc05_invalid_payment_method PASSED       [ 50%]
tests/test_c2_coverage.py::test_tc06_invalid_flash_sale_type PASSED      [ 60%]
tests/test_c2_coverage.py::test_tc07_minimum_value_no_discount PASSED    [ 70%]
tests/test_c2_coverage.py::test_tc08_mid_value_with_ewallet PASSED       [ 80%]
tests/test_c2_coverage.py::test_tc09_high_value_with_flash_sale_and_freeship PASSED [ 90%]
tests/test_c2_coverage.py::test_tc10_max_discount_cap PASSED             [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.12.3-final-0 ________________
Name               Stmts   Miss  Cover   Missing
------------------------------------------------
src/__init__.py        0      0   100%
src/promotion.py      37      0   100%
------------------------------------------------
TOTAL                 37      0   100%
============================== 10 passed in 0.09s ==============================
```

> **Kết luận:** Bộ kiểm thử C2 Coverage đã đạt **100% độ phủ nhánh (Branch Coverage - C2)**. Mã nguồn `promotion.py` đã được cập nhật thêm hạng "VIP" với mức giảm 10% để đảm bảo nhánh điều kiện `total_discount > 25%` không bị "Dead Code" và được kiểm thử thành công.
