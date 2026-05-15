def process_payment(amount: float):
    tax = amount * 0.0825
    return amount + tax

async def checkout(user_id, total):
    await db.deduct_money(user_id, total)
    await email_service.send_receipt(user_id)
    await db.create_order(user_id, total)
