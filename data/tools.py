from .orders import Orders
from .couriers import Couriers
from wtforms.validators import ValidationError
import datetime


# Функция проверяющая пересечения времени работы и доставки
def time_check(t1, t2):
    time_check_list = []
    for time1 in t1:
        for time2 in t2:
            bt1 = datetime.datetime.strptime(time1.split('-')[0], '%H:%M')  # Время начала промежутка доставки
            et1 = datetime.datetime.strptime(time1.split('-')[1], '%H:%M')  # Время окончания промежутка доставки

            bt2 = datetime.datetime.strptime(time2.split('-')[0], '%H:%M')  # Время начала промежутка работы курьера
            et2 = datetime.datetime.strptime(time2.split('-')[1], '%H:%M')  # Время конца промежутка работы курьера

            # Проверка пересечения промежутков работы и доставки
            time_check_list.append(((bt2 < bt1 < et2) or (bt2 < et1 < et2)) or ((bt1 <= bt2) and (et1 >= et2)))

    return any(time_check_list)


# Валидация входных данных в запросе post_couriers
def post_couriers_validation(curier, db_sess):
    # Проверка валидности регионов
    if curier['regions'].__class__.__name__ != 'list':
        raise ValueError

    # Проверка валидности часов работы
    if curier['working_hours'].__class__.__name__ != 'list':
        raise ValueError

    # Проверка на пустые значения
    if curier['regions'] == [] or curier['working_hours'] == []:
        raise ValueError

    # Проверка валидности типа курьера
    if curier['courier_type'] not in ('foot', 'bike', 'car'):
        raise ValueError

    # Проверка валидности id курьера
    if curier['courier_id'].__class__.__name__ != 'int':
        raise ValueError

    # Проверка на уникальность id
    if db_sess.query(Couriers).get(curier['courier_id']) is not None:
        raise TypeError


# Валидация входных данных в запросе post_orders
def post_orders_validation(order, db_sess):
    # Проверка на пустое значение
    if not order['delivery_hours']:
        raise ValueError

    # Проверка валидности времени доставки
    if order['delivery_hours'].__class__.__name__ != 'list':
        raise ValueError

    # Валидация id заказа
    if order['order_id'].__class__.__name__ != 'int':
        raise ValueError

    # Проверка уникальности id заказа
    if db_sess.query(Orders).get(order['order_id']) is not None:
        raise TypeError

    # Валидация региона заказа
    if order['region'].__class__.__name__ != 'int':
        raise ValueError

    # Валидация веса заказа
    if (order['weight'].__class__.__name__ != 'float' and order['weight'].__class__.__name__ != 'int') or \
            (order['weight'] < 0.01) or (order['weight'] > 50):
        raise ValueError


# Валидация входных данных в запросе complete_orders
def complete_orders_validation(request, order, complete_time):
    # Валидация id курьера и заказа
    if request.json['order_id'].__class__.__name__ != 'int' \
            or request.json['courier_id'].__class__.__name__ != 'int':
        raise TypeError

    # Проверка наличия заказа с заданным id
    if order is None:
        raise TypeError

    # Проверка введённого id курьера
    if order.courier_id != request.json['courier_id']:
        raise ValueError

    datetime.datetime.strptime(complete_time,
                               '%Y-%m-%dT%H:%M:%S.%fZ')


# Проверка данных формы
def type_is_integer(form, field):
    try:
        int(field.data)
    except ValueError:
        raise ValidationError('Field must be integer')


def region_validation(form, field):
    try:
        r = field.data.split(' ')
        for i in r:
            int(i)
    except ValueError:
        raise ValidationError('Field must be like: 1 2 3')


def working_hours_validation(form, field):
    try:
        time_list = field.data.split(' ')
        for time in time_list:
            datetime.datetime.strptime(time.split('-')[0],
                                       '%H:%M')
            datetime.datetime.strptime(time.split('-')[1],
                                       '%H:%M')
    except ValueError:
        raise ValidationError('Field must be like: HH:MM-HH:MM')


def type_is_float(form, field):
    try:
        float(field.data)
        if not (0.01 <= float(field.data) <= 50):
            raise ValueError
    except ValueError:
        raise ValidationError('Field must be float between 0.01 and 50')