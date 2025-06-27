from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить новый бизнес', callback_data='add_business')],
    [InlineKeyboardButton(text='Сгенерировать описание товара', callback_data='show')],
    [InlineKeyboardButton(text='Сгенерировать текст для рекламной рассылки', callback_data='show')],
    [InlineKeyboardButton(text='Сгенерировать карточку товара', callback_data='delete')]
])