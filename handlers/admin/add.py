
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ContentType, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData
from keyboards.default.markups import *
from states import ProductState, CategoryState
from aiogram.types.chat import ChatActions
from handlers.user.menu import settings
from loader import dp, db, bot
from filters import IsAdmin
from hashlib import md5


category_cb = CallbackData('category', 'id', 'action')
product_cb = CallbackData('product', 'id', 'action')

add_product = '➕ Add product'
delete_category = '🗑️ Delete category'

@dp.message_handler(IsAdmin(), text=settings)
async def process_settings(message: Message):

    markup = InlineKeyboardMarkup()

    for idx, title in db.fetchall('SELECT * FROM categories'):

        markup.add(InlineKeyboardButton(
            title, callback_data=category_cb.new(id=idx, action='view')))

    markup.add(InlineKeyboardButton(
        '+ Add category', callback_data='add_category'))

    await message.answer('Setting up categories:', reply_markup=markup)


@dp.callback_query_handler(IsAdmin(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery, callback_data: dict, state: FSMContext):

    category_idx = callback_data['id']

    products = db.fetchall('''SELECT * FROM products product
    WHERE product.tag = (SELECT title FROM categories WHERE idx=?)''',
                           (category_idx,))

    await query.message.delete()
    await query.answer('All added products to this category.')
    await state.update_data(category_index=category_idx)
    await show_products(query.message, products, category_idx)


# category


@dp.callback_query_handler(IsAdmin(), text='add_category')
async def add_category_callback_handler(query: CallbackQuery):
    await query.message.delete()
    await query.message.answer('name of category?')
    await CategoryState.title.set()


@dp.message_handler(IsAdmin(), state=CategoryState.title)
async def set_category_title_handler(message: Message, state: FSMContext):

    category = message.text
    idx = md5(category.encode('utf-8')).hexdigest()
    db.query('INSERT INTO categories VALUES (?, ?)', (idx, category))

    await state.finish()
    await process_settings(message)


@dp.message_handler(IsAdmin(), text=delete_category)
async def delete_category_handler(message: Message, state: FSMContext):

    async with state.proxy() as data:

        if 'category_index' in data.keys():

            idx = data['category_index']

            db.query(
                'DELETE FROM products WHERE tag IN (SELECT title FROM categories WHERE idx=?)', (idx,))
            db.query('DELETE FROM categories WHERE idx=?', (idx,))

            await message.answer('done!', reply_markup=ReplyKeyboardRemove())
            await process_settings(message)


# add product


@dp.message_handler(IsAdmin(), text=add_product)
async def process_add_product(message: Message):

    await ProductState.title.set()

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_message)

    await message.answer('Name?', reply_markup=markup)


@dp.message_handler(IsAdmin(), text=cancel_message, state=ProductState.title)
async def process_cancel(message: Message, state: FSMContext):

    await message.answer('Ок, cancelled!', reply_markup=ReplyKeyboardRemove())
    await state.finish()

    await process_settings(message)


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.title)
async def process_title_back(message: Message, state: FSMContext):
    await process_add_product(message)


@dp.message_handler(IsAdmin(), state=ProductState.title)
async def process_title(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data['title'] = message.text

    await ProductState.next()
    await message.answer('Description?', reply_markup=back_markup())


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.body)
async def process_body_back(message: Message, state: FSMContext):

    await ProductState.title.set()

    async with state.proxy() as data:

        await message.answer(f"Change name с <b>{data['title']}</b>?", reply_markup=back_markup())


@dp.message_handler(IsAdmin(), state=ProductState.body)
async def process_body(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data['body'] = message.text

    await ProductState.next()
    await message.answer('Photo?', reply_markup=back_markup())


@dp.message_handler(IsAdmin(), content_types=ContentType.PHOTO, state=ProductState.image)
async def process_image_photo(message: Message, state: FSMContext):

    fileID = message.photo[-1].file_id
    file_info = await bot.get_file(fileID)
    downloaded_file = (await bot.download_file(file_info.file_path)).read()

    async with state.proxy() as data:
        data['image'] = downloaded_file

    await ProductState.next()
    await message.answer('Price?', reply_markup=back_markup())


@dp.message_handler(IsAdmin(), content_types=ContentType.TEXT, state=ProductState.image)
async def process_image_url(message: Message, state: FSMContext):

    if message.text == back_message:

        await ProductState.body.set()

        async with state.proxy() as data:

            await message.answer(f"Change description с <b>{data['body']}</b>?", reply_markup=back_markup())

    else:

        await message.answer('You need to send a photo of the product.')


@dp.message_handler(IsAdmin(), lambda message: not message.text.isdigit(), state=ProductState.price)
async def process_price_invalid(message: Message, state: FSMContext):

    if message.text == back_message:

        await ProductState.image.set()

        async with state.proxy() as data:

            await message.answer("Another image?", reply_markup=back_markup())

    else:

        await message.answer('Enter the price as a number!')


@dp.message_handler(IsAdmin(), lambda message: message.text.isdigit(), state=ProductState.price)
async def process_price(message: Message, state: FSMContext):

    async with state.proxy() as data:

        data['price'] = message.text
        await ProductState.unique_code.set()  # Add this line
        await message.answer('Unique Code?', reply_markup=back_markup())
        await ProductState.shipping_price.set()  # Add this line
        await message.answer('Shipping Price?', reply_markup=back_markup())  # Add this line
        
        title = data['title']
        body = data['body']
        price = data['price']

        await ProductState.next()
        text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price} рублей.'

        markup = check_markup()

        await message.answer_photo(photo=data['image'],
                                   caption=text,
                                   reply_markup=markup)
@dp.message_handler(IsAdmin(), state=ProductState.shipping_price)
async def process_shipping_price(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['shipping_price'] = message.text
    await ProductState.posting_price.set()
    await message.answer('Posting Price?', reply_markup=back_markup())

@dp.message_handler(IsAdmin(), state=ProductState.posting_price)
async def process_posting_price(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['posting_price'] = message.text

    # Calculate the total price
    total_price = int(data['price']) + int(data['shipping_price']) + int(data['posting_price'])

    # Prepare the product details for confirmation
    title = data['title']
    body = data['body']
    price = data['price']
    shipping_price = data['shipping_price']
    posting_price = data['posting_price']

    await ProductState.confirm.set()  # Move to the confirmation state

    text = f'''
    <b>{title}</b>\n
    {body}\n
    Actual Price: {price} \n
    Shipping Price: {shipping_price} \n
    Posting Price: {posting_price} \n
    Total Price: {total_price}
    '''

    markup = check_markup()  # Assuming check_markup() returns the appropriate InlineKeyboardMarkup

    await message.answer(text, reply_markup=markup)

@dp.message_handler(IsAdmin(), lambda message: message.text.isdigit(), state=ProductState.price)
async def process_price(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    await ProductState.unique_code.set()
    await message.answer('Unique Code?', reply_markup=back_markup())
@dp.message_handler(IsAdmin(), state=ProductState.unique_code)
async def process_unique_code(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['unique_code'] = message.text
    await ProductState.confirm.set()
@dp.message_handler(IsAdmin(), lambda message: message.text not in [back_message, all_right_message], state=ProductState.confirm)
async def process_confirm_invalid(message: Message, state: FSMContext):
    await message.answer('There was no such option.')


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.confirm)
async def process_confirm_back(message: Message, state: FSMContext):

    await ProductState.price.set()

    async with state.proxy() as data:

        await message.answer(f"Change the price с <b>{data['price']}</b>?", reply_markup=back_markup())


@dp.message_handler(IsAdmin(), text=all_right_message, state=ProductState.confirm)
async def process_confirm(message: Message, state: FSMContext):

    async with state.proxy() as data:

        title = data['title']
        body = data['body']
        image = data['image']
        price = int(data['price'])  # Convert to int for calculations
        shipping_price = int(data['shipping_price'])  # Convert to int
        posting_price = int(data['posting_price'])  # Convert to int
        unique_code = data['unique_code']
        total_price = price + shipping_price + posting_price  # Calculate total price

        tag = db.fetchone(
            'SELECT title FROM categories WHERE idx=?', (data['category_index'],))[0]
        idx = md5(' '.join([title, body, str(price), tag]
                           ).encode('utf-8')).hexdigest()

        # Update the database query to include the new fields
        db.query('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                 (idx, title, body, image, price, shipping_price, posting_price, total_price, tag, unique_code))

    await state.finish()
    await message.answer('Product added successfully!', reply_markup=ReplyKeyboardRemove())
    await process_settings(message)


# delete product


@dp.callback_query_handler(IsAdmin(), product_cb.filter(action='delete'))
async def delete_product_callback_handler(query: CallbackQuery, callback_data: dict):

    product_idx = callback_data['id']
    db.query('DELETE FROM products WHERE idx=?', (product_idx,))
    await query.answer('Deleted!')
    await query.message.delete()


async def show_products(m, products, category_idx):

    await bot.send_chat_action(m.chat.id, ChatActions.TYPING)

    for idx, title, body, image, price, tag in products:

        text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price} рублей.'

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(
            '🗑️ Delete', callback_data=product_cb.new(id=idx, action='delete')))

        await m.answer_photo(photo=image,
                             caption=text,
                             reply_markup=markup)

    markup = ReplyKeyboardMarkup()
    markup.add(add_product)
    markup.add(delete_category)

    await m.answer('Do you want to add or remove anything??', reply_markup=markup)
