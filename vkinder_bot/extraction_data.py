import configparser
from pprint import pprint

import requests

config = configparser.ConfigParser()
config.read("config_bot.cfg")


class ExtractingUserData:
    def __init__(self):
        self.list_photo_extraction_with_marks = None
        self.dict_city_and_country = None
        self.dict_photo_and_like = None
        self.user_id = None
        self.country = None
        self.sex = None
        self.city = None
        self.age_to = None
        self.age_from = None
        self.count = None
        self.paramitres = None
        self.token = config["TOKEN"]["vk_user_token"]

    def user_search(self, count, age_from, age_to, sex, city, country):
        """
        Метод поиска пользователей сайта VK по заданным параметрам, получает на вход параметры:

        count - количество найденых записей (не более 999)
        age_from - от какого возраста искать
        age_to - до какого возраста искать
        sex - пол (2 мужчина, 1 женщина)
        city - идентификаттор города (берется у пользователя который ведет диалог с ботом)
        country - идентификатор страны (берется у пользователя который ведет диалог с ботом)

        Поиск ведется ТОЛЬКО по страницам пользователей у которых установлен смейный статус "В активном поиске"

        """
        self.count = count
        self.age_from = age_from
        self.age_to = age_to
        self.sex = sex
        self.city = city
        self.country = country

        self.paramitres = {'access_token': self.token, 'count': self.count, 'has_photo': 1, 'age_from': self.age_from,
                           'age_to': self.age_to, 'fields': 'photo_200_orig, relation: 6', 'sex': self.sex,
                           'city': self.city, 'country': self.country, 'v': 5.131}
        request_generation = requests.get(url=f'https://api.vk.com/method/users.search', params=self.paramitres)
        return request_generation.json()['response']['items']

    def photo_extraction(self, user_id):
        """
        Метод получения 3 фотографий пофиля которые имеют наибольшие LIKE, получает на вход параметры:

        user_id - id пользователя

        На выходе бедет

        """
        try:
            self.user_id = user_id
            self.dict_photo_and_like = {}
            self.paramitres = {'access_token': self.token, 'owner_id': self.user_id, 'album_id': 'profile',
                               'extended': 1, 'photo_sizes': 0, 'v': 5.131}
            request_generation = requests.get(url=f'https://api.vk.com/method/photos.get', params=self.paramitres)

            for reqer in request_generation.json()['response']['items']:
                self.dict_photo_and_like[(reqer['sizes'][3]['url'])] = reqer['likes']['count']

            return sorted(self.dict_photo_and_like, key=self.dict_photo_and_like.get)[-3:]
        except KeyError:
            return "Страница пользователя закрыта настройками приватности!"

    def extract_city_and_country(self, user_id):

        """
        Метод для получения идентификатора страны и города пользователя, получает на вход параметры:

        user_id - id пользователя

        на выходе будет список формата [идентификатор_страны, идентификатор_города]

        """
        try:
            self.user_id = user_id
            self.dict_city_and_country = []
            self.paramitres = {'access_token': self.token, 'user_ids': self.user_id, 'fields': 'city, country',
                               'v': 5.131}
            request_generation = requests.get(url=f'https://api.vk.com/method/users.get', params=self.paramitres)
            for reqer in request_generation.json()['response']:
                self.dict_city_and_country.append(reqer['country']['id'])
                self.dict_city_and_country.append(reqer['city']['id'])
            return self.dict_city_and_country
        except KeyError:
            return "Страница пользователя закрыта настройками приватности!"

    def photo_extraction_with_marks(self, user_id):

        """
        Метод для получения списка фотографий где отмечен пользователь, получает на вход параметры:

        user_id - id пользователя

        МЕТОД ВЫВОДИТ 5 ФОТОГРАФИЙ!!!!
        """
        try:
            self.user_id = user_id
            self.list_photo_extraction_with_marks = []
            self.paramitres = {'access_token': self.token, 'user_id': self.user_id, 'count': 5, 'v': 5.131}
            request_generation = requests.get(url=f'https://api.vk.com/method/photos.getUserPhotos',
                                              params=self.paramitres)
            for reqer in request_generation.json()['response']['items']:
                self.list_photo_extraction_with_marks.append(reqer['sizes'][4]['url'])

            return self.list_photo_extraction_with_marks
        except KeyError:
            return "Страница пользователя закрыта настройками приватности!"


if __name__ == '__main__':
    ex = ExtractingUserData()
    pprint(ex.photo_extraction_with_marks('127862738'))
