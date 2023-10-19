from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from states import OrderState
from loader import dp, db

@dp.message_handler(state=OrderState.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Please enter your last name:")
    await OrderState.next()

@dp.message_handler(state=OrderState.last_name)
async def process_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Please enter your phone number:")
    await OrderState.next()

@dp.message_handler(state=OrderState.phone_number)
async def process_phone_number(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    await message.answer("Please enter your post address:")
    await OrderState.next()

@dp.message_handler(state=OrderState.post_address)
async def process_post_address(message: Message, state: FSMContext):
    await state.update_data(post_address=message.text)
    # Save to database and finish the state
    user_data = await state.get_data()
    db.query('INSERT INTO orders (name, last_name, phone_number, post_address) VALUES (?, ?, ?, ?)',
             (user_data['name'], user_data['last_name'], user_data['phone_number'], user_data['post_address']))
    await state.finish()
    await message.answer("Order placed successfully!")
