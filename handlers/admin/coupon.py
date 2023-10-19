from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from loader import dp, db
from filters import IsAdmin
from states.coupon_state import CouponState  # Import the state class

# Start the process of adding a new coupon
@dp.message_handler(IsAdmin(), commands=['add_coupon'])
async def add_coupon(message: Message):
    await CouponState.code.set()
    await message.answer("Enter the coupon code:")

# Capture the coupon code
@dp.message_handler(IsAdmin(), state=CouponState.code)
async def process_coupon_code(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['code'] = message.text
    await CouponState.percentage.set()
    await message.answer("Enter the discount percentage:")

# Capture the discount percentage
@dp.message_handler(IsAdmin(), state=CouponState.percentage)
async def process_coupon_percentage(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['percentage'] = message.text
    await CouponState.duration.set()
    await message.answer("Enter the duration (in days):")

# Capture the duration
@dp.message_handler(IsAdmin(), state=CouponState.duration)
async def process_coupon_duration(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['duration'] = message.text
    await CouponState.limit.set()
    await message.answer("Enter the usage limit:")

# Capture the usage limit
@dp.message_handler(IsAdmin(), state=CouponState.limit)
async def process_coupon_limit(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['limit'] = message.text
    await CouponState.affected_products.set()
    await message.answer("Enter the affected products (comma-separated IDs):")

# Capture the affected products
@dp.message_handler(IsAdmin(), state=CouponState.affected_products)
async def process_coupon_affected_products(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['affected_products'] = message.text
    await CouponState.affected_categories.set()
    await message.answer("Enter the affected categories (comma-separated IDs):")

# Capture the affected categories and save to database
@dp.message_handler(IsAdmin(), state=CouponState.affected_categories)
async def process_coupon_affected_categories(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['affected_categories'] = message.text
        # Save to database
        db.query('INSERT INTO coupons VALUES (?, ?, ?, ?, ?, ?)',
                 (data['code'], data['percentage'], data['duration'], data['limit'], data['affected_products'], data['affected_categories']))
    await state.finish()
    await message.answer("Coupon added successfully!")
