from random import randrange
import configparser
import vk_api, json
from vk_api.longpoll import VkLongPoll, VkEventType


config = configparser.ConfigParser()
config.read("config_bot.cfg")
vk = vk_api.VkApi(token=config["TOKEN"]["vk_token"])
longpoll = VkLongPoll(vk)


def get_keyboard(buts):
    '''
    Функция для создания кнопок в меню чата, имеет 3 основных цвета:
    зеленый - positive, красный - negative, синий - primary
    '''
    nb = []
    color = ''
    for i in range(len(buts)):
        nb.append([])
        for k in range(len(buts[i])):
            nb[i].append(None)
    for i in range(len(buts)):
        for k in range(len(buts[i])):
            text = buts[i][k][0]
            color = {"зеленый": "positive", "красный": "negative", "синий": "primary"}[buts[i][k][1]]
            nb[i][k] = {"action": {"type": "text", "payload": "{\"button\": \"" + "1" + "\"}", "label": f"{text}"}, "color": f"{color}"}
    first_keyboard = {"one_time": False, "buttons": nb}
    first_keyboard = json.dumps(first_keyboard, ensure_ascii=False).encode("utf-8")
    first_keyboard = str(first_keyboard.decode("utf-8"))
    return first_keyboard



'''Стартовое меню с 6 кнопками (для начала работа с меню)'''
start_keyboard = get_keyboard([
    [('Критерии для поиска', 'синий'), ('Поиск людей', 'зеленый')],
    [('Что умеет делать бот', 'синий'), ('ЧС', 'красный')],
    [('Избранные', 'зеленый'), ('Создатели', 'синий')]
])

'''Меню с 6 кнопками для непосредственно самого поиска'''
process_keyboard = get_keyboard([
    [('Поставить лайк', 'красный'), ('Убрать лайк', 'синий')],
    [('Поиск', 'синий'), ('В избранное', 'красный')],
    [('В ЧС', 'синий'), ('Назад', 'зеленый')]
])

'''Меню с 2 кнопка для выбора пола партнера'''
sex_keyboard = get_keyboard([
    [('Мужчина', 'зеленый')],
    [('Девушка', 'красный')]
])

# TODO Пока временные списки, потом при работе с базой данных решим этот вопрос


user_sex_list = []
'''Критерии поиска пола (2-мужчина, 1-женщина)'''


age_from_list = []
'''Критерий поиска от минимального возраста (-3)'''

age_to_list = []
'''Критерий поиска до максимального возраста (+3)'''

age = []


age_user = {}
'''Словарь для возраста пользователя'''


black_list = []
'''ЧС со списком id пользователей'''

like_me_list =[]
'''Список понравившихся id пользователей'''




def run_bot():
    # TODO: добавить запрос разрешения отправки сообщений!

    def write_msg(user_id, message, keyboard=None):
        vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), 'keyboard': keyboard})

    for event in longpoll.listen():

        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            request = event.text.lower()


            if request == "начать" or request == "привет":
                '''Стартовое, основное меню для пользователя'''
                write_msg(event.user_id, f"{event.user_id} привет! Прошу ознакомиться с меню:", start_keyboard)
                user_mode = 'start'

            if request == "критерии для поиска":
                '''Переход в меню для фильтрации данных пользователя'''
                write_msg(event.user_id, "Собеседника какого пола вы ищете?", sex_keyboard)
                user_mode = 'info_search_people'

            if request == "поиск людей":
                '''Переход пользователя на следующее меню для поиска партнеров'''
                write_msg(event.user_id, "Управляйте кнопками и просматривайте варианты!", process_keyboard)
                user_mode = 'search_people'

            if request == "назад":
                '''Переход в основное, стартовое меню'''
                write_msg(event.user_id, f"{event.user_id} вы перешли назад", start_keyboard)


            if user_mode == 'start':

                if request == "что умеет делать бот":
                    '''Описание функциоанала бота'''
                    write_msg(event.user_id, "Бот способен на многое!\n Главная его функция, это сближать людей!\n"
                                                 "Ничего сложного нету, полагайтесь на кнопки в меню чата!\n"
                                                 "Поиск людей производится по 3-ем критериям:\n"
                                                 "1 - Пол\n"
                                                 "2 - Возраст (+- 3 года диапазон поиска по возрасту)\n"
                                                 "3 - Город\n"
                                                 "Также вы можете добавить людей в Избранное и список ЧС!\n"
                                                 "Удачного пользования, надеемся мы вам поможем &#128107;", start_keyboard)

                if request == "избранные":
                    '''Выведение списка избранных пользователей'''
                    write_msg(event.user_id, f"Ваш список избранных:", start_keyboard)


                if request == "чс":
                    '''Выведение списка ЧС пользователей'''
                    write_msg(event.user_id, f"Ваш список ЧС:", start_keyboard)


            if user_mode == 'info_search_people':

                if request == "мужчина":
                    '''Выбор пола, если мужчина, то в список добавляется 2'''
                    user_sex_list.append(2)
                    write_msg(event.user_id, f"{event.user_id} Напишите возраст:")
                '''Добавление возраста в словарь под ключом: age'''

                # age.append(request)
                # print(age[-1])

                # age_user['age'] = request

                if request == "девушка":
                    '''Если девушка, то в список добавляется 1'''
                    user_sex_list.append(1)
                    write_msg(event.user_id, f"{event.user_id} Напишите возраст:")
                '''Добавление возраста в словарь под ключом: age'''
                age_user['age'] = request

            if user_mode == 'search_people':

                if request == 'поставить лайк':
                    '''Поставить лайк на определенное фото пользователя'''
                    # TODO: Здесь как то реализовать метод поставки лайк на фото
                    '''Автоматически добавляем пользователя в избранное, таким же методом что и при добавке в избранное'''
                    # TODO: like_me_list.append(search_users_id???)

                if request == 'убрать лайк':
                    '''Убирает лайк с фото пользователя и убирает пользователя из списка Избранное'''
                    # TODO: Метод убирания лайка с фото
                    '''Убираем пользователя со списка Избранное'''
                    # TODO: like_me_list.remove(search_users_id???)

                if request == 'поиск':
                    '''поиск людей через глобальный поиск'''
                    write_msg(event.user_id, "Ищем дальше")
                    # TODO: Сюда мы напишем метод по поискую людей и будем выдавать их пользователю

                if request == 'в чс':
                    '''Добавляем страницу(id) в ЧС'''
                    write_msg(event.user_id, "Теперь данная страница находится в ЧС!")
                    # TODO: В список будет добавляться id пользователя, либо можно ссылку пользователя
                    # TODO: black_list.append(search_users_id????)

                if request == 'в избранное':
                    '''Добавляем страницу(id) в понравившийся список'''
                    write_msg(event.user_id, "Пользователь добавлен в избранное")
                    # TODO: Здесь абсолютно таже схема, что и с ЧС, только список избранных
                    # TODO: like_me_list.append(search_users_id???)

