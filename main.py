import os
import configparser

import vkinder_bot.bot as vkinder

config = configparser.ConfigParser()
configpath = "config_bot.cfg"


def startup():
    """Функция запуска и первоначальной настройки программы"""
    if os.path.exists(configpath):
        vkinder.run_bot()
        return "[INFO]  Bot launched"
    else:
        config.add_section("TOKEN")
        add_token = input("[SET]Введите токен - ")
        config.set("TOKEN", "vk_token", add_token)

        with open(configpath, "w") as config_file:
            config.write(config_file)

        # TODO Далее здесь прописать настройку и создание базы данных и другие необходимые настройки

        vkinder.run_bot()
        return "[INFO]  Bot set up and running"


if __name__ == '__main__':
    startup()
