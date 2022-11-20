import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    user_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.String(length=40), unique=True)
    name = sq.Column(sq.String(length=40))
    lastname = sq.Column(sq.String(length=40))
    date_of_birth = sq.Column(sq.DateTime)
    search_sex = sq.Column(sq.String(length=10))
    search_city = sq.Column(sq.String(length=40))
    search_age_min = sq.Column(sq.Integer)
    search_age_max = sq.Column(sq.Integer)


class Favorite(Base):
    __tablename__ = "favorites"

    favorite_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.String(length=40), unique=True, nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("user.user_id"), nullable=False)
    User = relationship(User, backref="favorites")


class Blocked(Base):
    __tablename__ = "blocked"

    blocked_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.String(length=40), unique=True, nullable=False)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("user.user_id"), nullable=False)
    User = relationship(User, backref="blocking")


class Photo(Base):
    __tablename__ = "photo"

    photo_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.String(length=40), unique=True, nullable=False)
    link = sq.Column(sq.String(length=40), nullable=False)
    quantity_like = sq.Column(sq.Integer)


class Founduser(Base):
    __tablename__ = "founduser"

    found_user_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.String(length=40), unique=True)
    name = sq.Column(sq.String(length=40))
    lasrname = sq.Column(sq.String(length=40))
    user_id = sq.Column(sq.Integer, sq.ForeignKey("user.user_id"), nullable=False)
    photo_id = sq.Column(sq.Integer, sq.ForeignKey("photo.photo_id"), nullable=False)
    User = relationship(User, backref="foundusers")
    Photo = relationship(User, backref="foundusers")


def create_tables(engine):
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
