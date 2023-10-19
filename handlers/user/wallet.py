
from loader import dp
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from filters import IsUser
from .menu import balance
from states import ReceiptState  # Add this line at the top if it's not there


# test card ==> 1111 1111 1111 1026, 12/22, CVC 000

# shopId 506751

# shopArticleId 538350


@dp.message_handler(IsUser(), text=balance)
async def process_balance(message: Message, state: FSMContext):
    await message.answer('Ваш кошелек пуст! Чтобы его пополнить нужно...')

@dp.message_handler(IsUser(), text=balance)
async def process_balance(message: Message, state: FSMContext):
    await message.answer('Ваш кошелек пуст! Чтобы его пополнить нужно...')
    await ReceiptState.receipt.set()
    await message.answer("Please send the payment receipt.")
from states import ReceiptState  # Make sure this is imported

@dp.message_handler(state=ReceiptState.receipt)
async def process_receipt(message: Message, state: FSMContext):
    # Validate the receipt and update the order status
    receipt = message.text
    if validate_receipt(receipt):  # Implement this function
        await update_order_status(order_id, 'Paid')  # Implement this function
        await message.answer("Payment successful!")
    else:
        await message.answer("Invalid receipt.")
    await state.finish()