import sqlite3
import os
from dotenv import load_dotenv


load_dotenv()
DB_PATH = os.environ.get('DB_PATH')

def execute_query(query, values=None, fetch_all=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if values is not None:
        cursor.execute(query, values)
    else:
        cursor.execute(query)

    result = cursor.fetchall() if fetch_all else None

    conn.commit()
    conn.close()

    return result

# Мероприятия

def add_event_to_db(event_name, event_date, event_description):
    query = ''' 
        INSERT INTO Events (name, date, description) 
        VALUES (?, ?, ?) 
    '''
    execute_query(query, (event_name, event_date, event_description))


def update_event_by_id(event_id, new_name=None, new_date=None):
    update_query = 'UPDATE Events SET'
    update_values = []

    if new_name is not None:
        update_query += ' name = ?,'
        update_values.append(new_name)

    if new_date is not None:
        update_query += ' date = ?,'
        update_values.append(new_date)

    update_query = update_query.rstrip(',')

    update_query += ' WHERE id = ?'
    update_values.append(event_id)

    execute_query(update_query, tuple(update_values))


def get_all_events():
    query = 'SELECT * FROM Events'
    return execute_query(query, fetch_all=True)

def get_event(event_id):
    query = 'SELECT * FROM Events WHERE id = ?'
    return execute_query(query, (event_id,), fetch_all=True)

def delete_event_by_id(event_id):   #admin
    delete_query = 'DELETE FROM Events WHERE id = ?'
    execute_query(delete_query, (event_id,))

# people
    
def add_person_to_db(telegram_id, full_name, phone):
    query = ''' 
        INSERT INTO Person (telegramId, fullName, phone) 
        VALUES (?, ?, ?) 
    '''
    execute_query(query, (telegram_id, full_name, phone))


def delete_person_by_id(person_id):  # admin
    query = 'DELETE FROM Person WHERE id = ?'
    execute_query(query, (person_id,))


def update_person_by_id(person_id, new_full_name=None, new_phone=None):  # admin
    update_query = 'UPDATE Person SET'
    update_values = []

    if new_full_name is not None:
        update_query += ' fullName = ?,'
        update_values.append(new_full_name)

    if new_phone is not None:
        update_query += ' phone = ?,'
        update_values.append(new_phone)

    update_query = update_query.rstrip(',')

    update_query += ' WHERE id = ?'
    update_values.append(person_id)

    execute_query(update_query, tuple(update_values))

def find_person_in_db(user_telegram_id):
    query = 'SELECT * FROM Person WHERE telegramId = ?'
    return execute_query(query, (user_telegram_id,), fetch_all=True)

def get_info_about_person(person_id):
    query = 'SELECT * FROM Person WHERE id = ?'
    return execute_query(query, (person_id,), fetch_all=True)

def get_all_people():  # admin
    query = 'SELECT * FROM Person'
    return execute_query(query, fetch_all=True)


# Предложения


def add_suggestion_to_db(person_id, suggestion_text):
    query = ''' 
        INSERT INTO Suggestions (personId, suggestionText) 
        VALUES (?, ?) 
    '''
    execute_query(query, (person_id, suggestion_text))


def get_all_suggestions():  # admin
    query = 'SELECT * FROM Suggestions'
    return execute_query(query, fetch_all=True)


# QA


def get_all_people():  # admin
    query = 'SELECT * FROM Person'
    return execute_query(query, fetch_all=True)


def add_qa_to_db(question, answer):
    query = ''' 
        INSERT INTO QA (question, answer) 
        VALUES (?, ?) 
    '''
    execute_query(query, (question, answer))


def get_all_qa():  # admin
    query = 'SELECT * FROM QA'
    return execute_query(query, fetch_all=True)


def update_qa_by_id(qa_id, new_question=None, new_answer=None):  # admin
    update_query = 'UPDATE QA SET'
    update_values = []

    if new_question is not None:
        update_query += ' question = ?,'
        update_values.append(new_question)

    if new_answer is not None:
        update_query += ' answer = ?,'
        update_values.append(new_answer)

    update_query = update_query.rstrip(',')

    update_query += ' WHERE id = ?'
    update_values.append(qa_id)

    execute_query(update_query, tuple(update_values))


def delete_qa_by_id(qa_id):  # admin
    query = 'DELETE FROM QA WHERE id = ?'
    execute_query(query, (qa_id,))

def get_answer_by_id(qa_id):
    query = 'SELECT * FROM QA WHERE id=?'
    return execute_query(query, (qa_id,), fetch_all=True)

# Мероприятие - человек


def add_event_person_to_db(event_id, person_id):
    query = ''' 
        INSERT INTO EventPerson (eventId, personId) 
        VALUES (?, ?) 
    '''
    execute_query(query, (event_id, person_id))


def get_all_event_person():  # admin
    query = 'SELECT * FROM EventPerson'
    return execute_query(query, fetch_all=True)

def get_all_people_of_event(event_id):
    query = 'SELECT * FROM EventPerson WHERE eventId = ?'
    return execute_query(query, (event_id,), fetch_all=True)

def update_event_person_by_id(event_person_id, new_event_id=None, new_person_id=None):  # admin
    update_query = 'UPDATE EventPerson SET'
    update_values = []

    if new_event_id is not None:
        update_query += ' eventId = ?,'
        update_values.append(new_event_id)

    if new_person_id is not None:
        update_query += ' personId = ?,'
        update_values.append(new_person_id)

    update_query = update_query.rstrip(',')

    update_query += ' WHERE id = ?'
    update_values.append(event_person_id)

    execute_query(update_query, tuple(update_values))

def find_event_person_by_id(person_id, event_id):
    query = 'SELECT id FROM EventPerson WHERE personId = ? AND eventId = ?'
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, (person_id, event_id))
        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None
    except Exception as e:
        return None

def delete_event_person_by_id(event_person_id):
    query = 'DELETE FROM EventPerson WHERE id = ?'
    execute_query(query, (event_person_id,))

def get_active_people():
    query = '''
        SELECT p.fullName, COUNT(ep.eventId) as eventCount
        FROM Person p
        LEFT JOIN EventPerson ep ON p.id = ep.personId
        GROUP BY p.fullName
    '''

    result = execute_query(query, fetch_all=True)

    active_people_list = []
    for row in result:
        active_people_list.append((row[0], row[1]))

    return active_people_list
