VALID_TIERS = {"Bạc", "Vàng", "Kim cương", "VIP"}
VALID_PAYMENTS = {"Tiền mặt", "Ví điện tử", "Chuyển khoản"}

ORDER_VALUE_MIN = 0
ORDER_VALUE_MAX = 50_000_000

MAX_DISCOUNT_PERCENT = 25  


def calculate_promotion(order_value, member_tier, payment_method, is_flash_sale):
    # --------------------------------------------------------
    # VALIDATE ĐẦU VÀO
    # --------------------------------------------------------
    # Kiểm tra kiểu dữ liệu order_value
    if not isinstance(order_value, int):
        return {"error": True, "message": "order_value phải là số nguyên (int)"}

    # Kiểm tra miền xác định order_value
    if order_value < ORDER_VALUE_MIN:
        return {"error": True, "message": f"order_value không được âm (nhận được: {order_value})"}

    if order_value > ORDER_VALUE_MAX:
        return {
            "error": True,
            "message": f"order_value vượt quá {ORDER_VALUE_MAX:,} (nhận được: {order_value})",
        }

    # Kiểm tra hạng thành viên
    if member_tier not in VALID_TIERS:
        return {
            "error": True,
            "message": f"member_tier không hợp lệ: '{member_tier}'. Chấp nhận: {VALID_TIERS}",
        }

    # Kiểm tra phương thức thanh toán
    if payment_method not in VALID_PAYMENTS:
        return {
            "error": True,
            "message": f"payment_method không hợp lệ: '{payment_method}'. Chấp nhận: {VALID_PAYMENTS}",
        }

    # Kiểm tra is_flash_sale
    if not isinstance(is_flash_sale, bool):
        return {"error": True, "message": "is_flash_sale phải là bool (True/False)"}

    # --------------------------------------------------------
    # R1: GIẢM GIÁ THEO GIÁ TRỊ ĐƠN HÀNG
    # --------------------------------------------------------
    if order_value < 500_000:
        base_discount = 0
    elif order_value <= 2_000_000:
        base_discount = 5
    else:
        base_discount = 10

    # --------------------------------------------------------
    # R2: GIẢM THÊM THEO HẠNG THÀNH VIÊN
    # --------------------------------------------------------
    tier_discount = {"Bạc": 0, "Vàng": 3, "Kim cương": 5, "VIP": 10}
    member_discount = tier_discount[member_tier]

    # --------------------------------------------------------
    # R3: GIẢM THÊM KHI THANH TOÁN BẰNG VÍ ĐIỆN TỬ
    # --------------------------------------------------------
    ewallet_discount = 2 if payment_method == "Ví điện tử" else 0

    # --------------------------------------------------------
    # R4: GIẢM THÊM KHI FLASH SALE
    # --------------------------------------------------------
    flash_discount = 5 if is_flash_sale else 0

    # --------------------------------------------------------
    # TỔNG % GIẢM GIÁ (trước cap)
    # --------------------------------------------------------
    total_discount = base_discount + member_discount + ewallet_discount + flash_discount

    # --------------------------------------------------------
    # R6: CAP GIẢM GIÁ TỐI ĐA 25%
    # --------------------------------------------------------
    if total_discount > MAX_DISCOUNT_PERCENT:
        total_discount = MAX_DISCOUNT_PERCENT

    # --------------------------------------------------------
    # R5: FREESHIP
    # Điều kiện: order_value ≥ 2.000.000 VÀ Kim cương VÀ Ví điện tử
    # --------------------------------------------------------
    freeship = (
        order_value >= 2_000_000
        and member_tier == "Kim cương"
        and payment_method == "Ví điện tử"
    )

    # --------------------------------------------------------
    # TÍNH GIÁ CUỐI CÙNG
    # --------------------------------------------------------
    final_price = order_value - (order_value * total_discount // 100)

    # --------------------------------------------------------
    # TẠO THÔNG BÁO
    # --------------------------------------------------------
    parts = [f"Giảm {total_discount}%"]
    if freeship:
        parts.append("Miễn phí vận chuyển")
    message = ", ".join(parts)

    return {
        "discount_percent": total_discount,
        "freeship": freeship,
        "final_price": final_price,
        "message": message,
    }
