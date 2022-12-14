import os
import vk_api
import pwinput
import psycopg2
import configparser

config = configparser.ConfigParser()
configpath = "vkinder_bot/config_bot.cfg"


def cprint_upred(text):
    """
    Функция вывода текста красного цвета
    """
    return "\033[1m\033[31m{}\033[0m".format(text)


def cprint_redtext(text):
    """
    Функция вывода в консоль текста красного цвета
    """
    print("\033[1m\033[31m{}\033[0m".format(text))


def cprint_yellow(text):
    """
    Функция вывода текста желтого цвета
    """
    return "\033[33m{}\033[0m".format(text)


def cprint_blue(text):
    """
    Функция вывода текста синего цвета
    """
    return "\033[34m{}\033[0m".format(text)


def cprint_text(text):
    """
    Функция вывода в консоль текста синего цвета
    """
    print("\033[34m{}\033[0m".format(text))


def startup():
    """
    Функция запуска и первоначальной настройки программы
    """
    global vk_session

    if os.path.exists(configpath):
        cprint_redtext("Бот запущен!")
        from vkinder_bot.bot import run_bot
        run_bot()
    else:
        try:
            cprint_redtext("ПЕРВОНАЧАЛЬНАЯ НАСТРОЙКА ПРОГРАММЫ")
            cprint_redtext("+" * 34)
            cprint_text(
                """[!] Программа запущена впервый раз! 
[!] Необходимо произвести первоначальную настройку!
[!] Данное действие необходимо произвести только один раз, последующие включения будут проходить в 
    штатном режиме
    
[!] Для прекращения процесса первичной настройки, нажмите [CTRL] + [C]""")
            cprint_redtext("+" * 34)
            cprint_redtext("Настройка взаимодействия с ВКонтакте \n")
            config.add_section("TOKEN")
            add_token = pwinput.pwinput(prompt='[SET]Введите токен сообщества в котором будет работать БОТ- ', mask='*')
            config.set("TOKEN", "vk_token", add_token)
            cprint_text("Авторизация на сайта Вконтакте для работы с api_vk")
            add_user = input("[SET]Введите имя пользователя Вконтакте - ")
            add_pass = pwinput.pwinput(prompt='[SET]Введите пароль Вконтакте - ', mask='*')

            try:
                vk_session = vk_api.VkApi(token=config["TOKEN"]["vk_user_token"])
            except KeyError:
                username = add_user
                password = add_pass
                scope = 'users,notify,friends,photos,offline,wall'
                vk_session = vk_api.VkApi(username, password, scope=scope, api_version='5.124')
            except TypeError:
                cprint_redtext("ВВЕДЕН НЕКОРРЕКТНЫЙ ТОКЕН!!!")
            try:
                vk_session.auth(token_only=True)
            except vk_api.AuthError as error_msg:
                print(error_msg)
            set_token_vk = vk_session.token['access_token']
            config.set("TOKEN", "vk_user_token", set_token_vk)

            if os.path.isfile('vk_config.v2.json'):
                os.remove('vk_config.v2.json')
                cprint_redtext("[INFO] Временный файл удален!")
            else:
                cprint_redtext("[INFO] Временный файл не найден!")

            cprint_redtext("Настройка взаимодействия с базой данных")
            config.add_section("DATABASE")
            user_data = input("[SET] Введите имя пользователя базы данных- ")
            config.set("DATABASE", "db_user", user_data)
            password_data = pwinput.pwinput(prompt='[SET] Введите пароль пользователя базы данных- ', mask='*')
            config.set("DATABASE", "db_password", password_data)
            host_data = input("[SET] Введите хост базы данных- ")
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
                cprint_text("[INFO] Начало установки модулей!")
                os.system("pip install -r requirements.txt")
                cprint_text("[FINISH] Настройка завершена! Перезапустите БОТ.")

            except psycopg2.OperationalError:
                cprint_redtext("[ERROR] БАЗА ДАННЫХ НЕДОСТУПНА!!!!")
                raise ValueError('oops!')

        except KeyboardInterrupt:
            cprint_upred("Выполнение настройки завершено по команде пользователя!")

        except ValueError:
            pass


if __name__ == '__main__':
    startup()
