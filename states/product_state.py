from aiogram.dispatcher.filters.state import StatesGroup, State

class ProductState(StatesGroup):
    title = State()
    body = State()
    image = State()
    price = State()
    confirm = State()
    unique_code = State()
    shipping_price = State()  # Add this line
    posting_price = State()
class CategoryState(StatesGroup):
    title = State()