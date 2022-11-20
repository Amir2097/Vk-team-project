import sqlalchemy
from sqlalchemy.orm import sessionmaker
import configparser
from models import create_tables, User, Favorite, Blocked, Founduser, Photo

config = configparser.ConfigParser()
config.read('config_bot.cfg')
db_user = config.get('DATABASE', 'db_user')
db_password = config.get('DATABASE', 'db_password')
db_host = config.get('DATABASE', 'db_host')

DSN = "postgresql://%s:%s@%s:5432/vkinder" % (db_user, db_password, db_host)
engine = sqlalchemy.create_engine(DSN)
create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()
