# import dotenv
# import os

# dotenv_file = dotenv.find_dotenv()
# dotenv.load_dotenv(dotenv_file)

# # Получите текущее значение переменной ADMINS и преобразуйте его в список
# current_admins = os.getenv("ADMINS")
# admins_list = eval(current_admins) if current_admins else []

# # Добавьте новое значение в список
# new_value = 123
# admins_list.append(new_value)

# # Установите обновленный список в переменную ADMINS
# os.environ["ADMINS"] = str(admins_list)

# # Запишите изменения в .env файл
# dotenv.set_key(dotenv_file, "ADMINS", os.environ["ADMINS"])

# # Выведите обновленное значение переменной ADMINS
# print(os.environ["ADMINS"])