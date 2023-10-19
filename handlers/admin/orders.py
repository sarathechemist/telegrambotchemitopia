
from aiogram.types import Message
from loader import dp, db
from handlers.user.menu import orders
from filters import IsAdmin
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from loader import bot

@dp.message_handler(IsAdmin(), text=orders)
async def process_orders(message: Message):
    orders = db.fetchall('SELECT * FROM orders')
    if len(orders) == 0:
        await message.answer('No orders available.')
    else:
        await order_answer(message, orders)

async def order_answer(message, orders):
    for order in orders:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Confirm", callback_data=f"confirm_{order[0]}"))
        markup.add(InlineKeyboardButton("Reject", callback_data=f"reject_{order[0]}"))
        await message.answer(f"Order ID: {order[0]}, Status: {order[7]}", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith('confirm_'))
async def confirm_receipt(query: CallbackQuery):
    order_id = query.data.split("_")[1]
    # Assuming the user_id is stored in the 'user_id' column in your 'orders' table
    user_id = db.fetchone('SELECT user_id FROM orders WHERE id=?', (order_id,))[0]
    db.query('UPDATE orders SET status="Confirmed" WHERE id=?', (order_id,))
    await query.message.answer("Order confirmed.")
    await notify_user(user_id, "Your order has been confirmed.")

@dp.callback_query_handler(lambda c: c.data.startswith('reject_'))
async def reject_receipt(query: CallbackQuery):
    order_id = query.data.split("_")[1]
    # Assuming the user_id is stored in the 'user_id' column in your 'orders' table
    user_id = db.fetchone('SELECT user_id FROM orders WHERE id=?', (order_id,))[0]
    db.query('UPDATE orders SET status="Rejected" WHERE id=?', (order_id,))
    await query.message.answer("Order rejected.")
    await notify_user(user_id, "Your order has been rejected.")
async def notify_user(user_id, message):
    await bot.send_message(user_id, message)

async def order_answer(message, orders):

    res = ''

    for order in orders:
        res += f'Заказ <b>№{order[3]}</b>\n\n'

    await message.answer(res)
    
    