import os
import configparser
import psycopg2

config = configparser.ConfigParser()
configpath = "vkinder_bot/config_bot.cfg"


def cprint_upred(text):
    return "\033[1m\033[31m{}\033[0m".format(text)


def cprint_redtext(text):
    print("\033[1m\033[31m{}\033[0m".format(text))


def cprint_yellow(text):
    return "\033[33m{}\033[0m".format(text)


def cprint_blue(text):
    return "\033[34m{}\033[0m".format(text)


def cprint_text(text):
    print("\033[34m{}\033[0m".format(text))


def startup():
    """Функция запуска и первоначальной настройки программы"""
    if os.path.exists(configpath):
        from vkinder_bot.bot import run_bot
        run_bot()
    else:
        try:
            cprint_redtext("ПЕРВОНАЧАЛЬНАЯ НАСТРОЙКА ПРОГРАММЫ")
            cprint_text(
                """
[!] Программа запущена впервый раз! 
[!] Необходимо произвести первоначальную настройку!
[!] Данное действие необходимо произвести только один раз, последующие включения будут проходить в 
    штатном режиме
    
[!] Для прекращения процесса первичной настройки, нажмите [CTRL] + [C]
            """)
            cprint_redtext("Настройка взаимодействия с ВКонтакте")
            config.add_section("TOKEN")
            add_token = input("[SET]Введите токен сообщества в котором будет работать БОТ - ")
            config.set("TOKEN", "vk_token", add_token)
            add_user = input("[SET]Введите имя пользователя VK.COM (от его имени будут работать некоторые запросы)- ")
            config.set("TOKEN", "vk_user", add_user)
            add_pass = input("[SET]Введите пароль VK.COM - ")
            config.set("TOKEN", "vk_pass", add_pass)

            cprint_redtext("Настройка взаимодействия с базой данных")
            config.add_section("DATABASE")
            user_data = input("[SET] Введите имя пользователя базы данных - ")
            config.set("DATABASE", "db_user", user_data)
            password_data = input("[SET] Введите пароль пользователя базы данных - ")
            config.set("DATABASE", "db_password", password_data)
            host_data = input("[SET] Введите хост базы данных - ")
            config.set("DATABASE", "db_host", host_data)

            try:
                conn = psycopg2.connect(
                    dbname="vkinder",
                    user=user_data,
                    host=host_data,
                    password=password_data,
                    port="5432",
                    connect_timeout=1)
                conn.close()

                with open(configpath, "w") as config_file:
                    config.write(config_file)

                cprint_text("[INFO] Соединение с базой настроено! Конфигурация записана!")
                os.system("pip install -r requirements.txt")

            except psycopg2.OperationalError:
                cprint_redtext("[ERROR] БАЗА ДАННЫХ НЕДОСТУПНА!!!!")
                raise ValueError('oops!')

        except KeyboardInterrupt:
            cprint_upred("Выполнение настройки завершено по команде пользователя!")

        except ValueError:
            pass


if __name__ == '__main__':
    startup()
