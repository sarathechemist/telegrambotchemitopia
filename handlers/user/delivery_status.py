
from aiogram.types import Message
from loader import dp, db, bot
from .menu import delivery_status
from filters import IsUser

@dp.message_handler(IsUser(), text=delivery_status)
async def process_delivery_status(message: Message):
    
    orders = db.fetchall('SELECT * FROM orders WHERE cid=?', (message.chat.id,))
    
    if len(orders) == 0: await message.answer('У вас нет активных заказов.')
    else: await delivery_status_answer(message, orders)

async def delivery_status_answer(message, orders):
    res = ''
    for order in orders:
        res += f'Order <b>#{order[0]}</b> is currently <b>{order[7]}</b>.\n\n'
    await message.answer(res)
from loader import bot  # Make sure to import the bot instance

async def update_order_status(order_id, new_status):
    # Update the order status in the database
    db.query('UPDATE orders SET status=? WHERE id=?', (new_status, order_id))
    
    # Fetch the chat ID (cid) for the user associated with this order
    row = db.fetchone('SELECT cid FROM orders WHERE id=?', (order_id,))
    if row:
        cid = row[0]
        
        # Notify the user about the status change
        await bot.send_message(cid, f"Your order with ID {order_id} has been updated to: {new_status}")
    else:
        print(f"Order ID {order_id} not found in database.")
