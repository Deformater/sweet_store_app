import sqlalchemy
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


# Класс пользователя
class User(SqlAlchemyBase):
    # Название таблицы
    __tablename__ = 'users'

    # id юзера
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # Имя пользователя
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # Информация о пользователе
    # email пользователей
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)   # Захешированный пароль
    couriers_added = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)   # Кол-во добаленных курьеров
    orders_added = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)  # Кол-во добавленных заказов

    # Хешированние пароля
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    # Проверка пароля
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)