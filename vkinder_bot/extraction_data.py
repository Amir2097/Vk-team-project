import configparser
import requests

config = configparser.ConfigParser()
config.read("config_bot.cfg")


class ExtractingUserData:
    def __init__(self, user_id):
        self.paramitres = None
        self.token = config["TOKEN"]["vk_token"]
        self.user_id = user_id

    def primary_user_data(self):
        """
        ____________________primary_user_data_____________________
        Метод получения первичной информации о пользователе.
        Данные выводятся в json формате. Подробнее про результат
        вывода можно прочитать https://dev.vk.com/method/users.get
        """

        self.paramitres = {'access_token': self.token, 'user_id': self.user_id, 'v': 5.131}
        request_generation = requests.get(url=f'https://api.vk.com/method/users.get', params=self.paramitres)
        return request_generation.json()

    print(primary_user_data.__doc__)

