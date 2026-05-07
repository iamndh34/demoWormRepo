"""
🚨 BẢNG LIỆT KÊ LỖI MONG ĐỢI (EXPECTED FINDINGS)
----------------------------------------------------------------------
| STT | Agent Mục Tiêu         | Loại Lỗi (Error Category)      | Mô Tả Chi Tiết                               |
|-----|------------------------|-------------------------------|----------------------------------------------|
| 1   | bmad-developer-amelia  | Code Quality: Floating Point  | Dùng float cho tiền tệ (gây sai số)          |
| 2   | bmad-codereview-pro    | Logic: Non-atomic Checkout    | Trừ tiền trước khi check kho/gửi mail        |
| 3   | architect-winston      | Architecture: Circular Dep    | Import vòng quanh giữa Payment và Inventory  |
----------------------------------------------------------------------
"""

def process_payment(amount: float):
    # Lỗi: Sai số kế toán. Đáng lẽ phải dùng Decimal
    tax = amount * 0.0825
    return amount + tax

async def checkout(user_id, total):
    # Lỗi: Nếu email fail, tiền đã bị trừ nhưng order chưa tạo
    await db.deduct_money(user_id, total)
    await email_service.send_receipt(user_id)
    await db.create_order(user_id, total)
