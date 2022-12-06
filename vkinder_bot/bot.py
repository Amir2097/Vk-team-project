from random import randrange
import configparser
import vk_api, json
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
from Database.Session import Connect, Photo, Founduser, Mainuser, Blocked, Favorite
from vkinder_bot.extraction_data import ExtractingUserData

config = configparser.ConfigParser()
config.read("vkinder_bot/config_bot.cfg")
tokenson = config["TOKEN"]["vk_token"]
vk = vk_api.VkApi(token=tokenson)
longpoll = VkLongPoll(vk)


class sending_messages:
    """Итератор для вывода данных сформированных в бд о найденных пользователях"""

    def __init__(self, main_vk_id):
        self.main_vk_id = main_vk_id
        self.token_communities = config["TOKEN"]["vk_token"]
        self.query = Connect.session.query(Mainuser).filter(Mainuser.vk_id == str(main_vk_id)).first()
        self.query_founduser = Connect.session.query(Founduser).filter(Founduser.user_id == self.query.user_id).all()

    def __iter__(self):
        return self

    def __next__(self):
        if self.query_founduser:
            self.value_list = self.query_founduser.pop()
            self.usermessage = f'{self.value_list.name} {self.value_list.lastname}\nhttps://vk.com/id{self.value_list.vk_id}\n'
            self.query_photo = Connect.session.query(Photo).filter(
                Photo.found_user_id == self.value_list.found_user_id).all()
            attachment = [f'photo{self.value_list.vk_id}_{photo_iter.media_id}' for photo_iter in self.query_photo]
            new_attachment = ','.join(attachment)
            self.paramitres = {'access_token': self.token_communities, 'user_ids': self.main_vk_id,
                               'random_id': 0, 'attachment': new_attachment, 'v': 5.131}
            requests.get(url=f'https://api.vk.com/method/messages.send', params=self.paramitres)
        else:
            self.usermessage = 'список людей закончился, для того, чтобы начать с начала нажми "Поиск"'
            self.query_founduser = Connect.session.query(Founduser).filter(
                Founduser.user_id == self.query.user_id).all()
        return self.usermessage


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
            nb[i][k] = {"action": {"type": "text", "payload": "{\"button\": \"" + "1" + "\"}", "label": f"{text}"},
                        "color": f"{color}"}
    first_keyboard = {"one_time": False, "buttons": nb}
    first_keyboard = json.dumps(first_keyboard, ensure_ascii=False).encode("utf-8")
    first_keyboard = str(first_keyboard.decode("utf-8"))
    return first_keyboard


'''Стартовое меню с 6 кнопками (для начала работа с меню)'''
start_keyboard = get_keyboard([
    [('Критерии для поиска', 'синий'), ('Поиск людей', 'зеленый')],
    [('Что умеет делать бот', 'синий'), ('Черный Список', 'красный')],
    [('Избранные', 'зеленый'), ('Добавить ТОКЕН', 'синий')]
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


def run_bot():
    global age_from, age_to, user_sex

    def write_msg(user_id, message, keyboard=None):
        vk.method('messages.send',
                  {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), 'keyboard': keyboard})

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            request = event.text.lower()
            name_vk_user = Connect().session.query(Mainuser).filter(
                Mainuser.vk_id == str(event.user_id)).first()

            if request == "начать" or request == "привет" or request == "1":
                double_user_id = Connect.session.query(Mainuser).filter(Mainuser.vk_id == str(event.user_id)).first()

                if double_user_id == None:
                    main_user_vk = ExtractingUserData().profile_info(event.user_id)
                    Connect().user_database_entry(main_user_vk)
                    write_msg(event.user_id, f"{name_vk_user.name} привет! Прошу ознакомиться с меню:", start_keyboard)
                    user_mode = 'start'
                else:
                    '''Стартовое, основное меню для пользователя'''
                    write_msg(event.user_id, f"{name_vk_user.name} привет! Прошу ознакомиться с меню:", start_keyboard)
                    user_mode = 'start'

            if request == "критерии для поиска":
                '''Переход в меню для фильтрации данных пользователя'''
                write_msg(event.user_id, "Собеседника какого пола вы ищете?", sex_keyboard)
                user_mode = 'info_search_people'

            if request == "поиск людей":
                '''Переход пользователя на следующее меню для поиска партнеров'''
                write_msg(event.user_id, "Управляйте кнопками и просматривайте варианты!", process_keyboard)
                user_mode = 'search_people'
                iterator_start = sending_messages(event.user_id)

            if request == "назад":
                '''Переход в основное, стартовое меню'''
                write_msg(event.user_id, f"{name_vk_user.name} вы перешли назад", start_keyboard)
                user_mode = 'start'

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
                    user_user_id = Connect.session.query(Mainuser).filter(
                        Mainuser.vk_id == str(event.user_id)).first()
                    favorite_users = Connect.session.query(Favorite).filter(
                        Favorite.user_id == user_user_id.user_id).all()

                    if favorite_users == []:
                        write_msg(event.user_id, f'Список избранных пуст!')

                    else:
                        for favorites in favorite_users:
                            write_msg(event.user_id, f'https://vk.com/id{favorites.vk_id}')

                if request == "черный список":
                    '''Выведение списка ЧС пользователей'''
                    write_msg(event.user_id, f"Ваш список ЧС:", start_keyboard)
                    user_user_id = Connect.session.query(Mainuser).filter(
                        Mainuser.vk_id == str(event.user_id)).first()
                    blocked_users = Connect.session.query(Blocked).filter(
                        Blocked.user_id == user_user_id.user_id).all()

                    if blocked_users == []:
                        write_msg(event.user_id, f'Список ЧС пуст!')

                    else:
                        for blockeds in blocked_users:
                            write_msg(event.user_id, f'https://vk.com/id{blockeds.vk_id}')


                if request == "добавить токен":
                    '''Запрос на добавление токена от пользователя в чат'''
                    write_msg(event.user_id, f"Данная функция в реализации", start_keyboard)

                # if 'vk1.a' in request:
                #     'Получение токена от пользователя'
                #     print(request)

            if user_mode == 'info_search_people':

                if request == "мужчина":
                    '''Выбор пола, если мужчина, то в список добавляется 2'''
                    user_sex = 2
                    write_msg(event.user_id, f"{name_vk_user.name} напишите возраст:")
                '''Добавление возраста в словарь под ключом: age'''

                if request == "девушка":
                    '''Если девушка, то в список добавляется 1'''
                    user_sex = 1
                    write_msg(event.user_id, f"{name_vk_user.name} напишите возраст:")
                '''Добавление возраста в словарь под ключом: age'''

                if len(request) == 2:
                    age_from = int(request) - 3
                    age_to = int(request) + 3
                    try:
                        found_double_id = Connect.session.query(Founduser).filter(
                            Founduser.user_id == double_user_id.user_id).first()
                    except AttributeError:
                        continue

                    if found_double_id == None:
                        write_msg(event.user_id,
                                  f"Происходит добавление людей в базу данных, ожидайте ответа о завершении:")
                        City_user = ExtractingUserData().extract_city_and_country(str(event.user_id))
                        data_found_user = ExtractingUserData().user_search(count=107, age_from=age_from, age_to=age_to,
                                                                           sex=user_sex, city=City_user[1],
                                                                           country=City_user[0])
                        Connect().founduser_database_entry(data_found_user, event.user_id)
                        write_msg(event.user_id, f"Рекомендации найдены, перейдите в поиск:", start_keyboard)

                    else:
                        write_msg(event.user_id,
                                  f"Происходит обновление БД, ожидайте ответа о завершении:")
                        Connect().delete_found_users(str(event.user_id))
                        write_msg(event.user_id,
                                  f"Происходит добавление людей в базу данных, ожидайте ответа о завершении:")
                        City_user = ExtractingUserData().extract_city_and_country(event.user_id)
                        data_found_user = ExtractingUserData().user_search(count=107, age_from=age_from, age_to=age_to,
                                                                           sex=user_sex, city=City_user[1],
                                                                           country=City_user[0])
                        Connect().founduser_database_entry(data_found_user, event.user_id)
                        write_msg(event.user_id, f"Рекомендации найдены, перейдите в поиск:", start_keyboard)


            if user_mode == 'search_people':

                if request == 'поставить лайк':
                    '''Поставить лайк на первое(главное) фото пользователя'''
                    ExtractingUserData().like(iterator_start.value_list.vk_id, iterator_start.query_photo[0].media_id)
                    write_msg(event.user_id, f"Вы лайкнули фото!")

                if request == 'убрать лайк':
                    '''Убирает лайк с фото пользователя'''
                    ExtractingUserData().dislike(iterator_start.value_list.vk_id,
                                                 iterator_start.query_photo[0].media_id)
                    write_msg(event.user_id, f"Вы убрали лайк с фото!")

                if request == 'поиск':
                    '''поиск людей через глобальный поиск'''
                    write_msg(event.user_id, next(iterator_start))

                if request == 'в чс':
                    '''Добавляем страницу(id) в ЧС'''
                    if Connect.session.query(Blocked.vk_id).filter(
                            Blocked.vk_id == iterator_start.value_list.vk_id).first() == None:
                        add_blocked_users = Blocked(vk_id=iterator_start.value_list.vk_id,
                                                    user_id=iterator_start.value_list.user_id)
                        Connect().session.add(add_blocked_users)
                        Connect().session.commit()
                        write_msg(event.user_id, "Теперь данная страница находится в ЧС!")

                    else:
                        write_msg(event.user_id, "Пользователь уже в ЧС!")


                if request == 'в избранное':
                    '''Добавляем страницу(id) в понравившийся список'''
                    if Connect.session.query(Favorite.vk_id).filter(
                            Favorite.vk_id == iterator_start.value_list.vk_id).first() == None:
                        add_favorite_users = Favorite(vk_id=iterator_start.value_list.vk_id,
                                                      user_id=iterator_start.value_list.user_id)
                        Connect().session.add(add_favorite_users)
                        Connect().session.commit()
                        write_msg(event.user_id, "Пользователь добавлен в избранное")

                    else:
                        write_msg(event.user_id, "Пользователь уже есть!")
