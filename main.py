import os
import configparser

config = configparser.ConfigParser()
configpath = "vkinder_bot/config_bot.cfg"


def startup():
    """Функция запуска и первоначальной настройки программы"""
    if os.path.exists(configpath):
        from vkinder_bot.bot import run_bot
        run_bot()
    else:
        try:
            config.add_section("TOKEN")
            add_token = input("[SET]Введите токен сообщества - ")
            config.set("TOKEN", "vk_token", add_token)
            add_user = input("[SET]Введите имя пользователя VK.COM - ")
            config.set("TOKEN", "vk_user", add_user)
            add_pass = input("[SET]Введите пароль VK.COM - ")
            config.set("TOKEN", "vk_pass", add_pass)

            config.add_section("DATABASE")
            user_data = input("[SET] Введите имя пользователя базы данных - ")
            config.set("DATABASE", "db_user", user_data)
            password_data = input("[SET] Введите пароль пользователя базы данных - ")
            config.set("DATABASE", "db_password", password_data)
            host_data = input("[SET] Введите хост базы данных - ")
            config.set("DATABASE", "db_host", host_data)

            with open(configpath, "w") as config_file:
                config.write(config_file)

        except KeyboardInterrupt:
            os.system("clear")
            print("Выполнение настройки завершено по команде пользователя!")

        except ValueError:
            os.system("clear")
            print("Ошибка записи в файл!!! Настройка прервана!")


if __name__ == '__main__':
    startup()
