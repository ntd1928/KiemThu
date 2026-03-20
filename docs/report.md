# BÁO CÁO BÀI TẬP LỚN
## Bài toán: Kiểm thử Hệ thống Khuyến mại (Promotional Module)

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

#### 2.1.1. Cơ sở lý thuyết

- **Định nghĩa:** Kiểm thử giá trị biên là kỹ thuật kiểm thử hộp đen tập trung vào các giá trị tại ranh giới (biên) của miền dữ liệu đầu vào, nơi lỗi thường xảy ra nhiều nhất.
- **Giả thiết khiếm khuyết đơn (Single fault assumption):** Lỗi thường xảy ra do một sai sót đơn lẻ, không cần sự kết hợp của nhiều sai sót cùng lúc.
- **Chiến lược 5 điểm:** Với mỗi biến, lấy 5 giá trị đặc trưng: **min, min+, nom, max-, max**.
- **Công thức số ca kiểm thử:**
  - BVA thường (Normal BVA): **4n + 1** (n = số biến)
  - BVA mạnh (Robust BVA): **6n + 1** (bổ sung **min-** và **max+** nằm ngoài miền xác định)

#### 2.1.2. Xác định biến kiểm thử

- **Biến thay đổi:** `order_value` – biến liên tục với 3 miền con và 2 điểm biên nội bộ (500.000 và 2.000.000)
- **Biến cố định (giả thiết khiếm khuyết đơn):**
  - `member_tier = "Bạc"` → R2 = +0%
  - `payment_method = "Tiền mặt"` → R3 = +0%
  - `is_flash_sale = False` → R4 = +0%
  - → Chỉ có R1 (giảm theo giá trị đơn hàng) tác động đến kết quả.

#### 2.1.3. Phân hoạch miền con (Equivalence Partitioning)

Trước khi áp dụng BVA, cần phân hoạch miền dữ liệu thành các lớp tương đương:

| Miền | Khoảng giá trị | Mức giảm giá | Đặc điểm |
|------|----------------|-------------|----------|
| **Miền không hợp lệ (dưới)** | X < 0 | Error | Ngoài miền xác định |
| **Miền 1** (hợp lệ) | [0, 499.999] | 0% | Đơn hàng nhỏ |
| **Miền 2** (hợp lệ) | [500.000, 2.000.000] | 5% | Đơn hàng trung bình |
| **Miền 3** (hợp lệ) | [2.000.001, 50.000.000] | 10% | Đơn hàng lớn |
| **Miền không hợp lệ (trên)** | X > 50.000.000 | Error | Ngoài miền xác định |

**Kiểm tra tính đúng đắn phân hoạch:**
- Các miền con không chồng lấn (giao = ∅)
- Hợp các miền con = toàn bộ miền dữ liệu
- Không có miền con nào rỗng

#### 2.1.4. Xác định các điểm biên

Từ phân hoạch trên, xác định **4 điểm biên** của biến `order_value`:

| Điểm biên | Giá trị | Ý nghĩa |
|-----------|---------|---------|
| b₁ | 0 | Biên dưới tổng thể (min) |
| b₂ | 500.000 | Ranh giới Miền 1 ↔ Miền 2 |
| b₃ | 2.000.000 / 2.000.001 | Ranh giới Miền 2 ↔ Miền 3 |
| b₄ | 50.000.000 | Biên trên tổng thể (max) |

#### 2.1.5. Bảng ca kiểm thử BVA

**Bảng A – BVA thường (Normal BVA): 13 ca kiểm thử**

| ID | Giá trị | Loại điểm | Miền | Expected discount | Expected final_price | Giải thích |
|----|---------|-----------|------|:-----------------:|:--------------------:|------------|
| BVA-01 | 0 | **min** | Miền 1 | 0% | 0 | Giá trị nhỏ nhất hợp lệ |
| BVA-02 | 250.000 | **nom** | Miền 1 | 0% | 250.000 | Giá trị đại diện vùng 1 |
| BVA-03 | 499.999 | **max-** | Miền 1 | 0% | 499.999 | Ngay dưới biên b₂ |
| BVA-04 | 500.000 | **min** | Miền 2 | 5% | 475.000 | Tại biên b₂ (bắt đầu giảm 5%) |
| BVA-05 | 500.001 | **min+** | Miền 2 | 5% | 475.001 | Ngay trên biên b₂ |
| BVA-06 | 1.250.000 | **nom** | Miền 2 | 5% | 1.187.500 | Giá trị đại diện vùng 2 |
| BVA-07 | 1.999.999 | **max-** | Miền 2 | 5% | 1.900.000 | Ngay dưới biên b₃ |
| BVA-08 | 2.000.000 | **max** | Miền 2 | 5% | 1.900.000 | Tại biên b₃ (vẫn là 5%) |
| BVA-09 | 2.000.001 | **min** | Miền 3 | 10% | 1.800.001 | Ngay trên biên b₃ (chuyển sang 10%) |
| BVA-10 | 2.000.002 | **min+** | Miền 3 | 10% | 1.800.002 | Xác nhận vùng 3 |
| BVA-11 | 25.000.000 | **nom** | Miền 3 | 10% | 22.500.000 | Giá trị đại diện vùng 3 |
| BVA-12 | 49.999.999 | **max-** | Miền 3 | 10% | 45.000.000 | Cận biên trên tổng thể |
| BVA-13 | 50.000.000 | **max** | Miền 3 | 10% | 45.000.000 | Giá trị lớn nhất hợp lệ |

**Bảng B – BVA mạnh (Robust BVA): Bổ sung 2 ca kiểm thử ngoài miền**

| ID | Giá trị | Loại điểm | Expected | Giải thích |
|----|---------|-----------|----------|------------|
| BVA-R1 | -1 | **min-** | Error | Dưới biên dưới → kiểm tra validate |
| BVA-R2 | 50.000.001 | **max+** | Error | Trên biên trên → kiểm tra validate |

**Tổng cộng: 13 + 2 = 15 ca kiểm thử BVA**

---

### 2.2. Kiểm thử bảng quyết định (Decision Table Testing)

#### 2.2.1. Cơ sở lý thuyết

- **Định nghĩa:** Bảng quyết định là kỹ thuật kiểm thử hộp đen dùng khi đầu ra phụ thuộc vào sự kết hợp của nhiều điều kiện đầu vào.
- **Cấu trúc bảng:** Gồm 4 phần – Điều kiện (Conditions), Giá trị điều kiện (T/F/-), Hành động (Actions), Trạng thái hành động (✓).
- **Dấu "–" (Indifferent):** Điều kiện không ảnh hưởng đến hành động trong rule đó.
- **Mỗi cột (rule)** trong bảng cuối cùng được chuyển thành **một ca kiểm thử**.

#### 2.2.2. Quy trình 8 bước

##### Bước 1: Xác định các điều kiện và hành động

Cố định `order_value = 3.000.000` (thuộc Miền 3, R1 = 10% giảm giá cơ bản).

**Điều kiện:**

| Ký hiệu | Điều kiện | Giá trị |
|----------|-----------|---------|
| C1 | Hạng Kim cương? | T / F |
| C2 | Hạng Vàng? | T / F |
| C3 | Thanh toán bằng Ví điện tử? | T / F |
| C4 | Mua trong Flash Sale? | T / F |

*Ràng buộc: C1 và C2 không thể đồng thời True (loại bỏ tổ hợp bất khả thi).*
*Nếu C1=F và C2=F → Hạng Bạc.*

**Hành động:**

| Ký hiệu | Hành động |
|----------|-----------|
| E1 | Cộng thêm 5% giảm giá (Kim cương) |
| E2 | Cộng thêm 3% giảm giá (Vàng) |
| E3 | Cộng thêm 2% giảm giá (Ví điện tử) |
| E4 | Cộng thêm 5% giảm giá (Flash Sale) |
| E5 | Miễn phí vận chuyển (Freeship) |

##### Bước 2: Liệt kê vào bảng

Bảng cấu trúc gồm 4 điều kiện C1–C4, 5 hành động E1–E5, và các cột rule.

##### Bước 3: Tính số sự kết hợp

4 điều kiện nhị phân → 2⁴ = **16 tổ hợp**. Tuy nhiên C1=T ∧ C2=T là bất khả thi (không thể vừa Kim cương vừa Vàng) → loại bỏ 4 tổ hợp → còn **12 rules**.

##### Bước 4: Điền tất cả các sự kết hợp (Bảng đầy đủ)

| | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **C1: Kim cương?** | T | T | T | T | F | F | F | F | F | F | F | F |
| **C2: Vàng?** | F | F | F | F | T | T | T | T | F | F | F | F |
| **C3: Ví điện tử?** | F | F | T | T | F | F | T | T | F | F | T | T |
| **C4: Flash Sale?** | F | T | F | T | F | T | F | T | F | T | F | T |

##### Bước 5: Giảm bớt – Tìm sự kết hợp Indifferent (–)

Phân tích các hành động:
- **E1 (+5% KC):** Chỉ phụ thuộc C1=T → C2, C3, C4 đều **–** cho hành động này
- **E2 (+3% Vàng):** Chỉ phụ thuộc C2=T → C1, C3, C4 đều **–**
- **E3 (+2% VĐT):** Chỉ phụ thuộc C3=T → C1, C2, C4 đều **–**
- **E4 (+5% FS):** Chỉ phụ thuộc C4=T → C1, C2, C3 đều **–**
- **E5 (Freeship):** Phụ thuộc C1=T **VÀ** C3=T → C2, C4 đều **–**

Gộp các rules có cùng tập hành động, sử dụng dấu **–** cho điều kiện không ảnh hưởng:

**Bảng quyết định rút gọn:**

| | R1' | R2' | R3' | R4' | R5' | R6' | R7' | R8' | R9' | R10' |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **C1: Kim cương?** | T | T | T | T | F | F | F | F | F | F |
| **C2: Vàng?** | – | – | – | – | T | T | T | T | F | F |
| **C3: Ví điện tử?** | F | F | T | T | F | F | T | T | F | T |
| **C4: Flash Sale?** | F | T | F | T | F | T | F | T | – | – |
| | | | | | | | | | | |
| **E1: +5% (KC)** | ✓ | ✓ | ✓ | ✓ | | | | | | |
| **E2: +3% (Vàng)** | | | | | ✓ | ✓ | ✓ | ✓ | | |
| **E3: +2% (VĐT)** | | | ✓ | ✓ | | | ✓ | ✓ | | ✓ |
| **E4: +5% (FS)** | | ✓ | | ✓ | | ✓ | | ✓ | | |
| **E5: Freeship** | | | ✓ | ✓ | | | | | | |
| | | | | | | | | | | |
| **Tổng % giảm thêm** | +5 | +10 | +7 | +12 | +3 | +8 | +5 | +10 | +0 | +2 |
| **Tổng % giảm (+ R1=10%)** | 15% | 20% | 17% | 22% | 13% | 18% | 15% | 20% | 10% | 12% |

> **Ghi chú:**
> - R1'–R4': Hạng Kim cương, C2 = **–** vì khi C1=T thì C2 luôn F
> - R9'–R10': Hạng Bạc (C1=F, C2=F), C4 = **–** vì Flash Sale không ảnh hưởng đến việc xác định hạng Bạc
> - Tất cả tổng % ≤ 25% → không bị cap bởi R6

##### Bước 6: Kiểm tra độ phủ

- 10 rules đã phủ tất cả tổ hợp có ý nghĩa của 4 điều kiện ✓
- Mỗi hạng thành viên (Bạc, Vàng, Kim cương) đều có ít nhất 2 ca kiểm thử ✓
- Hành động Freeship (E5) được kiểm tra ở R3', R4' ✓

##### Bước 7: Thêm hành động vào mỗi cột

Đã hoàn thành ở bảng rút gọn trên.

##### Bước 8: Chuyển mỗi cột thành ca kiểm thử

| TC-ID | Rule | order_value | member_tier | payment_method | is_flash_sale | Expected discount | Expected freeship | Expected final_price |
|-------|:----:|:-----------:|:-----------:|:--------------:|:-------------:|:-----------------:|:-----------------:|:--------------------:|
| DT-01 | R1' | 3.000.000 | Kim cương | Tiền mặt | False | 15% | No | 2.550.000 |
| DT-02 | R2' | 3.000.000 | Kim cương | Tiền mặt | True | 20% | No | 2.400.000 |
| DT-03 | R3' | 3.000.000 | Kim cương | Ví điện tử | False | 17% | Yes | 2.490.000 |
| DT-04 | R4' | 3.000.000 | Kim cương | Ví điện tử | True | 22% | Yes | 2.340.000 |
| DT-05 | R5' | 3.000.000 | Vàng | Tiền mặt | False | 13% | No | 2.610.000 |
| DT-06 | R6' | 3.000.000 | Vàng | Tiền mặt | True | 18% | No | 2.460.000 |
| DT-07 | R7' | 3.000.000 | Vàng | Ví điện tử | False | 15% | No | 2.550.000 |
| DT-08 | R8' | 3.000.000 | Vàng | Ví điện tử | True | 20% | No | 2.400.000 |
| DT-09 | R9' | 3.000.000 | Bạc | Tiền mặt | False | 10% | No | 2.700.000 |
| DT-10 | R10' | 3.000.000 | Bạc | Ví điện tử | False | 12% | No | 2.640.000 |

**Bổ sung – Ca kiểm thử đầu vào không hợp lệ:**

| TC-ID | Mô tả | Expected |
|-------|-------|----------|
| DT-11 | Hạng không tồn tại ("Platinum") | Error |
| DT-12 | Phương thức thanh toán không hợp lệ ("Bitcoin") | Error |
| DT-13 | is_flash_sale không phải bool ("yes") | Error |

**Tổng: 10 ca kiểm thử Decision Table + 3 ca kiểm thử invalid = 13**

---

## 3. Kết quả thực hiện

### Chạy test

```
$ python -m pytest tests/ -v

=========== test session starts ===========
collected 28 items

tests/test_boundary.py::TestBVA_Boundary500k::test_BVA01_min          PASSED
tests/test_boundary.py::TestBVA_Boundary500k::test_BVA02_nom          PASSED
tests/test_boundary.py::TestBVA_Boundary500k::test_BVA03_max_minus    PASSED
tests/test_boundary.py::TestBVA_Boundary500k::test_BVA04_min_bien     PASSED
tests/test_boundary.py::TestBVA_Boundary500k::test_BVA05_min_plus     PASSED
tests/test_boundary.py::TestBVA_Boundary2M::test_BVA06_nom            PASSED
tests/test_boundary.py::TestBVA_Boundary2M::test_BVA07_max_minus      PASSED
tests/test_boundary.py::TestBVA_Boundary2M::test_BVA08_max            PASSED
tests/test_boundary.py::TestBVA_Boundary2M::test_BVA09_min            PASSED
tests/test_boundary.py::TestBVA_Boundary2M::test_BVA10_min_plus       PASSED
tests/test_boundary.py::TestBVA_BoundaryOverall::test_BVA11_nom       PASSED
tests/test_boundary.py::TestBVA_BoundaryOverall::test_BVA12_max_minus PASSED
tests/test_boundary.py::TestBVA_BoundaryOverall::test_BVA13_max       PASSED
tests/test_boundary.py::TestBVA_Robust::test_BVA_R1_min_minus         PASSED
tests/test_boundary.py::TestBVA_Robust::test_BVA_R2_max_plus          PASSED
tests/test_decision_table.py::TestDT_KimCuong::test_DT01              PASSED
tests/test_decision_table.py::TestDT_KimCuong::test_DT02              PASSED
tests/test_decision_table.py::TestDT_KimCuong::test_DT03              PASSED
tests/test_decision_table.py::TestDT_KimCuong::test_DT04              PASSED
tests/test_decision_table.py::TestDT_Vang::test_DT05                  PASSED
tests/test_decision_table.py::TestDT_Vang::test_DT06                  PASSED
tests/test_decision_table.py::TestDT_Vang::test_DT07                  PASSED
tests/test_decision_table.py::TestDT_Vang::test_DT08                  PASSED
tests/test_decision_table.py::TestDT_Bac::test_DT09                   PASSED
tests/test_decision_table.py::TestDT_Bac::test_DT10                   PASSED
tests/test_decision_table.py::TestDT_Invalid::test_DT11               PASSED
tests/test_decision_table.py::TestDT_Invalid::test_DT12               PASSED
tests/test_decision_table.py::TestDT_Invalid::test_DT13               PASSED

=========== 28 passed in 0.05s ============
```

### Bảng so sánh Expected vs Actual

| TC-ID | Expected Result | Actual Result | Pass/Fail |
|-------|:---------------:|:-------------:|:---------:|
| BVA-01 → BVA-13 | Xem bảng mục 2.1.5 | Khớp |  PASS |
| BVA-R1, BVA-R2 | Error | Error |  PASS |
| DT-01 → DT-10 | Xem bảng mục 2.2.2 bước 8 | Khớp |  PASS |
| DT-11 → DT-13 | Error | Error |  PASS |

**Kết quả: 28/28 ca kiểm thử PASS (100%)**

---

## 4. Link GitHub

> **Repository:** [https://github.com/ntd1928/KiemThu](https://github.com/ntd1928/KiemThu)
