from aiogram.dispatcher.filters.state import StatesGroup, State

class CouponState(StatesGroup):
    code = State()
    percentage = State()
    duration = State()
    limit = State()
    affected_products = State()
    affected_categories = State()
