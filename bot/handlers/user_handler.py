from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboard.inline_kb import start_keyboard_inline
from states.state_bot import BotStates, BusinessCreation, CardCreation, DescriptionCreation, AdTextCreation
from generations.generations import generate_description as generate_product_description, generate_ad_text, generate_product_card
from data_base.models import User, Business
from data_base.db import SessionLocal
from datetime import datetime as dt
from sqlalchemy import select

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


@router.callback_query(F.data == 'add_business', BotStates.Start)
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
async def process_business_audience(message: types.Message, state: FSMContext):
    async with SessionLocal() as session:
        data = await state.get_data()
        await state.clear()
        try:
            result = await session.execute(select(User).where(User.id == message.from_user.id))
            user = result.scalar_one_or_none()

            if not user:
                user = User(id=message.from_user.id, username=message.from_user.username, created_at=dt.utcnow())
                session.add(user)
                await session.commit()

            new_business = Business(
                user_id=user.id,
                name=data['name'],
                description=data['description'],
                target_audience=message.text,
                created_at=dt.utcnow()
            )
            session.add(new_business)
            await session.commit()

            await message.answer(
                f"✅ Бизнес '{new_business.name}' успешно создан!\n"
                f"ID: {new_business.id}\n"
                f"Описание: {new_business.description}\n"
                f"Целевая аудитория: {new_business.target_audience}"
            )
            await message.answer("\nВыберите действие:", reply_markup=start_keyboard_inline)
            await state.set_state(BotStates.Start)

        except Exception as e:
            await session.rollback()
            await message.answer(f"❌ Ошибка при создании бизнеса: {str(e)}")
            await state.set_state(BotStates.Start)


@router.callback_query(F.data == 'delete_business', BotStates.Start)
async def choose_business_to_delete(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    async with SessionLocal() as session:
        try:
            user = await session.get(User, callback.from_user.id)
            if not user:
                await callback.message.answer("У вас нет добавленных бизнесов.")
                return

            result = await session.execute(select(Business).where(Business.user_id == user.id))
            businesses = result.scalars().all()

            if not businesses:
                await callback.message.answer("У вас нет добавленных бизнесов.")
                return

            builder = InlineKeyboardBuilder()
            for biz in businesses:
                builder.button(text=f"🗑 {biz.name}", callback_data=f"delete_business_{biz.id}")
            builder.adjust(1)

            await callback.message.answer("Выберите бизнес для удаления:", reply_markup=builder.as_markup())

        except Exception as e:
            await callback.message.answer(f"❌ Ошибка: {str(e)}")
            await session.rollback()

@router.callback_query(F.data.startswith("delete_business_"), BotStates.Start)
async def delete_selected_business(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    business_id = int(callback.data.split("_")[-1])

    async with SessionLocal() as session:
        try:
            business = await session.get(Business, business_id)

            if not business or business.user_id != callback.from_user.id:
                await callback.message.answer("Бизнес не найден или у вас нет прав для удаления.")
                return

            await session.delete(business)
            await session.commit()
            await callback.message.answer(f"✅ Бизнес '{business.name}' успешно удалён.", reply_markup=start_keyboard_inline)

        except Exception as e:
            await session.rollback()
            await callback.message.answer(f"❌ Ошибка при удалении бизнеса: {str(e)}")


@router.callback_query(F.data == 'create_card', BotStates.Start)
async def choose_business_for_card(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    async with SessionLocal() as session:
        try:
            user = await session.get(User, callback.from_user.id)
            result = await session.execute(select(Business).where(Business.user_id == user.id))
            businesses = result.scalars().all()

            if not businesses:
                await callback.message.answer("У вас ещё нет добавленных бизнесов. Сначала создайте бизнес.")
                return

            builder = InlineKeyboardBuilder()
            for biz in businesses:
                builder.button(text=biz.name, callback_data=f"select_business_{biz.id}")
            builder.adjust(1)

            await callback.message.answer("Выберите бизнес для генерации карточки товара:", reply_markup=builder.as_markup())
            await state.set_state(CardCreation.waiting_for_name_description_etc)

        except Exception as e:
            await callback.message.answer(f"❌ Ошибка: {str(e)}")
            await session.rollback()

@router.callback_query(F.data.startswith("select_business_"), CardCreation.waiting_for_name_description_etc)
async def ask_for_card_details(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    business_id = int(callback.data.split("_")[-1])
    await state.update_data(selected_business_id=business_id)
    await callback.message.answer("Пожалуйста, подробно опишите товар, карточку которого нужно сгенерировать:")
    await state.set_state(CardCreation.waiting_for_generation)

@router.message(CardCreation.waiting_for_generation)
async def generate_card(message: Message, state: FSMContext):
    text = message.text
    await state.update_data(card_description=text)
    state_data = await state.get_data()
    business_id = state_data.get('selected_business_id')

    async with SessionLocal() as session:
        business = (await session.execute(select(Business).where(Business.id == business_id))).scalar_one_or_none()
        if not business:
            await message.answer("Бизнес не найден. Пожалуйста, выберите бизнес снова.")
            await state.set_state(BotStates.Start)
            return

        try:
            image_url = generate_product_card(text, business.description, business.target_audience)
            await message.answer_photo(
                photo=image_url,
                caption=f"Карточка товара {text} успешно сгенерирована! Выберите следующее действие:",
                reply_markup=start_keyboard_inline
            )
        except Exception as e:
            await message.answer(f"Ошибка при генерации изображения: {str(e)}")

    await state.set_state(BotStates.Start)


@router.callback_query(F.data == 'generate_description', BotStates.Start)
async def choose_business_for_description(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    async with SessionLocal() as session:
        try:
            user = await session.get(User, callback.from_user.id)
            result = await session.execute(select(Business).where(Business.user_id == user.id))
            businesses = result.scalars().all()

            if not businesses:
                await callback.message.answer("Сначала добавьте бизнес.")
                return

            builder = InlineKeyboardBuilder()
            for biz in businesses:
                builder.button(text=biz.name, callback_data=f"select_business_{biz.id}")
            builder.adjust(1)

            await callback.message.answer("Выберите бизнес для генерации описания товара:", reply_markup=builder.as_markup())
            await state.set_state(DescriptionCreation.waiting_for_generation)

        except Exception as e:
            await callback.message.answer(f"❌ Ошибка: {str(e)}")
            await session.rollback()

@router.callback_query(F.data.startswith("select_business_"), DescriptionCreation.waiting_for_generation)
async def ask_for_description(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    business_id = int(callback.data.split("_")[-1])
    await state.update_data(selected_business_id=business_id)
    await callback.message.answer("Введите название товара для генерации описания:")

@router.message(DescriptionCreation.waiting_for_generation)
async def generate_description(message: Message, state: FSMContext):
    text = message.text
    state_data = await state.get_data()
    business_id = state_data.get('selected_business_id')

    async with SessionLocal() as session:
        try:
            business = (await session.execute(select(Business).where(Business.id == business_id))).scalar_one_or_none()
            if not business:
                await message.answer("Бизнес не найден.")
                await state.set_state(BotStates.Start)
                return

            description = generate_product_description(text, business.description, business.target_audience)
            await message.answer(
                f"Описание товара '{text}' успешно сгенерировано:\n\n{description}",
                reply_markup=start_keyboard_inline
            )

        except Exception as e:
            await message.answer(f"Ошибка при генерации описания: {str(e)}")
            await session.rollback()

    await state.set_state(BotStates.Start)


@router.callback_query(F.data == 'generate_ad_text', BotStates.Start)
async def choose_business_for_ad_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    async with SessionLocal() as session:
        try:
            user = await session.get(User, callback.from_user.id)
            result = await session.execute(select(Business).where(Business.user_id == user.id))
            businesses = result.scalars().all()

            if not businesses:
                await callback.message.answer("Сначала добавьте бизнес.")
                return

            builder = InlineKeyboardBuilder()
            for biz in businesses:
                builder.button(text=biz.name, callback_data=f"select_business_{biz.id}")
            builder.adjust(1)

            await callback.message.answer("Выберите бизнес для генерации рекламного текста:", reply_markup=builder.as_markup())
            await state.set_state(AdTextCreation.waiting_for_generation)

        except Exception as e:
            await callback.message.answer(f"❌ Ошибка: {str(e)}")
            await session.rollback()

@router.callback_query(F.data.startswith("select_business_"), AdTextCreation.waiting_for_generation)
async def ask_for_ad_text(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    business_id = int(callback.data.split("_")[-1])
    await state.update_data(selected_business_id=business_id)
    await callback.message.answer("Введите название и описание товара для рекламного текста:")

@router.message(AdTextCreation.waiting_for_generation)
async def generate_ad_text_handler(message: Message, state: FSMContext):
    text = message.text
    state_data = await state.get_data()
    business_id = state_data.get('selected_business_id')

    async with SessionLocal() as session:
        try:
            business = (await session.execute(select(Business).where(Business.id == business_id))).scalar_one_or_none()
            if not business:
                await message.answer("Бизнес не найден.")
                await state.set_state(BotStates.Start)
                return

            ad = generate_ad_text(text, business.description, business.target_audience)
            await message.answer(
                f"Рекламный текст для '{text}' успешно сгенерирован:\n\n{ad}",
                reply_markup=start_keyboard_inline
            )

        except Exception as e:
            await message.answer(f"Ошибка при генерации рекламы: {str(e)}")
            await session.rollback()

    await state.set_state(BotStates.Start)
