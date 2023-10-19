from aiogram.types import Message
from loader import dp, db
from filters import IsUser

@dp.message_handler(IsUser(), text='💳 Make Payment')
async def process_payment(message: Message):
    # Here, you can integrate your payment gateway
    await message.answer("Please make the payment to the following credit card: [Your Credit Card Info]")
