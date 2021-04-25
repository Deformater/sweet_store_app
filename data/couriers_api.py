import flask
from flask import request, make_response
from . import db_session
from .couriers import Couriers
from .orders import Orders
from .tools import time_check, post_orders_validation, post_couriers_validation, complete_orders_validation
import datetime
import json


blueprint = flask.Blueprint(
    'couriers_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/couriers', methods=['POST'])
def post_couriers():
    # Объявление списков
    id_error_list = []
    id_list = []
    couriers_list = []

    db_sess = db_session.create_session()   # Создание ссесии с БД

    for curier in request.json['data']:
        try:
            post_couriers_validation(curier, db_sess)   # Валидация входный данных

            # Создание объекта курьера с указанными параметрами
            couriers = Couriers(
                courier_id=curier['courier_id'],
                courier_type=curier['courier_type'],
                regions=curier['regions'],
                working_hours=curier['working_hours'],
                orders_ids=[],
                delivery_count=0
            )

            id_list.append({'id': curier['courier_id']})    # Добавление словаря в список для успешного ответа
            couriers_list.append(couriers)  # Добавление курьера в список для БД
        except (ValueError, TypeError, KeyError):
            id_error_list.append({'id': curier['courier_id']})  # Добавление словаря в список неудачного ответа

    try:
        # Проверка на наличие не прошедших валидацию курьеров
        if id_error_list:
            raise ValueError

        db_sess.add_all(couriers_list)  # Добавление курьеров в БД
        db_sess.commit()    # Сохранение изменений

        # Успешный ответ
        return make_response('HTTP 201 Created\n' + json.dumps(
                                        {
                                            "couriers": id_list
                                        }), 200)
    except ValueError:
        # Неудачный ответ
        return make_response('HTTP 400 Bad Request\n' + json.dumps(
                                                {
                                                    "validation_error":
                                                    {
                                                        "couriers": id_error_list
                                                    }
                                                }), 400)


@blueprint.route('/couriers/<int:courier_id>', methods=['PATCH'])
def patch_courier(courier_id):
    db_sess = db_session.create_session()   # Создание ссесии с БД

    try:
        couriers = db_sess.query(Couriers).get(courier_id)  # Получение курьера из БД

        # Проверка наличия курьера с заданным id
        if couriers is None:
            raise TypeError

        # Изменение параметров курьера и валидация параметров
        for key in request.json.keys():
            couriers[key] = request.json[key]

        # Снимаем заказы, неподходящие после изменений
        for order in couriers.orders:
            if couriers.weight() < order.weight or not time_check(order.delivery_hours, couriers.working_hours):
                order.is_available = True
                order.courier_id = None
                order_ids = couriers.orders_ids[:]
                order_ids.remove(order.order_id)
                couriers.orders_ids = order_ids

        db_sess.commit()    # Сохранение изменений

        # Успешный ответ
        return make_response('HTTP 200 OK\n' + json.dumps({
                                                             "courier_id": couriers.courier_id,
                                                             "courier_type": couriers.courier_type,
                                                             "regions": couriers.regions,
                                                             "working_hours": couriers.working_hours
                                                            }), 200)
    except (KeyError, TypeError):

        return make_response('HTTP 400 Bad Request', 400)   # Не успешный ответ


@blueprint.route('/orders', methods=['POST'])
def post_orders():
    # Объявление списков
    id_error_list = []
    id_list = []
    orders_list = []

    db_sess = db_session.create_session()   # Создание ссесии с БД

    for order in request.json['data']:
        try:
            post_orders_validation(order, db_sess)  # Валидация входных данных

            # Создание объекта заказа с указанными параметрами
            orders = Orders(
                order_id=order['order_id'],
                weight=order['weight'],
                region=order['region'],
                delivery_hours=order['delivery_hours'],
                is_available=True,
            )

            id_list.append({'id': order['order_id']})   # Добавление словаря в список для успешного ответа
            orders_list.append(orders)  # Добавление курьера в список для БД
        except (ValueError, TypeError, KeyError):
            id_error_list.append({'id': order['order_id']})  # Добавление словаря в список неудачного ответа

    try:
        # Проверка на наличие не прошедших валидацию заказов
        if id_error_list:
            raise ValueError

        db_sess.add_all(orders_list)    # Добавление заказов в БД
        db_sess.commit()    # Сохранение изменений

        # Успешный ответ
        return make_response('HTTP 201 Created\n' + json.dumps({
                                        "couriers": id_list
                                      }), 200)
    except ValueError:
        # Неудачный ответ
        return make_response('HTTP 400 Bad Request\n' + json.dumps({
                                      "validation_error": {
                                            "couriers": id_error_list
                                      }}), 400)


@blueprint.route('/orders/assign', methods=['POST'])
def assign_orders():
    try:
        # Объявление списков и переменных
        order_list = []
        success_order_list = []
        assign_time = datetime.datetime.now().isoformat()[:-4] + 'Z'

        db_sess = db_session.create_session()   # Создание ссесии с БД

        courier_id = request.json['courier_id']

        # Валидация id курьера
        if courier_id.__class__.__name__ != 'int':
            raise ValueError

        courier = db_sess.query(Couriers).get(courier_id)

        # Проверка наличия курьера с заданным id
        if courier is None:
            raise TypeError

        # Проверка наличия активных заказов курьера
        if not courier.orders_ids:
            # Начисление заказов подходящих курьеру
            for order in db_sess.query(Orders).filter(Orders.region.in_(courier.regions),
                                                      Orders.weight <= courier.weight(), Orders.is_available):
                if time_check(order.delivery_hours, courier.working_hours):
                    # Изменение данных для начисления
                    order.is_available = False
                    order.courier_id = courier.courier_id
                    order.assign_time = assign_time
                    order_list.append(order.order_id)
                    success_order_list.append({'id': order.order_id})

            courier.orders_ids = courier.orders_ids + order_list

        db_sess.commit()    # Сохранение изменений
        if order_list:  # Проверка на наличие добавленных курьеру заказов
            # Успешный ответ с наличием добавленных заказов
            return make_response('HTTP 200 OK\n' + json.dumps({
                                          "orders": success_order_list,
                                          "assign_time": assign_time
                                         }), 200)
        else:
            # Успешный ответ без добавленных курьеру заказов
            return make_response('HTTP 200 OK\n' + json.dumps({
                                          "orders": success_order_list,
                                         }), 200)
    except (TypeError, KeyError, ValueError):

        return make_response('HTTP 400 Bad Request', 400)   # Неудачный ответ


@blueprint.route('/orders/complete', methods=['POST'])
def complete_orders():
    try:
        complete_time = request.json['complete_time']   # Получение время окончания заказа

        db_sess = db_session.create_session()   # Создание ссесии с БД

        order = db_sess.query(Orders).get(request.json['order_id'])  # Получение заказа из БД

        complete_orders_validation(request, order, complete_time)  # Валидация переданных данных

        courier = db_sess.query(Couriers).get(order.courier_id)  # Получение курьера из БД

        # Снятие заказа с курьера
        order.complete_time = complete_time
        order_ids = courier.orders_ids[:]
        order_ids.remove(order.order_id)
        courier.orders_ids = order_ids
        order.complete_by_id = order.courier_id
        order.courier_id = None

        # Проверка заверщения развоза
        if not courier.orders_ids:
            courier.delivery_count += 1

        db_sess.commit()    # Сохранение изменений

        # Успешный ответ
        return make_response('HTTP 200 OK\n' + json.dumps({
                                      "order_id": order.order_id
                                    }), 200)
    except (ValueError, TypeError, KeyError):

        return make_response('HTTP 400 Bad Request', 400)   # Неудачный ответ


@blueprint.route('/couriers/<int:courier_id>', methods=['GET'])
def get_couriers(courier_id):
    try:
        time_by_regions = []

        db_sess = db_session.create_session()   # Создание ссесии с БД

        courier = db_sess.query(Couriers).get(courier_id)   # Получение курьера из БД

        # Проверка наличия курьера с заданным id
        if courier is None:
            raise ValueError

        # Нахождение минимального среднего времени доставки по районам
        for region in courier.regions:
            delivery_time_list = []

            # Получение списка выполненых заказов в данном районе
            orders_list = list(db_sess.query(Orders).filter(Orders.region == region,
                                                            Orders.complete_by == courier))
            # Проверка наличия таких заказов
            if orders_list:
                sum1 = datetime.timedelta()

                # Вычисление времени доставки для 1 заказа из данного района
                delivery_time_list.append(datetime.datetime.strptime(orders_list[0].complete_time,
                                                                     '%Y-%m-%dT%H:%M:%S.%fZ') -
                                          datetime.datetime.strptime(orders_list[0].assign_time,
                                                                     '%Y-%m-%dT%H:%M:%S.%fZ'))

                # Вычисление времени доставки остальных заказов
                for i, order in enumerate(orders_list[1:]):
                    delivery_time_list.append(datetime.datetime.strptime(order.complete_time,
                                                                         '%Y-%m-%dT%H:%M:%S.%fZ') -
                                              datetime.datetime.strptime(orders_list[i].complete_time,
                                                                         '%Y-%m-%dT%H:%M:%S.%fZ'))
                # Нахождение общего времени доставки по району
                for delivery_time in delivery_time_list:
                    sum1 += delivery_time

                # Добавление среднего времени доставки 1 заказа с данного района
                time_by_regions.append(sum1.total_seconds() / len(delivery_time_list))

        # Проверка на наличие выполненых курьером заказов
        if courier.delivery_count and time_by_regions:

            t = min(time_by_regions)    # Минимальное среднее время доставки по районам
            rating = (60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5    # Рейтинг курьера
            earnings = 500 * courier.earning_coefficient() * courier.delivery_count  # Заработок курьера

            # Успешный ответ с хотя бы 1 выполненым развозом
            return make_response('HTTP 200 OK\n' + json.dumps({
                                              "courier_id": courier.courier_id,
                                              "courier_type": courier.courier_type,
                                              "regions": courier.regions,
                                              "working_hours": courier.working_hours,
                                              "rating": round(rating, 2),
                                              "earnings": earnings
                                            }), 200)
        else:
            # Успешный ответ без выполненых развозов
            return make_response('HTTP 200 OK\n' + json.dumps({
                "courier_id": courier.courier_id,
                "courier_type": courier.courier_type,
                "regions": courier.regions,
                "working_hours": courier.working_hours,
            }), 200)
    except ValueError:

        return make_response('HTTP 400 Bad Request', 400)   # Неудачный ответ


@blueprint.route('/orders/<int:order_id>', methods=['GET'])
def get_orders(order_id):
    try:
        db_sess = db_session.create_session()  # Создание ссесии с БД

        order = db_sess.query(Orders).get(order_id)  # Получение заказа из БД

        # Проверка наличия заказа с заданным id
        if order is None:
            raise ValueError

        # Проверка занаятости заказа
        if order.is_available:
            # Ответ для свободного заказа
            return make_response('HTTP 200 OK\n' + json.dumps({
                "order_id": order.order_id,
                "weight": order.weight,
                "region": order.region,
                "delivery_hours": order.delivery_hours,
                "is_available": order.is_available
            }))

        else:
            # Проверка выполненности заказа
            if order.courier:
                # Ответ для заказа назначенного на курьера
                return make_response('HTTP 200 OK\n' + json.dumps({
                    "order_id": order.order_id,
                    "weight": order.weight,
                    "region": order.region,
                    "delivery_hours": order.delivery_hours,
                    "is_available": order.is_available,
                    "assign_time": order.assign_time,
                    "courier_id": order.courier_id
                }))

            else:
                # Ответ для заказа выполненного курьером
                return make_response('HTTP 200 OK\n' + json.dumps({
                    "order_id": order.order_id,
                    "weight": order.weight,
                    "region": order.region,
                    "delivery_hours": order.delivery_hours,
                    "is_available": order.is_available,
                    "assign_time": order.assign_time,
                    "complete_time": order.complete_time,
                    "complete_by_id": order.complete_by_id
                }))

    except ValueError:

        return make_response('HTTP 400 Bad Request', 400)   # Неудачный ответ