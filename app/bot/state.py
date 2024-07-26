from aiogram.fsm.state import State, StatesGroup


class RegisterState(StatesGroup):
    first_name = State()
    last_name = State()
    gender = State()
    password = State()
    phone_number = State()
    confirmation = State()


class DeleteUserState(StatesGroup):
    get_password = State()
    confirmation = State()
    delete_user = State()
