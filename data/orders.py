import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


# Класс заказа
class Orders(SqlAlchemyBase, SerializerMixin):
    # Название таблицы
    __tablename__ = 'orders'

    # id заказа
    order_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 primary_key=True, nullable=True, unique=True)
    weight = sqlalchemy.Column(sqlalchemy.Float, nullable=True)  # Вес заказа
    region = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)   # Регион доставки заказа
    delivery_hours = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)  # Время доставки
    is_available = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)  # Доступен ли заказ для выдачи курьера
    assign_time = sqlalchemy.Column(sqlalchemy.String, nullable=True)   # Время выдачи заказа
    complete_time = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # Время выполнения заказа
    # id курьера, которому выдали данный заказом
    courier_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("couriers.courier_id"), nullable=True)
    courier = orm.relation('Couriers', foreign_keys=[courier_id])   # Курьер, которому выдали данный заказом
    # id курьера, который выполнил данный заказ
    complete_by_id = sqlalchemy.Column(sqlalchemy.Integer,
                                       sqlalchemy.ForeignKey("couriers.courier_id"), nullable=True)
    complete_by = orm.relation('Couriers', foreign_keys=[complete_by_id])   # Курьер, который выполнил данный заказ
