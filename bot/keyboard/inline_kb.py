from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Определяем клавиатуру для начального меню
start_keyboard_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Добавить новый бизнес', callback_data='add_business')],
        [InlineKeyboardButton(text='Сгенерировать описание товара', callback_data='generate_description')],
        [InlineKeyboardButton(text='Сгенерировать текст для рекламной рассылки', callback_data='generate_ad_text')],
        [InlineKeyboardButton(text='Сгенерировать карточку товара', callback_data='create_card')],
        [InlineKeyboardButton(text='Удалить бизнес', callback_data='delete_business')],
    ]
)