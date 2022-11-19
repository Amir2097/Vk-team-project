""" Модуль поиска и сбора информации о пользователе """

import vk_api
import configparser

config = configparser.ConfigParser()
config.read("config_bot.cfg")


class ExtractingUserData:
    def __init__(self, user_id):
        self.user_id = user_id
        self.vk = vk_api.VkApi(token=config["TOKEN"]["vk_token"])

    def extract_data(self):
        return self.user_id

    def extract_photo(self):
        return self.user_id


if __name__ == '__main__':
    ext = ExtractingUserData("1")
    ext.extract_data()
