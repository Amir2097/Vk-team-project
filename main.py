import os
import configparser
from vkinder_bot.bot import run_bot
from vkinder_bot.extraction_data import ExtractingUserData

config = configparser.ConfigParser()
configpath = "config_bot.cfg"


def startup():
    """Функция запуска и первоначальной настройки программы"""
    if os.path.exists(configpath):
        run_bot()
        return "[INFO]  Bot launched"
    else:
        config.add_section("TOKEN")
        add_token = input("[SET]Введите токен сообщества - ")
        config.set("TOKEN", "vk_token", add_token)
        add_user_token = input("[SET]Введите токен служебной страницы (https://vkhost.github.io/) - ")
        config.set("TOKEN", "vk_user_token", add_user_token)

        with open(configpath, "w") as config_file:
            config.write(config_file)

        # TODO Далее здесь прописать настройку и создание базы данных и другие необходимые настройки

        run_bot()
        return "[INFO]  Bot set up and running"


if __name__ == '__main__':
    # startup()
    ext = ExtractingUserData(100, 18, 29, 1, 1, 100)
    print(ext.user_search())
