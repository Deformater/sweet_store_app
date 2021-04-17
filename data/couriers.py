import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


# Класс курьера
class Couriers(SqlAlchemyBase, SerializerMixin):
    # Название таблицы
    __tablename__ = 'couriers'

    # id курьера
    courier_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   primary_key=True, nullable=True, unique=True)
    courier_type = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # Тип курьера
    regions = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)  # Регионы доставки
    working_hours = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)   # Часы работы
    orders_ids = sqlalchemy.Column(sqlalchemy.JSON, nullable=True)  # id активных заказов
    # Список активных заказов
    orders = orm.relation("Orders", back_populates='courier', foreign_keys='Orders.courier_id')
    # Список выполненых заказов
    complete_orders = orm.relation("Orders", back_populates='complete_by',
                                   foreign_keys='Orders.complete_by_id')
    delivery_count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)   # Кол-во выполненных развозов

    # Возможность изменять параметры курьера при помощи вызова ключей
    def __setitem__(self, key, v):
        if key == 'courier_type' and v in ('foot', 'bike', 'car'):
            self.courier_type = v
        elif key == 'regions' and v.__class__.__name__ == 'list' and v:
            self.regions = v
        elif key == 'working_hours' and v.__class__.__name__ == 'list' and v:
            self.working_hours = v
        else:
            raise KeyError

    # Функция возращающая грузоподъёмность курьера
    def weight(self):
        if self.courier_type == 'foot':
            courier_weight = 10
        elif self.courier_type == 'bike':
            courier_weight = 15
        else:
            courier_weight = 50
        return courier_weight

    # Функция возращающая коэффициент заработка курьера
    def earning_coefficient(self):
        if self.courier_type == 'foot':
            coefficient = 2
        elif self.courier_type == 'bike':
            coefficient = 5
        else:
            coefficient = 9
        return coefficient
