import sqlalchemy
from sqlalchemy.orm import sessionmaker

from models import create_tables, User, Favorite, Blocked, Founduser, Photo

DSN = "postgresql://netology:5512@admlab.ddns.net:5432/vkinder"
engine = sqlalchemy.create_engine(DSN)
create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()
