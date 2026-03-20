# Kiểm thử Hệ thống Khuyến mại (Promotional Module)

Bài tập lớn môn **Kiểm thử phần mềm** – Áp dụng 2 kỹ thuật kiểm thử hộp đen:
- **Kiểm thử giá trị biên (Boundary Value Analysis)**
- **Bảng quyết định (Decision Table Testing)**

## Mô tả bài toán

Module tính khuyến mại cho đơn hàng dựa trên 4 biến đầu vào:
- Tổng giá trị đơn hàng (0 – 50.000.000 VNĐ)
- Hạng thành viên (Bạc / Vàng / Kim cương)
- Phương thức thanh toán (Tiền mặt / Ví điện tử / Chuyển khoản)
- Thời điểm mua (Giờ thường / Flash Sale)

## Cấu trúc dự án

```
Kiemthu/
├── src/
│   ├── __init__.py
│   └── promotion.py            # Module tính khuyến mại (6 quy tắc)
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Cấu hình pytest (thêm src/ vào path)
│   ├── test_boundary.py         # 15 ca kiểm thử BVA
│   └── test_decision_table.py   # 14 ca kiểm thử Decision Table
├── docs/
│   └── report.md                # Báo cáo bài tập lớn
├── requirements.txt             # Dependencies (pytest)
├── .gitignore
└── README.md                    # File này
```

## Cài đặt & Chạy

### Yêu cầu
- Python 3.10+

### Cài đặt

```bash
git clone https://github.com/ntd1928/KiemThu.git
cd Kiemthu
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Chạy chương trình

```bash
python3 -c "
import sys; sys.path.insert(0, 'src')
from promotion import calculate_promotion
result = calculate_promotion(3000000, 'Kim cương', 'Ví điện tử', True)
print(result)
"
```

### Chạy test

```bash
# Chạy toàn bộ test
python3 -m pytest tests/ -v

# Chỉ chạy BVA
python3 -m pytest tests/test_boundary.py -v

# Chỉ chạy Decision Table
python3 -m pytest tests/test_decision_table.py -v
```

## Kết quả

```
29 passed in 0.05s ✅
```
