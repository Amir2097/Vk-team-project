import os
import configparser
from vkinder_bot.bot import run_bot

config = configparser.ConfigParser()
configpath = "config_bot.cfg"


def startup():
    """Функция запуска и первоначальной настройки программы"""
    if os.path.exists(configpath):
        run_bot()
        return "[INFO]  Bot launched"
    else:
        config.add_section("TOKEN")
        add_token = input("[SET]Введите токен - ")
        config.set("TOKEN", "vk_token", add_token)

        with open(configpath, "w") as config_file:
            config.write(config_file)

        # TODO Далее здесь прописать настройку и создание базы данных и другие необходимые настройки

        run_bot()
        return "[INFO]  Bot set up and running"


if __name__ == '__main__':
    startup()
