import configparser
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from vkinder_bot.extraction_data import ExtractingUserData

Base = declarative_base()


class Mainuser(Base):
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
    __tablename__ = "favorite"

    favorite_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.String(length=40), nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("mainuser.user_id"), nullable=False)
    Mainuser = relationship(Mainuser, backref="favorites")


class Blocked(Base):
    __tablename__ = "blocked"

    blocked_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.String(length=40), unique=True, nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("mainuser.user_id"), nullable=False)
    Mainuser = relationship(Mainuser, backref="blocking")


class Founduser(Base):
    __tablename__ = "founduser"

    found_user_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.String(length=40), unique=True)
    name = sq.Column(sq.String(length=40))
    lastname = sq.Column(sq.String(length=40))
    user_id = sq.Column(sq.Integer, sq.ForeignKey("mainuser.user_id"), nullable=False)
    Mainuser = relationship(Mainuser, backref="foundusers")


class Photo(Base):
    __tablename__ = "photo"

    photo_id = sq.Column(sq.Integer, primary_key=True)
    link = sq.Column(sq.String(length=200), nullable=False)
    quantity_like = sq.Column(sq.Integer)
    found_user_id = sq.Column(sq.Integer, sq.ForeignKey("founduser.found_user_id"), nullable=False)
    Founduser = relationship(Founduser, backref="foundusers")


def create_tables(engine):
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


class Connect:
    """Подключение к бд и создание сессии"""

    config = configparser.ConfigParser()
    config.read("../config_bot.cfg")
    db_user = config.get('DATABASE', 'db_user')
    db_password = config.get('DATABASE', 'db_password')
    db_host = config.get('DATABASE', 'db_host')

    DSN = "postgresql://%s:%s@%s:5432/vkinder" % (db_user, db_password, db_host)
    engine = sq.create_engine(DSN)
    create_tables(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    def user_database_entry(self, data):
        """Метод принимает json из функции profile_info и добавляет информацию в бд о пользователе,
        зарегестрировавшемся в боте"""

        new_post = Mainuser(vk_id=data.get('id'), name=data.get('first_name'), lastname=data.get('last_name'),
                            date_of_birth=data.get('ddate'))
        self.session.add(new_post)
        self.session.commit()

    def founduser_database_entry(self, data):
        """Метод принимает json из функции user_search и photo_extraction. Добавляет информацию в бд о пользователеях,
                найденных в поиске, а так же их фотографии"""
        main_vk_id = str(ExtractingUserData().profile_info()['id'])                                                     # получение vk_id пользователя использующего бота
        subq = Connect.session.query(Mainuser).filter(Mainuser.vk_id == main_vk_id).first()                             # находим запись в таблице mainuser пользователя использующего бот
        for record in data:                                                                                             # заполняем данные по user_id
            if record['is_closed'] == 0:                                                                                # проверяем чтобы профиль был открыт
                new_post = Founduser(vk_id=record.get('id'), name=record.get('first_name'),                             # заполняем таблицу founduser
                                     lastname=record.get('last_name'), user_id=subq.user_id)
                self.session.add(new_post)
                self.session.commit()
                subq_photo = Connect.session.query(Founduser).filter(Founduser.vk_id == str(record.get('id'))).first()  # находим запись в таблице founduser которая только-что была заполнена
                for iter in ExtractingUserData().photo_extraction(str(record.get('id'))):
                    new_post_photo = Photo(link=iter, found_user_id=subq_photo.found_user_id)                           # заполняем значения поля табл photo соответствующей записи в founduser, по found_user_id
                    self.session.add(new_post_photo)
                    self.session.commit()