# BÁO CÁO BÀI TẬP LỚN
## Môn: Kiểm thử phần mềm
## Đề tài: Kiểm thử Hệ thống Khuyến mại (Promotional Module)

---

## 1. Giới thiệu bài toán

Hệ thống Khuyến mại tính toán mức giảm giá và phí vận chuyển cho đơn hàng dựa trên **4 biến đầu vào**:

| Biến | Kiểu | Miền xác định |
|------|------|---------------|
| `order_value` – Tổng giá trị đơn hàng (VNĐ) | `int` | 0 ≤ X ≤ 50.000.000 |
| `member_tier` – Hạng thành viên | `str` | {Bạc, Vàng, Kim cương} |
| `payment_method` – Phương thức thanh toán | `str` | {Tiền mặt, Ví điện tử, Chuyển khoản} |
| `is_flash_sale` – Thời điểm mua | `bool` | True (Flash Sale) / False (Giờ thường) |

### Quy tắc nghiệp vụ

| Rule | Mô tả | Chi tiết |
|------|--------|----------|
| R1 | Giảm giá theo giá trị đơn hàng | < 500k → 0%, 500k–2tr → 5%, > 2tr → 10% |
| R2 | Giảm thêm theo hạng thành viên | Bạc: +0%, Vàng: +3%, Kim cương: +5% |
| R3 | Giảm thêm khi dùng Ví điện tử | +2% |
| R4 | Giảm thêm khi Flash Sale | +5% |
| R5 | Freeship | Khi: X ≥ 2tr **VÀ** Kim cương **VÀ** Ví điện tử |
| R6 | Giới hạn tối đa | Tổng giảm ≤ 25% |

### Đầu ra

```json
{
  "discount_percent": 15,
  "freeship": true,
  "final_price": 2550000,
  "message": "Giảm 15%, Miễn phí vận chuyển"
}
```

Nếu đầu vào không hợp lệ → `{"error": true, "message": "..."}`.

---

## 2. Thiết kế ca kiểm thử

### 2.1. Kiểm thử giá trị biên (Boundary Value Analysis – BVA)

#### Cơ sở lý thuyết

- **Giả thiết khiếm khuyết đơn:** Lỗi thường xảy ra do một sai sót đơn lẻ tại ranh giới của miền dữ liệu.
- **Chiến lược 5 điểm:** Với mỗi ngưỡng biên, lấy 5 giá trị: **min, min+, nom, max-, max**.
- **Công thức:** BVA thường: **4n + 1** ca kiểm thử; BVA mạnh: **6n + 1** (bổ sung min-, max+).

#### Biến kiểm thử

- **Biến thay đổi:** `order_value` (biến liên tục, có 2 ngưỡng nội bộ: 500.000 và 2.000.000)
- **Biến cố định:** `member_tier="Bạc"`, `payment_method="Tiền mặt"`, `is_flash_sale=False`
  - → Chỉ có R1 tác động, loại bỏ ảnh hưởng của R2, R3, R4.

#### Phân hoạch miền con

| Miền | Khoảng giá trị | Expected discount |
|------|----------------|-------------------|
| Miền 1 | [0, 499.999] | 0% |
| Miền 2 | [500.000, 2.000.000] | 5% |
| Miền 3 | [2.000.001, 50.000.000] | 10% |

#### Bảng ca kiểm thử BVA

**Ngưỡng biên 1: Ranh giới 500.000**

| ID | Giá trị order_value | Loại điểm | Expected discount | Expected final_price |
|----|---------------------|-----------|-------------------|---------------------|
| BVA-01 | 0 | min | 0% | 0 |
| BVA-02 | 250.000 | nom (vùng 1) | 0% | 250.000 |
| BVA-03 | 499.999 | max- (biên 500k) | 0% | 499.999 |
| BVA-04 | 500.000 | min (biên 500k) | 5% | 475.000 |
| BVA-05 | 500.001 | min+ (biên 500k) | 5% | 475.001 |

**Ngưỡng biên 2: Ranh giới 2.000.000**

| ID | Giá trị order_value | Loại điểm | Expected discount | Expected final_price |
|----|---------------------|-----------|-------------------|---------------------|
| BVA-06 | 1.250.000 | nom (vùng 2) | 5% | 1.187.500 |
| BVA-07 | 1.999.999 | max- (biên 2tr) | 5% | 1.900.000 |
| BVA-08 | 2.000.000 | max (biên 2tr) | 5% | 1.900.000 |
| BVA-09 | 2.000.001 | min (vùng 3) | 10% | 1.800.001 |
| BVA-10 | 2.000.002 | min+ (vùng 3) | 10% | 1.800.002 |

**Ngưỡng biên 3: Biên min/max tổng thể**

| ID | Giá trị order_value | Loại điểm | Expected discount | Expected final_price |
|----|---------------------|-----------|-------------------|---------------------|
| BVA-11 | 25.000.000 | nom (vùng 3) | 10% | 22.500.000 |
| BVA-12 | 49.999.999 | max- | 10% | 45.000.000 |
| BVA-13 | 50.000.000 | max | 10% | 45.000.000 |

**BVA mạnh – Giá trị ngoài miền**

| ID | Giá trị order_value | Loại điểm | Expected |
|----|---------------------|-----------|----------|
| BVA-R1 | -1 | min- | Error |
| BVA-R2 | 50.000.001 | max+ | Error |

**Tổng: 15 ca kiểm thử BVA**

---

### 2.2. Kiểm thử bảng quyết định (Decision Table Testing)

#### Cơ sở lý thuyết

- Bảng quyết định phù hợp khi các biến đầu vào **phụ thuộc lẫn nhau** trong việc xác định đầu ra.
- Cấu trúc bảng gồm 4 phần: Điều kiện, Giá trị điều kiện (T/F), Hành động, Trạng thái xảy ra hành động.
- Mỗi cột (rule) trong bảng được chuyển thành một ca kiểm thử.

#### Quy trình 8 bước

**Bước 1-2: Xác định và liệt kê Điều kiện & Hành động**

Cố định `order_value = 3.000.000` (R1 = 10% giảm giá cơ bản).

| Ký hiệu | Điều kiện |
|----------|-----------|
| C1 | Hạng thành viên = Kim cương? |
| C2 | Phương thức thanh toán = Ví điện tử? |
| C3 | Thời điểm = Flash Sale? |

| Ký hiệu | Hành động |
|----------|-----------|
| A1 | Cộng thêm 5% giảm giá (Kim cương) |
| A2 | Cộng thêm 2% giảm giá (Ví điện tử) |
| A3 | Cộng thêm 5% giảm giá (Flash Sale) |
| A4 | Miễn phí vận chuyển (Freeship) |

**Bước 3: Tính số tổ hợp**

3 điều kiện nhị phân → 2³ = **8 rules**

**Bước 4-7: Điền giá trị, kiểm tra gộp cột, thêm hành động**

| | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **C1: Kim cương?** | F | F | F | F | T | T | T | T |
| **C2: Ví điện tử?** | F | F | T | T | F | F | T | T |
| **C3: Flash Sale?** | F | T | F | T | F | T | F | T |
| | | | | | | | | |
| **A1: +5% (KC)** | | | | | ✓ | ✓ | ✓ | ✓ |
| **A2: +2% (VĐT)** | | | ✓ | ✓ | | | ✓ | ✓ |
| **A3: +5% (FS)** | | ✓ | | ✓ | | ✓ | | ✓ |
| **A4: Freeship** | | | | | | | ✓ | ✓ |
| **Tổng % giảm** | 10% | 15% | 12% | 17% | 15% | 20% | 17% | 22% |

> **Kiểm tra gộp cột (Indifferent):** A4 (Freeship) phụ thuộc C1 và C2 nhưng không C3 → có thể gộp R7+R8 cho hành động A4. Tuy nhiên % giảm giá khác nhau nên giữ nguyên 8 rules để đảm bảo tính chính xác.

**Bước 8: Chuyển thành ca kiểm thử**

| TC-ID | order_value | member_tier | payment_method | is_flash_sale | Expected discount | Expected freeship | Expected final_price |
|-------|:-----------:|:-----------:|:--------------:|:-------------:|:-----------------:|:-----------------:|:--------------------:|
| DT-01 | 3.000.000 | Bạc | Tiền mặt | False | 10% | No | 2.700.000 |
| DT-02 | 3.000.000 | Bạc | Tiền mặt | True | 15% | No | 2.550.000 |
| DT-03 | 3.000.000 | Bạc | Ví điện tử | False | 12% | No | 2.640.000 |
| DT-04 | 3.000.000 | Bạc | Ví điện tử | True | 17% | No | 2.490.000 |
| DT-05 | 3.000.000 | Kim cương | Tiền mặt | False | 15% | No | 2.550.000 |
| DT-06 | 3.000.000 | Kim cương | Tiền mặt | True | 20% | No | 2.400.000 |
| DT-07 | 3.000.000 | Kim cương | Ví điện tử | False | 17% | Yes | 2.490.000 |
| DT-08 | 3.000.000 | Kim cương | Ví điện tử | True | 22% | Yes | 2.340.000 |

**Bổ sung – Hạng Vàng (coverage R2):**

| TC-ID | order_value | member_tier | payment_method | is_flash_sale | Expected discount | Expected freeship | Expected final_price |
|-------|:-----------:|:-----------:|:--------------:|:-------------:|:-----------------:|:-----------------:|:--------------------:|
| DT-09 | 3.000.000 | Vàng | Tiền mặt | False | 13% | No | 2.610.000 |
| DT-10 | 3.000.000 | Vàng | Ví điện tử | True | 20% | No | 2.400.000 |

**Tổng: 10 ca kiểm thử Decision Table** (+ 4 ca kiểm thử đầu vào không hợp lệ)

---

## 3. Kết quả thực hiện

### Chạy test

```
$ python -m pytest test_boundary.py test_decision_table.py -v

=========== test session starts ===========
collected 29 items

test_boundary.py::TestBVA_Boundary500k::test_BVA01_min_gia_tri_nho_nhat    PASSED
test_boundary.py::TestBVA_Boundary500k::test_BVA02_nom_vung1              PASSED
test_boundary.py::TestBVA_Boundary500k::test_BVA03_max_minus_bien_500k    PASSED
test_boundary.py::TestBVA_Boundary500k::test_BVA04_min_bien_500k          PASSED
test_boundary.py::TestBVA_Boundary500k::test_BVA05_min_plus_bien_500k     PASSED
test_boundary.py::TestBVA_Boundary2M::test_BVA06_nom_vung2                PASSED
test_boundary.py::TestBVA_Boundary2M::test_BVA07_max_minus_bien_2tr       PASSED
test_boundary.py::TestBVA_Boundary2M::test_BVA08_max_bien_2tr             PASSED
test_boundary.py::TestBVA_Boundary2M::test_BVA09_min_vung3                PASSED
test_boundary.py::TestBVA_Boundary2M::test_BVA10_min_plus_vung3           PASSED
test_boundary.py::TestBVA_BoundaryOverall::test_BVA11_nom_vung3           PASSED
test_boundary.py::TestBVA_BoundaryOverall::test_BVA12_max_minus           PASSED
test_boundary.py::TestBVA_BoundaryOverall::test_BVA13_max                 PASSED
test_boundary.py::TestBVA_Robust::test_BVA_R1_min_minus                   PASSED
test_boundary.py::TestBVA_Robust::test_BVA_R2_max_plus                    PASSED
test_decision_table.py::TestDecisionTable_8Rules::test_DT01_R1_bac_tienmat_thuong          PASSED
test_decision_table.py::TestDecisionTable_8Rules::test_DT02_R2_bac_tienmat_flash           PASSED
test_decision_table.py::TestDecisionTable_8Rules::test_DT03_R3_bac_vi_thuong               PASSED
test_decision_table.py::TestDecisionTable_8Rules::test_DT04_R4_bac_vi_flash                PASSED
test_decision_table.py::TestDecisionTable_8Rules::test_DT05_R5_kimcuong_tienmat_thuong     PASSED
test_decision_table.py::TestDecisionTable_8Rules::test_DT06_R6_kimcuong_tienmat_flash      PASSED
test_decision_table.py::TestDecisionTable_8Rules::test_DT07_R7_kimcuong_vi_thuong          PASSED
test_decision_table.py::TestDecisionTable_8Rules::test_DT08_R8_kimcuong_vi_flash           PASSED
test_decision_table.py::TestDecisionTable_Vang::test_DT09_vang_tienmat_thuong              PASSED
test_decision_table.py::TestDecisionTable_Vang::test_DT10_vang_vi_flash                    PASSED
test_decision_table.py::TestDecisionTable_Cap25::test_DT11_cap25_scenario                  PASSED
test_decision_table.py::TestDecisionTable_InvalidInput::test_DT12_invalid_tier             PASSED
test_decision_table.py::TestDecisionTable_InvalidInput::test_DT13_invalid_payment          PASSED
test_decision_table.py::TestDecisionTable_InvalidInput::test_DT14_invalid_flash_sale       PASSED

=========== 29 passed in 0.05s ============
```

### Bảng so sánh Expected vs Actual

| TC-ID | Expected Result | Actual Result | Pass/Fail |
|-------|:---------------:|:-------------:|:---------:|
| BVA-01 → BVA-13 | Xem bảng mục 2.1 | Khớp | ✅ PASS |
| BVA-R1, BVA-R2 | Error | Error | ✅ PASS |
| DT-01 → DT-10 | Xem bảng mục 2.2 | Khớp | ✅ PASS |
| DT-11 (cap 25%) | 22% ≤ 25% | 22% | ✅ PASS |
| DT-12 → DT-14 | Error | Error | ✅ PASS |

**Kết quả: 29/29 ca kiểm thử PASS (100%)**

---

## 4. Cấu trúc mã nguồn

```
Kiemthu/
├── promotion.py            # Module tính khuyến mại
├── test_boundary.py        # 15 ca kiểm thử BVA
├── test_decision_table.py  # 14 ca kiểm thử Decision Table
├── report.md               # Báo cáo (file này)
└── README.md               # Hướng dẫn sử dụng
```

## 5. Link GitHub

> **Repository:** [https://github.com/ntd1928/KiemThu](https://github.com/ntd1928/KiemThu)
