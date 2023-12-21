from aiogram.dispatcher.filters.state import State, StatesGroup


class States(StatesGroup):
    main_menu = State()
    events = State()
    suggestions = State()
    news = State()
    faq = State()
    list_of_events = State()
    sign_up_for_event = State()
    contact = State()
    handle_event_button = State()
    handle_event_signup = State()
    delete_event = State()
    edit_event = State()
    add_event = State()
    edit_name = State()
    edit_description = State()
    edit_date = State()
    waiting_for_phone = State()
    waiting_for_name = State()
    waiting_for_suggestion = State()