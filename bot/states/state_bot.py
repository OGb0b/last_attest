from aiogram.fsm.state import State, StatesGroup

class BotStates(StatesGroup):
    Start = State()
    Add_Business = State()



class BusinessCreation(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_audience = State()