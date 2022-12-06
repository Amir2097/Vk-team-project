import configparser
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from vkinder_bot.extraction_data import ExtractingUserData

Base = declarative_base()


class Mainuser(Base):
    """
    Основная таблица. Добавление пользователя, который обратился в чат,
    для поиска людей
    """
    __tablename__ = "mainuser"

    user_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.String(length=40), unique=True)
    name = sq.Column(sq.String(length=40))
    lastname = sq.Column(sq.String(length=40))
    date_of_birth = sq.Column(sq.DateTime)
    token = sq.Column(sq.String(length=200), unique=True)

    def __str__(self):
        return f'{self.user_id}: {self.vk_id}, {self.name}, {self.lastname}, {self.date_of_birth}, {self.token}'


class Favorite(Base):
    """
    Таблица избранных профилей
    """

    __tablename__ = "favorite"

    favorite_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.String(length=40), nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("mainuser.user_id"), nullable=False)
    Mainuser = relationship(Mainuser, backref="favorites")


class Blocked(Base):
    """
    Таблица профилей добавленных в ЧС
    """
    __tablename__ = "blocked"

    blocked_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.String(length=40), unique=True, nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("mainuser.user_id"), nullable=False)
    Mainuser = relationship(Mainuser, backref="blocking")


class Founduser(Base):
    """
    Таблица найденных вариантов людей по критериям
    """
    __tablename__ = "founduser"

    found_user_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.String(length=40), unique=True)
    name = sq.Column(sq.String(length=40))
    lastname = sq.Column(sq.String(length=40))
    user_id = sq.Column(sq.Integer, sq.ForeignKey("mainuser.user_id"), nullable=False)
    Mainuser = relationship(Mainuser, backref="foundusers")


class Photo(Base):
    """
    Таблица для сохранения информации о фото,
    привязаны к Founduser
    """
    __tablename__ = "photo"

    photo_id = sq.Column(sq.Integer, primary_key=True)
    link = sq.Column(sq.String(length=500), nullable=False)
    quantity_like = sq.Column(sq.Integer)
    media_id = sq.Column(sq.Integer)
    found_user_id = sq.Column(sq.Integer, sq.ForeignKey("founduser.found_user_id"), nullable=False)
    Founduser = relationship(Founduser, backref="foundusers")


def create_tables(engine):
    """
    Создание таблиц в БД
    """
    Base.metadata.create_all(engine)


def remove_tables(engine):
    """
    Удаление таблиц из БД
    """
    Base.metadata.drop_all(engine)


class Connect:
    """
    Подключение к бд и создание сессии
    """
    config = configparser.ConfigParser()
    config.read("vkinder_bot/config_bot.cfg")
    token_communities = config["TOKEN"]["vk_token"]
    db_user = config["DATABASE"]["db_user"]
    db_password = config["DATABASE"]["db_password"]
    db_host = config["DATABASE"]["db_host"]

    DSN = "postgresql://%s:%s@%s:5432/vkinder" % (db_user, db_password, db_host)
    engine = sq.create_engine(DSN)
    # remove_tables(engine)
    create_tables(engine)

    session_mar = sessionmaker(bind=engine)
    session = session_mar()

    def __init__(self):
        self.user_ids = None
        self.vk_ids = None

    def user_database_entry(self, data):
        """
        Метод принимает json из функции profile_info и добавляет информацию в бд о пользователе,
        зарегестрировавшемся в боте
        """
        new_post = Mainuser(vk_id=data.get('id'), name=data.get('first_name'), lastname=data.get('last_name'),
                            date_of_birth=data.get('ddate'))
        self.session.add(new_post)
        self.session.commit()

    def founduser_database_entry(self, data, mainuser_vk):
        """
        Метод принимает json из функции user_search и photo_extraction.
        Добавляет информацию в бд о пользователеях, найденных в поиске, а так же их фотографии
        """
        main_vk_id = str(ExtractingUserData().profile_info(mainuser_vk)['id'])
        subq = Connect.session.query(Mainuser).filter(Mainuser.vk_id == main_vk_id).first()
        for record in data:
            if record['is_closed'] == 0:
                new_post = Founduser(vk_id=record.get('id'), name=record.get('first_name'),
                                     lastname=record.get('last_name'), user_id=subq.user_id)
                self.session.add(new_post)
                self.session.commit()
                subq_photo = Connect.session.query(Founduser).filter(Founduser.vk_id == str(record.get('id'))).first()
                for found_iter in ExtractingUserData().photo_extraction(str(record.get('id'))):
                    new_post_photo = Photo(link=found_iter[0], quantity_like=found_iter[1][0],
                                           media_id=found_iter[1][1], found_user_id=subq_photo.found_user_id)
                    self.session.add(new_post_photo)
                    self.session.commit()

    def favorites(self, vk_ids, user_ids):
        """
        Метод добавляет запись в таблицу избранных пользователей. Принимает на вход:
        vk_id - идентификатор пользователя которого добавляем в избранное
        user_id - идентификатор пользователя который ведет диалг с ботом
        """
        self.vk_ids = vk_ids
        self.user_ids = user_ids
        sending_data = Favorite(vk_id=self.vk_ids, user_id=self.user_ids)
        self.session.add(sending_data)
        self.session.commit()

    def blocked(self, vk_ids, user_ids):
        """
        Метод добавляет запись в таблицу заблокированных пользователей. Принимает на вход:
        vk_id - идентификатор пользователя которого добавляем в избранное
        user_id - идентификатор пользователя который ведет диалг с ботом
        """
        self.vk_ids = vk_ids
        self.user_ids = user_ids
        sending_data = Blocked(vk_id=self.vk_ids, user_id=self.user_ids)
        self.session.add(sending_data)
        self.session.commit()

    def delete_found_users(self, main_user_id):
        """
        Удаление данных с таблицы FoundUsers данных пользователей (в том числе фото)
        по main_user_id - id пользователя обратившегося в чат,
        испоьзуется для изменения критериев
        """
        subq_main = Connect.session.query(Mainuser).filter(Mainuser.vk_id == main_user_id).first()
        subq_people = Connect.session.query(Founduser).filter(Founduser.user_id == subq_main.user_id).all()
        for subq_peoples in subq_people:
            subq_photo_foundusers = Connect.session.query(Photo).filter(
                Photo.found_user_id == subq_peoples.found_user_id).all()
            for subq_photo_found in subq_photo_foundusers:
                self.session.delete(subq_photo_found)
                self.session.commit()
            self.session.delete(subq_peoples)
            self.session.commit()
