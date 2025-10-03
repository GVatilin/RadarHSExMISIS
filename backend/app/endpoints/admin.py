from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from app.database import DeclarativeBase
from app.database.connection import get_sync_session


flask_app = Flask(__name__)
flask_app.secret_key = 'secret'

admin = Admin(flask_app, name='Admin panel')
table_models = [mapper.class_ for mapper in DeclarativeBase.registry.mappers]
admin.add_views(*(ModelView(m, next(get_sync_session())) for m in table_models))