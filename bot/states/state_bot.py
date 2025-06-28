from aiogram.fsm.state import State, StatesGroup


class BotStates(StatesGroup):
    Start = State()


class BusinessCreation(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_audience = State()


class CardCreation(StatesGroup):
    waiting_for_name_description_etc = State()
    waiting_for_generation = State()


class DescriptionCreation(StatesGroup):
    waiting_for_generation = State()


class AdTextCreation(StatesGroup):
    waiting_for_generation = State()