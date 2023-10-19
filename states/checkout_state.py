from aiogram.dispatcher.filters.state import StatesGroup, State

class CheckoutState(StatesGroup):
    check_cart = State()
    name = State()
    address = State()
    confirm = State()
    
class ReceiptState(StatesGroup):
    receipt = State()
    
class OrderState(StatesGroup):
    name = State()
    last_name = State()
    phone_number = State()
    post_address = State()
class ReceiptState(StatesGroup):
    receipt = State()
