from aiogram.dispatcher.filters.state import State, StatesGroup


class States(StatesGroup):
    main_menu = State()
    suggestions = State()
    news = State()
    faq = State()

    events = State()
    list_of_events = State()
    sign_up_for_event = State()
    handle_event_signout = State()
    add_event = State()
    add_event_waiting_name = State()
    add_event_waiting_date = State()
    add_event_waiting_description = State()
    handle_event_button = State()
    handle_event_signup = State()
    delete_event = State()
    edit_event = State()
    add_event = State()
    edit_name = State()
    edit_description = State()
    edit_date = State()
    list_of_event_people = State()
    
    contact = State()

    waiting_for_phone = State()
    waiting_for_name = State()
    waiting_for_suggestion = State()