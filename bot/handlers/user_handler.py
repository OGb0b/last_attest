from aiogram import Router, F, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboard.inline_kb import start_keyboard_inline
from states.state_bot import BotStates, BusinessCreation
from sqlalchemy.ext.asyncio import AsyncSession
from data_base.models import User, Business
import datetime


router = Router()

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        """
Привет! 👋
Добро пожаловать в Маркетинг-Бота — твой карманный генератор продающих идей!

Я помогу тебе:
📦 Создать карточки товаров  
📝 Придумать цепляющие заголовки  
💬 Написать тексты для рекламы  
📈 И многое другое для роста твоего бизнеса

Готовы начать? Просто выбери, что тебе нужно👇
""",
         reply_markup=start_keyboard_inline)
    await state.set_state(BotStates.Start)


@router.callback_query(F.data== 'add_business', BotStates.Start)
async def start_business_creation(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Давайте создадим новый бизнес. Введите название:")
    await state.set_state(BusinessCreation.waiting_for_name)


@router.message(BusinessCreation.waiting_for_name)
async def process_business_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Отлично! Теперь введите описание бизнеса:")
    await state.set_state(BusinessCreation.waiting_for_description)


@router.message(BusinessCreation.waiting_for_description)
async def process_business_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Хорошо! Теперь укажите целевую аудиторию:")
    await state.set_state(BusinessCreation.waiting_for_audience)


@router.message(BusinessCreation.waiting_for_audience)
async def process_business_audience(
        message: types.Message,
        state: FSMContext,
        session: AsyncSession
):
    data = await state.get_data()
    await state.clear()

    try:
        user = await session.get(User, message.from_user.id)
        if not user:
            user = User(
                id=message.from_user.id,
                username=message.from_user.username,
                created_at=datetime.utcnow()
            )
            session.add(user)

        new_business = Business(
            user_id=user.id,
            name=data['name'],
            description=data['description'],
            target_audience=message.text,
            created_at=datetime.utcnow()
        )

        session.add(new_business)
        await session.commit()

        await message.answer(
            f"✅ Бизнес '{new_business.name}' успешно создан!\n"
            f"ID: {new_business.id}\n"
            f"Описание: {new_business.description}\n"
            f"Целевая аудитория: {new_business.target_audience}"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании бизнеса: {str(e)}")
        await session.rollback()