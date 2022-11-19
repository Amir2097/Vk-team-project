import configparser
import requests

config = configparser.ConfigParser()
config.read("config_bot.cfg")


class ExtractingUserData:
    def __init__(self, count, age_from, age_to, sex, city, country):
        self.paramitres = None
        self.token = config["TOKEN"]["vk_user_token"]
        self.count = count
        self.age_from = age_from
        self.age_to = age_to
        self.sex = sex
        self.city = city
        self.country = country

    def user_search(self):
        self.paramitres = {'access_token': self.token, 'count': self.count, 'has_photo': 1, 'age_from': self.age_from,
                           'age_to': self.age_to, 'fields': 'photo_200_orig, relation: 6', 'sex': self.sex,
                           'city': self.city, 'country': self.country, 'v': 5.131}
        request_generation = requests.get(url=f'https://api.vk.com/method/users.search', params=self.paramitres)
        return request_generation.json()
